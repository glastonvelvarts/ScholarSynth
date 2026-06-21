import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Sparkles, BookOpen } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { ChatPanel } from './ChatPanel';
import { ContextExplorer } from './ContextExplorer';
import { FileUpload, ProgressSteps } from '../ui';
import type { Paper, Message, Citation, ProcessingStatus, AppView } from '../../types';
import { PROCESSING_STEPS, SUGGESTED_PROMPTS } from '../../types';
import { generateId } from '../../lib/utils';
import { queryDocuments, uploadPapers, pollJobUntilDone, importPapers, listIndexedPapers } from '../../lib/api';

interface WorkspaceProps {
  onNavigate: (v: AppView) => void;
  pendingImportIds?: string[];
  pendingImportTitles?: Record<string, string>;
  onImportsHandled?: () => void;
}

export function Workspace({ onNavigate, pendingImportIds, pendingImportTitles, onImportsHandled }: WorkspaceProps) {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [showModal, setShowModal] = useState(true);
  const [step, setStep] = useState<ProcessingStatus>('idle');
  const [processError, setProcessError] = useState('');

  useEffect(() => {
    listIndexedPapers()
      .then(({ papers: indexed }) => {
        if (indexed.length === 0) return;
        setPapers(indexed.map((p) => ({
          id: p.id,
          title: p.title,
          authors: [],
          abstract: '',
          tags: [],
          source: 'upload' as const,
          uploadedAt: new Date(),
          processingStatus: 'ready' as ProcessingStatus,
        })));
        setShowModal(false);
      })
      .catch(() => { /* index may be empty */ });
  }, []);

  useEffect(() => {
    if (!pendingImportIds?.length) return;

    let cancelled = false;
    (async () => {
      setIsBusy(true);
      setShowModal(true);
      setProcessError('');

      const drafts: Paper[] = pendingImportIds.map((id) => ({
        id,
        title: pendingImportTitles?.[id] ?? id,
        authors: [],
        abstract: '',
        tags: [],
        source: 'search' as const,
        uploadedAt: new Date(),
        processingStatus: 'uploading' as ProcessingStatus,
      }));
      setPapers((prev) => {
        const existing = new Set(prev.map((p) => p.id));
        return [...prev, ...drafts.filter((d) => !existing.has(d.id))];
      });

      try {
        const job = await importPapers(pendingImportIds, pendingImportTitles);
        const result = await pollJobUntilDone(job.job_id ?? job.id, (s) => setStep(s as ProcessingStatus));
        if (cancelled) return;

        setPapers((prev) => prev.map((p) => {
          const jp = result.papers.find((j) => j.id === p.id);
          if (!jp) return p;
          return {
            ...p,
            processingStatus: jp.status === 'ready' ? 'ready' : jp.status === 'error' ? 'error' : p.processingStatus,
            pageCount: jp.page_count,
          };
        }));

        const ready = result.papers.filter((p) => p.status === 'ready').length;
        const failed = result.papers.filter((p) => p.status === 'error');

        if (ready > 0) {
          setShowModal(false);
          setMessages((prev) => prev.length ? prev : [{
            id: generateId(), role: 'assistant',
            content: `I've imported ${ready} paper${ready !== 1 ? 's' : ''} into your knowledge base.${failed.length ? `\n\n${failed.length} paper${failed.length !== 1 ? 's' : ''} couldn't be downloaded (no open-access PDF available).` : ''}\n\nAsk me anything about them.`,
            timestamp: new Date(),
          }]);
        } else {
          setProcessError(failed[0]?.error ?? 'No papers could be imported. Try selecting open-access papers.');
        }
      } catch (err) {
        if (!cancelled) {
          setProcessError(err instanceof Error ? err.message : 'Import failed');
        }
      } finally {
        if (!cancelled) {
          setIsBusy(false);
          setStep('idle');
          onImportsHandled?.();
        }
      }
    })();

    return () => { cancelled = true; };
  }, [pendingImportIds, pendingImportTitles, onImportsHandled]);

  const handleFiles = useCallback(async (files: File[]) => {
    setIsBusy(true);
    setProcessError('');

    const drafts: Paper[] = files.map((f) => ({
      id: generateId(),
      title: f.name.replace(/\.pdf$/i, ''),
      authors: [],
      abstract: '',
      tags: [],
      source: 'upload' as const,
      fileSize: f.size,
      uploadedAt: new Date(),
      processingStatus: 'uploading' as ProcessingStatus,
    }));
    setPapers(drafts);

    try {
      const job = await uploadPapers(files);
      const result = await pollJobUntilDone(job.job_id ?? job.id, (s) => setStep(s as ProcessingStatus));

      setPapers(result.papers.map((jp) => ({
        id: jp.id,
        title: jp.title,
        authors: [],
        abstract: '',
        tags: [],
        source: 'upload' as const,
        pageCount: jp.page_count,
        uploadedAt: new Date(),
        processingStatus: jp.status === 'ready' ? 'ready' : jp.status === 'error' ? 'error' : 'ready',
      })));

      const ready = result.papers.filter((p) => p.status === 'ready').length;
      if (ready > 0) {
        setShowModal(false);
        setMessages([{
          id: generateId(), role: 'assistant',
          content: `I've processed ${ready} paper${ready !== 1 ? 's' : ''} and built your research knowledge base.\n\nYou can now ask questions, compare methodologies, summarise findings, or drill into specific topics. What would you like to know?`,
          timestamp: new Date(),
        }]);
      } else {
        const err = result.papers.find((p) => p.error)?.error ?? result.error ?? 'Processing failed';
        setProcessError(err);
      }
    } catch (err) {
      setProcessError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsBusy(false);
      setStep('idle');
    }
  }, []);

  const handleSend = useCallback(async (text: string) => {
    setMessages((prev) => [...prev, { id: generateId(), role: 'user', content: text, timestamp: new Date() }]);
    setIsBusy(true);
    try {
      const result = await queryDocuments(text);
      const c: Citation[] = result.citations.map((cite) => ({
        id: cite.id,
        paperId: cite.paper_id,
        paperTitle: cite.paper_title,
        text: cite.text,
        pageNumber: cite.page_number,
        relevanceScore: cite.relevance_score,
      }));
      setMessages((prev) => [...prev, {
        id: generateId(),
        role: 'assistant',
        content: result.answer,
        timestamp: new Date(),
        citations: c,
      }]);
      setCitations(c);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong.';
      setMessages((prev) => [...prev, {
        id: generateId(),
        role: 'assistant',
        content: `I couldn't complete that query.\n\n${message}`,
        timestamp: new Date(),
      }]);
    } finally {
      setIsBusy(false);
    }
  }, []);

  const reset = () => { setPapers([]); setMessages([]); setCitations([]); setShowModal(true); setProcessError(''); };

  const readyCount = papers.filter((p) => p.processingStatus === 'ready').length;

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      <Sidebar papers={papers} currentView="workspace" onNavigate={onNavigate} onNewWorkspace={reset} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="shrink-0 h-12 border-b border-[color:var(--border)] flex items-center justify-between px-5" style={{ background: 'var(--bg-surface)' }}>
          <div className="flex items-center gap-2.5">
            <BookOpen className="w-4 h-4 text-forest-600 dark:text-forest-400" />
            <span className="text-sm font-semibold text-[color:var(--text-primary)]">Research Workspace</span>
            {readyCount > 0 && (
              <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-forest-100 dark:bg-forest-900/50 text-forest-700 dark:text-forest-400">
                {readyCount} paper{readyCount !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          {papers.length > 0 && (
            <button
              onClick={() => setShowModal(true)}
              className="btn-secondary py-1.5 px-3 text-xs gap-1.5 flex items-center"
            >
              <Upload className="w-3.5 h-3.5" /> Add papers
            </button>
          )}
        </div>

        <div className="flex-1 relative overflow-hidden flex">
          <ChatPanel
            messages={messages}
            suggestedPrompts={SUGGESTED_PROMPTS}
            onSendMessage={handleSend}
            isBusy={isBusy && !showModal}
          />
          <AnimatePresence>
            {showModal && (
              <UploadModal
                onFiles={handleFiles}
                isBusy={isBusy}
                step={step}
                error={processError}
                onDismiss={papers.length > 0 ? () => setShowModal(false) : undefined}
              />
            )}
          </AnimatePresence>
        </div>
      </div>

      <ContextExplorer papers={papers} activeCitations={citations} />
    </div>
  );
}

function UploadModal({
  onFiles, isBusy, step, error, onDismiss,
}: { onFiles: (f: File[]) => void; isBusy: boolean; step: ProcessingStatus; error?: string; onDismiss?: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="absolute inset-0 z-20 flex items-center justify-center p-8"
      style={{ background: 'rgba(11,26,16,0.55)', backdropFilter: 'blur(6px)' }}
    >
      <motion.div
        initial={{ scale: 0.92, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.92, y: 16 }}
        className="w-full max-w-md rounded-2xl p-7 shadow-2xl border border-[color:var(--border)]"
        style={{ background: 'var(--bg-surface)' }}
      >
        {isBusy ? (
          <>
            <div className="text-center mb-7">
              <motion.div
                animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="w-14 h-14 rounded-2xl bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center mx-auto mb-4"
              >
                <Sparkles className="w-7 h-7 text-amber-500" />
              </motion.div>
              <h3 className="text-lg font-bold text-[color:var(--text-primary)]">Processing papers…</h3>
              <p className="text-xs text-[color:var(--text-muted)] mt-1">Building your semantic knowledge base</p>
            </div>
            <ProgressSteps steps={PROCESSING_STEPS} currentStep={step} />
          </>
        ) : (
          <>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-[color:var(--text-primary)] mb-1">Upload Research Papers</h3>
                <p className="text-sm text-[color:var(--text-muted)]">Add up to 10 PDF files — we handle the rest</p>
              </div>
              {onDismiss && (
                <button onClick={onDismiss} className="text-xs text-[color:var(--text-muted)] hover:text-[color:var(--text-secondary)] transition-colors ml-4 shrink-0">
                  Cancel
                </button>
              )}
            </div>
            {error && (
              <div className="mb-4 px-3 py-2.5 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 text-sm text-red-700 dark:text-red-400">
                {error}
              </div>
            )}
            <FileUpload onFilesSelected={onFiles} />
          </>
        )}
      </motion.div>
    </motion.div>
  );
}
