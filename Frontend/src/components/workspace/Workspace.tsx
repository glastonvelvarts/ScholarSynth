import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Sparkles, FolderOpen, BookOpen } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { ChatPanel } from './ChatPanel';
import { ContextExplorer } from './ContextExplorer';
import { FileUpload, ProgressSteps } from '../ui';
import type { Paper, Message, Citation, ProcessingStatus, AppView } from '../../types';
import { PROCESSING_STEPS, SUGGESTED_PROMPTS } from '../../types';
import { generateId } from '../../lib/utils';

interface WorkspaceProps {
  onNavigate: (v: AppView) => void;
}

export function Workspace({ onNavigate }: WorkspaceProps) {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [showModal, setShowModal] = useState(true);
  const [step, setStep] = useState<ProcessingStatus>('idle');

  const handleFiles = useCallback(async (files: File[]) => {
    setIsBusy(true);
    const drafts: Paper[] = files.map((f) => ({
      id: generateId(), title: f.name.replace(/\.pdf$/i, ''), authors: [], abstract: '',
      tags: [], source: 'upload' as const,
      pageCount: Math.floor(Math.random() * 18) + 4,
      fileSize: f.size, uploadedAt: new Date(), processingStatus: 'uploading' as ProcessingStatus,
    }));
    setPapers(drafts);

    const statuses: ProcessingStatus[] = ['uploading','reading','cleaning','chunking','embedding','indexing','ready'];
    for (const s of statuses) {
      setStep(s);
      await sleep(680);
      setPapers((prev) => prev.map((p) => ({ ...p, processingStatus: s })));
    }

    setIsBusy(false);
    setStep('idle');
    setShowModal(false);
    setMessages([{
      id: generateId(), role: 'assistant',
      content: `I've processed ${files.length} paper${files.length !== 1 ? 's' : ''} and built your research knowledge base.\n\nYou can now ask questions, compare methodologies, summarise findings, or drill into specific topics. What would you like to know?`,
      timestamp: new Date(),
    }]);
  }, []);

  const handleSend = useCallback((text: string) => {
    setMessages((prev) => [...prev, { id: generateId(), role: 'user', content: text, timestamp: new Date() }]);
    setIsBusy(true);
    setTimeout(() => {
      const c = makeCitations(papers);
      setMessages((prev) => [...prev, { id: generateId(), role: 'assistant', content: demoAnswer(), timestamp: new Date(), citations: c }]);
      setCitations(c);
      setIsBusy(false);
    }, 1600);
  }, [papers]);

  const reset = () => { setPapers([]); setMessages([]); setCitations([]); setShowModal(true); };

  const readyCount = papers.filter((p) => p.processingStatus === 'ready').length;

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      <Sidebar papers={papers} currentView="workspace" onNavigate={onNavigate} onNewWorkspace={reset} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Workspace top bar */}
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
              <UploadModal onFiles={handleFiles} isBusy={isBusy} step={step} onDismiss={papers.length > 0 ? () => setShowModal(false) : undefined} />
            )}
          </AnimatePresence>
        </div>
      </div>

      <ContextExplorer papers={papers} activeCitations={citations} />
    </div>
  );
}

function UploadModal({
  onFiles, isBusy, step, onDismiss,
}: { onFiles: (f: File[]) => void; isBusy: boolean; step: ProcessingStatus; onDismiss?: () => void }) {
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
            <FileUpload onFilesSelected={onFiles} />
          </>
        )}
      </motion.div>
    </motion.div>
  );
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function demoAnswer(): string {
  const answers = [
    `Based on the uploaded papers, here is what I found:\n\n**Key Findings**\n- Transformer-based architectures dominate recent results\n- Average accuracy improvement over baselines: ~12–18%\n- Most papers evaluate on SQuAD, BEIR, and MS-MARCO\n\n**Methodology Overview**\nThe papers share a common pre-training → fine-tuning paradigm. Key differences lie in attention mechanisms, positional encodings, and training objectives.\n\n**Common Limitations**\n- High computational cost at inference\n- Limited cross-lingual generalisation\n- Sensitivity to prompt design`,
    `Here is a comparative summary across the uploaded documents:\n\n1. **Architectures** — All papers use encoder-decoder or decoder-only Transformers. Two introduce sparse attention variants.\n2. **Datasets** — Commonly used: MS-MARCO, Natural Questions, TriviaQA.\n3. **Results** — Best F1: 91.4 (Paper 2). Best ROUGE-L: 47.6 (Paper 3).\n\nThe authors converge on retrieval-augmented generation as the most promising direction for knowledge-intensive tasks.`,
    `The proposed architectures vary across the papers:\n\n**Paper 1** — Dense bi-encoder with late interaction scoring\n**Paper 2** — Cross-encoder re-ranker on top of a retrieval stage\n**Paper 3** — End-to-end differentiable retrieval pipeline\n\nAll three outperform BM25 baselines significantly. The end-to-end approach shows the highest ceiling but requires more training data.`,
  ];
  return answers[Math.floor(Math.random() * answers.length)];
}

function makeCitations(papers: Paper[]): Citation[] {
  return papers.slice(0, 3).map((p, i) => ({
    id: generateId(), paperId: p.id, paperTitle: p.title,
    text: 'This passage describes the core experimental methodology, including training details and evaluation metrics used in the study.',
    pageNumber: Math.floor(Math.random() * (p.pageCount ?? 10)) + 1,
    relevanceScore: 0.94 - i * 0.09,
  }));
}
