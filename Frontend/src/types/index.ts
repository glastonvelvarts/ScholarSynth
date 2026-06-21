export type AppView = 'landing' | 'workspace' | 'search';

export type ProcessingStatus =
  | 'idle'
  | 'uploading'
  | 'reading'
  | 'cleaning'
  | 'chunking'
  | 'embedding'
  | 'indexing'
  | 'ready'
  | 'error';

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  publicationVenue?: string;
  year?: number;
  tags: string[];
  source: 'upload' | 'search';
  pageCount?: number;
  fileSize?: number;
  uploadedAt: Date;
  processingStatus: ProcessingStatus;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

export interface Citation {
  id: string;
  paperId: string;
  paperTitle: string;
  text: string;
  pageNumber: number;
  relevanceScore: number;
}

export interface SearchResult {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  publicationVenue?: string;
  year?: number;
  tags: string[];
  relevanceScore: number;
  isOpenAccess: boolean;
  pdfUrl?: string;
  url?: string;
}

export interface SuggestedPrompt {
  id: string;
  text: string;
}

export const PROCESSING_STEPS: { id: ProcessingStatus; label: string; description: string }[] = [
  { id: 'uploading', label: 'Uploading', description: 'Transferring files to server' },
  { id: 'reading', label: 'Reading PDF', description: 'Extracting text content' },
  { id: 'cleaning', label: 'Cleaning Text', description: 'Normalising and preparing text' },
  { id: 'chunking', label: 'Semantic Chunking', description: 'Creating intelligent segments' },
  { id: 'embedding', label: 'Generating Embeddings', description: 'Creating vector representations' },
  { id: 'indexing', label: 'Building Search Index', description: 'Indexing knowledge base' },
  { id: 'ready', label: 'Ready', description: 'Papers are ready to query' },
];

export const SUGGESTED_PROMPTS: SuggestedPrompt[] = [
  { id: '1', text: 'Summarize all uploaded papers' },
  { id: '2', text: 'Compare the methodologies across papers' },
  { id: '3', text: 'Which paper achieved the highest F1 score?' },
  { id: '4', text: 'What datasets are commonly used?' },
  { id: '5', text: 'Explain the proposed architecture' },
  { id: '6', text: 'List limitations mentioned by the authors' },
];

export const TRENDING_TOPICS = [
  'Retrieval-Augmented Generation',
  'Vision Transformers',
  'Multi-agent Systems',
  'Graph Neural Networks',
  'Diffusion Models',
  'Large Language Models',
];
