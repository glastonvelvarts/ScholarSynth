import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, ChevronRight, Quote, Telescope } from 'lucide-react';
import { Badge } from '../ui';
import type { Citation, Paper } from '../../types';

interface ContextExplorerProps {
  papers: Paper[];
  activeCitations: Citation[];
}

export function ContextExplorer({ papers, activeCitations }: ContextExplorerProps) {
  return (
    <aside className="w-72 h-screen border-l border-[color:var(--border)] flex flex-col shrink-0" style={{ background: 'var(--bg-surface)' }}>
      <div className="px-4 py-4 border-b border-[color:var(--border)]">
        <div className="flex items-center gap-2">
          <Telescope className="w-4 h-4 text-amber-500" />
          <h2 className="font-bold text-sm text-[color:var(--text-primary)]">Context Explorer</h2>
        </div>
        <p className="text-xs text-[color:var(--text-muted)] mt-0.5">Retrieved evidence for the current response</p>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin p-3">
        {activeCitations.length === 0 ? <EmptyState /> : (
          <div className="space-y-2.5">
            {activeCitations.map((c, i) => (
              <motion.div key={c.id} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
                <SourceCard citation={c} />
              </motion.div>
            ))}
          </div>
        )}
      </div>
      <div className="border-t border-[color:var(--border)] px-4 py-3 flex items-center justify-between">
        <span className="text-xs text-[color:var(--text-muted)]">Papers in workspace</span>
        <Badge variant="forest">{papers.length}</Badge>
      </div>
    </aside>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-14">
      <div className="w-12 h-12 rounded-xl bg-parchment-200 dark:bg-dark-elevated flex items-center justify-center mx-auto mb-3">
        <Telescope className="w-5 h-5 text-[color:var(--text-muted)]" />
      </div>
      <p className="text-sm font-medium text-[color:var(--text-secondary)]">No context yet</p>
      <p className="text-xs text-[color:var(--text-muted)] mt-1">Ask a question to see sources here</p>
    </div>
  );
}

function SourceCard({ citation }: { citation: Citation }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-xl border border-[color:var(--border)] overflow-hidden" style={{ background: 'var(--bg-elevated)' }}>
      <button onClick={() => setOpen(!open)} className="w-full p-3 flex items-start gap-2.5 hover:bg-forest-50 dark:hover:bg-dark-card transition-colors text-left">
        <div className="w-8 h-8 rounded-lg bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center shrink-0">
          <FileText className="w-4 h-4 text-forest-600 dark:text-forest-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-[color:var(--text-primary)] truncate">{citation.paperTitle}</p>
          <div className="flex items-center gap-2 mt-1">
            <Badge variant="muted">p.{citation.pageNumber}</Badge>
            <div className="flex items-center gap-1">
              <div className="w-10 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
                <div className="h-full bg-forest-500 dark:bg-forest-400 rounded-full" style={{ width: `${citation.relevanceScore * 100}%` }} />
              </div>
              <span className="text-xs text-[color:var(--text-muted)]">{Math.round(citation.relevanceScore * 100)}%</span>
            </div>
          </div>
        </div>
        <ChevronRight className={`w-4 h-4 text-[color:var(--text-muted)] shrink-0 transition-transform ${open ? 'rotate-90' : ''}`} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="border-t border-[color:var(--border)]">
            <div className="p-3" style={{ background: 'var(--bg-surface)' }}>
              <div className="flex items-start gap-2">
                <Quote className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <p className="text-xs text-[color:var(--text-secondary)] leading-relaxed">{citation.text}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
