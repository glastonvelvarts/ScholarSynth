export interface RAGCitation {
  id: string;
  paper_id: string;
  paper_title: string;
  text: string;
  page_number: number;
  page_end?: number;
  section?: string | null;
  chunk_type?: string;
  relevance_score: number;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  confident: boolean;
  retrieval_score: number;
  retrieval_message?: string | null;
  citations: RAGCitation[];
}

export interface SearchPaperResult {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  publication_venue?: string;
  year?: number;
  tags: string[];
  relevance_score: number;
  is_open_access: boolean;
  pdf_url?: string;
  url?: string;
  citation_count?: number;
}

export interface JobPaper {
  id: string;
  title: string;
  status: string;
  error?: string | null;
  page_count?: number;
  source: string;
}

export interface ProcessingJobResponse {
  id: string;
  job_id?: string;
  status: string;
  step: string;
  error?: string | null;
  papers: JobPaper[];
}

const JSON_HEADERS = { 'Content-Type': 'application/json' };

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body.detail === 'string') return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((d: { msg?: string }) => d.msg).join(', ');
  } catch {
    /* fall through */
  }
  return await res.text() || `Request failed (${res.status})`;
}

export async function queryDocuments(
  query: string,
  options?: { documentFilter?: string; topK?: number },
): Promise<RAGQueryResponse> {
  const res = await fetch('/api/query', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({
      query,
      document_filter: options?.documentFilter,
      top_k: options?.topK ?? 5,
    }),
  });

  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function searchPapers(
  query: string,
  options?: { limit?: number; yearsBack?: number },
): Promise<{ query: string; count: number; results: SearchPaperResult[] }> {
  const res = await fetch('/api/search', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({
      query,
      limit: options?.limit ?? 20,
      years_back: options?.yearsBack ?? 10,
    }),
  });

  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function uploadPapers(files: File[]): Promise<ProcessingJobResponse> {
  const form = new FormData();
  files.forEach((f) => form.append('files', f));

  const res = await fetch('/api/papers/upload', {
    method: 'POST',
    body: form,
  });

  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function importPapers(
  paperIds: string[],
  titles?: Record<string, string>,
): Promise<ProcessingJobResponse> {
  const res = await fetch('/api/papers/import', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ paper_ids: paperIds, titles }),
  });

  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getJobStatus(jobId: string): Promise<ProcessingJobResponse> {
  const res = await fetch(`/api/jobs/${jobId}`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function listIndexedPapers(): Promise<{ papers: { id: string; title: string }[]; count: number }> {
  const res = await fetch('/api/papers');
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function pollJobUntilDone(
  jobId: string,
  onStep?: (step: string) => void,
  intervalMs = 800,
): Promise<ProcessingJobResponse> {
  while (true) {
    const job = await getJobStatus(jobId);
    if (onStep && job.step !== 'idle') onStep(job.step);
    if (job.status === 'completed' || job.status === 'error') return job;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch('/api/health');
    return res.ok;
  } catch {
    return false;
  }
}
