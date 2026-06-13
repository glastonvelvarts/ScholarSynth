import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, FileText, ChevronDown, BookOpen, ArrowUpRight } from 'lucide-react';
import { Badge } from '../ui';
import type { Message, Citation, SuggestedPrompt } from '../../types';

interface ChatPanelProps {
  messages: Message[];
  suggestedPrompts: SuggestedPrompt[];
  onSendMessage: (msg: string) => void;
  isBusy: boolean;
}

export function ChatPanel({ messages, suggestedPrompts, onSendMessage, isBusy }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, isBusy]);

  const send = () => {
    const t = input.trim();
    if (!t || isBusy) return;
    onSendMessage(t);
    setInput('');
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      <div className="flex-1 overflow-y-auto scrollbar-thin px-6 py-6">
        {messages.length === 0 ? (
          <EmptyState prompts={suggestedPrompts} onPrompt={onSendMessage} />
        ) : (
          <div className="max-w-2xl mx-auto space-y-5">
            <AnimatePresence initial={false}>
              {messages.map((m) => <MessageBubble key={m.id} message={m} />)}
            </AnimatePresence>
            {isBusy && (
              <div className="flex items-center gap-2 pl-1">
                <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.3 }}>
                  <Sparkles className="w-4 h-4 text-amber-400" />
                </motion.div>
                <span className="text-sm text-[color:var(--text-muted)]">Synthesising…</span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-[color:var(--border)] px-6 py-4 shrink-0" style={{ background: 'var(--bg-surface)' }}>
        <div className="max-w-2xl mx-auto flex items-end gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Ask anything about your research papers…"
            rows={1}
            disabled={isBusy}
            className="flex-1 resize-none input-base text-sm rounded-2xl"
            style={{ maxHeight: 140 }}
          />
          <motion.button
            whileHover={{ scale: 1.06 }}
            whileTap={{ scale: 0.94 }}
            onClick={send}
            disabled={!input.trim() || isBusy}
            className="w-11 h-11 rounded-2xl bg-forest-700 dark:bg-forest-600 hover:bg-forest-800 dark:hover:bg-forest-500 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center text-white transition-colors shrink-0"
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ prompts, onPrompt }: { prompts: SuggestedPrompt[]; onPrompt: (t: string) => void }) {
  return (
    <div className="max-w-2xl mx-auto pt-8">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
        <div className="w-14 h-14 rounded-2xl bg-forest-800 dark:bg-forest-700 flex items-center justify-center mx-auto mb-5 shadow-glow">
          <BookOpen className="w-6 h-6 text-amber-300" />
        </div>
        <h2 className="text-xl font-bold text-[color:var(--text-primary)] mb-2">What would you like to know?</h2>
        <p className="text-sm text-[color:var(--text-muted)]">
          Your papers are ready. Ask anything — comparisons, summaries, specific data points.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {prompts.map((p, i) => (
          <motion.button
            key={p.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            onClick={() => onPrompt(p.text)}
            className="group text-left p-4 rounded-xl border border-[color:var(--border)] text-sm text-[color:var(--text-secondary)] hover:border-forest-400 dark:hover:border-forest-600 hover:bg-forest-50 dark:hover:bg-forest-950/30 transition-all flex items-center justify-between gap-3"
            style={{ background: 'var(--bg-surface)' }}
          >
            <span>{p.text}</span>
            <ArrowUpRight className="w-3.5 h-3.5 text-[color:var(--text-muted)] group-hover:text-forest-600 dark:group-hover:text-forest-400 shrink-0 transition-colors" />
          </motion.button>
        ))}
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const user = message.role === 'user';
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className={`flex ${user ? 'justify-end' : 'justify-start'}`}>
      <div className="max-w-[88%]">
        {!user && (
          <div className="flex items-center gap-1.5 mb-1.5">
            <div className="w-5 h-5 rounded-md bg-forest-800 dark:bg-forest-700 flex items-center justify-center">
              <BookOpen style={{ width: 10, height: 10 }} className="text-amber-300" />
            </div>
            <span className="text-xs font-semibold text-[color:var(--text-muted)]">ScholarSynth</span>
          </div>
        )}
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            user
              ? 'bg-forest-700 dark:bg-forest-600 text-white'
              : 'border border-[color:var(--border)] text-[color:var(--text-primary)]'
          }`}
          style={!user ? { background: 'var(--bg-surface)' } : {}}
        >
          <pre className="whitespace-pre-wrap font-sans">{message.content}</pre>
        </div>
        {message.citations && message.citations.length > 0 && <CitationsRow citations={message.citations} />}
      </div>
    </motion.div>
  );
}

function CitationsRow({ citations }: { citations: Citation[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-xs text-[color:var(--text-muted)] hover:text-[color:var(--text-secondary)] transition-colors"
      >
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`} />
        {citations.length} source{citations.length !== 1 ? 's' : ''} cited
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 space-y-2"
          >
            {citations.map((c) => (
              <div key={c.id} className="flex items-start gap-2.5 p-2.5 rounded-lg border border-[color:var(--border)]" style={{ background: 'var(--bg-surface)' }}>
                <div className="w-7 h-7 rounded-md bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center shrink-0">
                  <FileText className="w-3.5 h-3.5 text-forest-600 dark:text-forest-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-[color:var(--text-primary)] truncate">{c.paperTitle}</p>
                  <p className="text-xs text-[color:var(--text-muted)] mt-0.5 line-clamp-2">{c.text}</p>
                </div>
                <Badge variant="muted">p.{c.pageNumber}</Badge>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
