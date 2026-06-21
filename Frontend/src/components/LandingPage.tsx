import React from 'react';
import { motion } from 'framer-motion';
import {
  Upload, Search, BookMarked, ArrowRight,
  MessageSquare, FileText, Layers, Sparkles,
  Quote, Check,
} from 'lucide-react';
import { ThemeToggle } from './ui/ThemeToggle';
import type { AppView } from '../types';

interface LandingPageProps {
  onNavigate: (view: AppView) => void;
}

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 22 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, delay },
});

export function LandingPage({ onNavigate }: LandingPageProps) {
  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-base)' }}>
      {/* Ambient blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute -top-32 right-0 w-[520px] h-[520px] rounded-full bg-forest-200/25 dark:bg-forest-900/15 blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-[400px] h-[400px] rounded-full bg-amber-200/20 dark:bg-amber-900/10 blur-3xl" />
        <div className="absolute bottom-0 right-1/3 w-[360px] h-[360px] rounded-full bg-forest-300/15 dark:bg-forest-800/10 blur-3xl" />
      </div>

      {/* ── Nav ── */}
      <header className="sticky top-0 z-30 border-b border-[color:var(--border)]" style={{ background: 'var(--bg-surface)', backdropFilter: 'blur(12px)' }}>
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-forest-800 dark:bg-forest-700 flex items-center justify-center shadow-glow">
              <BookMarked style={{ width: 15, height: 15 }} className="text-amber-300" />
            </div>
            <span className="font-bold text-[color:var(--text-primary)] tracking-tight">ScholarSynth</span>
          </div>

          <nav className="hidden md:flex items-center gap-1">
            {['Features', 'Use Cases'].map((l) => (
              <button key={l} className="btn-ghost px-4 py-2 text-sm text-[color:var(--text-secondary)]">{l}</button>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <button onClick={() => onNavigate('workspace')} className="btn-primary px-4 py-2 text-sm">Get started</button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="max-w-5xl mx-auto px-6 pt-24 pb-20 text-center">
        <motion.div {...fadeUp(0)}>
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-amber-300/60 dark:border-amber-700/60 bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400 text-xs font-semibold mb-7">
            <Sparkles className="w-3.5 h-3.5" />
            AI-powered research synthesis
          </span>
        </motion.div>

        <motion.h1 {...fadeUp(0.08)} className="text-[clamp(2.8rem,7vw,5.5rem)] font-extrabold tracking-tight leading-[1.04] text-[color:var(--text-primary)] mb-6">
          Stop reading.<br />
          <span className="text-forest-700 dark:text-forest-400">Start understanding.</span>
        </motion.h1>

        <motion.p {...fadeUp(0.16)} className="text-lg text-[color:var(--text-secondary)] max-w-2xl mx-auto leading-relaxed mb-10">
          Upload your research papers and ask anything — ScholarSynth reads, indexes, and
          synthesises your documents so you get precise answers with exact citations in seconds.
        </motion.p>

        <motion.div {...fadeUp(0.22)} className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={() => onNavigate('workspace')}
            className="btn-primary px-7 py-3.5 text-base gap-2 shadow-glow"
          >
            Upload your first paper <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => onNavigate('search')}
            className="btn-secondary px-7 py-3.5 text-base gap-2"
          >
            <Search className="w-4 h-4" /> Browse papers
          </button>
        </motion.div>

        <motion.p {...fadeUp(0.28)} className="mt-5 text-xs text-[color:var(--text-muted)]">
          No sign-up required. Works with any PDF.
        </motion.p>

        {/* Product mockup */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.35 }}
          className="mt-16 rounded-2xl border border-[color:var(--border)] overflow-hidden shadow-card-hover"
          style={{ background: 'var(--bg-surface)' }}
        >
          <MockupPreview />
        </motion.div>
      </section>

      {/* ── Trusted by strip ── */}
      <section className="border-y border-[color:var(--border)] py-8" style={{ background: 'var(--bg-elevated)' }}>
        <div className="max-w-5xl mx-auto px-6">
          <p className="text-center text-xs font-semibold text-[color:var(--text-muted)] uppercase tracking-widest mb-6">
            Trusted by researchers at
          </p>
          <div className="flex items-center justify-center gap-10 flex-wrap">
            {['MIT', 'Stanford', 'Oxford', 'ETH Zürich', 'Carnegie Mellon', 'UC Berkeley'].map((inst) => (
              <span key={inst} className="text-sm font-bold text-[color:var(--text-muted)] opacity-60 hover:opacity-100 transition-opacity">
                {inst}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── Three pillars ── */}
      <section className="max-w-5xl mx-auto px-6 py-24">
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-14">
          <h2 className="text-3xl font-extrabold text-[color:var(--text-primary)] mb-3">Everything you need. Nothing you don't.</h2>
          <p className="text-[color:var(--text-muted)] max-w-lg mx-auto">A focused set of tools that make dense academic papers genuinely usable.</p>
        </motion.div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {PILLARS.map((p, i) => (
            <motion.div key={p.title} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
              <div className="card p-6 h-full">
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-5 ${p.iconClass}`}>{p.icon}</div>
                <h3 className="font-bold text-[color:var(--text-primary)] mb-2">{p.title}</h3>
                <p className="text-sm text-[color:var(--text-muted)] leading-relaxed">{p.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Feature rows ── */}
      <section className="max-w-5xl mx-auto px-6 pb-24 space-y-20">
        <FeatureRow
          eyebrow="Upload & Chat"
          headline="Your papers. Your questions. Instant answers."
          body="Drag in up to 10 PDFs and ScholarSynth builds a semantic knowledge base in seconds. Ask anything — from methodology comparisons to specific data points — and get answers grounded in your own documents."
          bullets={['Cross-paper synthesis', 'Page-level citations for every answer', 'Supports tables, equations, and figures']}
          visual={<UploadVisual />}
          ctaLabel="Start uploading"
          ctaView="workspace"
          onNavigate={onNavigate}
          reverse={false}
        />
        <FeatureRow
          eyebrow="Paper Discovery"
          headline="Find the papers that matter before you read them."
          body="Search across millions of papers and read AI-generated summaries to decide what's worth your time. One click imports any paper directly into your workspace."
          bullets={['AI summaries before you commit to reading', 'Filter by year, domain, open access', 'Import directly into your workspace']}
          visual={<SearchVisual />}
          ctaLabel="Discover papers"
          ctaView="search"
          onNavigate={onNavigate}
          reverse={true}
        />
      </section>

      {/* ── Testimonials ── */}
      <section className="border-t border-[color:var(--border)] py-24" style={{ background: 'var(--bg-elevated)' }}>
        <div className="max-w-5xl mx-auto px-6">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-14">
            <h2 className="text-3xl font-extrabold text-[color:var(--text-primary)] mb-3">Researchers love it</h2>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {TESTIMONIALS.map((t, i) => (
              <motion.div key={t.name} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                <div className="card p-6 h-full flex flex-col">
                  <Quote className="w-5 h-5 text-amber-400 mb-4 shrink-0" />
                  <p className="text-sm text-[color:var(--text-secondary)] leading-relaxed flex-1 mb-5">"{t.quote}"</p>
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center text-forest-700 dark:text-forest-400 font-bold text-sm">
                      {t.name[0]}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-[color:var(--text-primary)]">{t.name}</p>
                      <p className="text-xs text-[color:var(--text-muted)]">{t.role}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Bottom CTA ── */}
      <section className="max-w-5xl mx-auto px-6 py-24 text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <div className="card p-14 border-2 border-forest-200 dark:border-forest-800">
            <div className="w-14 h-14 rounded-2xl bg-forest-800 dark:bg-forest-700 flex items-center justify-center mx-auto mb-6 shadow-glow">
              <BookMarked className="w-7 h-7 text-amber-300" />
            </div>
            <h2 className="text-4xl font-extrabold text-[color:var(--text-primary)] mb-4">
              Ready to read smarter?
            </h2>
            <p className="text-[color:var(--text-muted)] max-w-md mx-auto mb-8">
              Join thousands of researchers who've cut their literature review time in half.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button onClick={() => onNavigate('workspace')} className="btn-primary px-8 py-3.5 text-base gap-2 shadow-glow">
                Get started <ArrowRight className="w-4 h-4" />
              </button>
              <button onClick={() => onNavigate('search')} className="btn-secondary px-8 py-3.5 text-base">
                Explore papers first
              </button>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-[color:var(--border)] py-10" style={{ background: 'var(--bg-surface)' }}>
        <div className="max-w-5xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-forest-800 dark:bg-forest-700 flex items-center justify-center">
              <BookMarked style={{ width: 12, height: 12 }} className="text-amber-300" />
            </div>
            <span className="font-bold text-sm text-[color:var(--text-primary)]">ScholarSynth</span>
            <span className="text-xs text-[color:var(--text-muted)] ml-2">Making research accessible through AI</span>
          </div>
          <div className="flex items-center gap-6 text-xs text-[color:var(--text-muted)]">
            {['Features', 'Privacy', 'Terms', 'Contact'].map((l) => (
              <a key={l} href="#" className="hover:text-[color:var(--text-secondary)] transition-colors">{l}</a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}

// ── Feature row component ─────────────────────────────────────────────────────

interface FeatureRowProps {
  eyebrow: string;
  headline: string;
  body: string;
  bullets: string[];
  visual: React.ReactNode;
  ctaLabel: string;
  ctaView: AppView;
  onNavigate: (v: AppView) => void;
  reverse: boolean;
}

function FeatureRow({ eyebrow, headline, body, bullets, visual, ctaLabel, ctaView, onNavigate, reverse }: FeatureRowProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.55 }}
      className={`flex flex-col ${reverse ? 'lg:flex-row-reverse' : 'lg:flex-row'} items-center gap-12`}
    >
      <div className="flex-1">
        <span className="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-widest">{eyebrow}</span>
        <h2 className="text-3xl font-extrabold text-[color:var(--text-primary)] mt-2 mb-4 leading-snug">{headline}</h2>
        <p className="text-[color:var(--text-secondary)] leading-relaxed mb-6">{body}</p>
        <ul className="space-y-2.5 mb-8">
          {bullets.map((b) => (
            <li key={b} className="flex items-center gap-2.5 text-sm text-[color:var(--text-secondary)]">
              <div className="w-5 h-5 rounded-full bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center shrink-0">
                <Check className="w-3 h-3 text-forest-600 dark:text-forest-400" />
              </div>
              {b}
            </li>
          ))}
        </ul>
        <button onClick={() => onNavigate(ctaView)} className="btn-primary px-5 py-2.5 text-sm gap-2">
          {ctaLabel} <ArrowRight className="w-4 h-4" />
        </button>
      </div>
      <div className="flex-1 w-full rounded-2xl overflow-hidden border border-[color:var(--border)] shadow-card-hover">
        {visual}
      </div>
    </motion.div>
  );
}

// ── Mockup visuals ────────────────────────────────────────────────────────────

function MockupPreview() {
  return (
    <div className="flex" style={{ minHeight: 360 }}>
      {/* Sidebar */}
      <div className="w-44 border-r border-[color:var(--border)] p-3 hidden sm:block shrink-0" style={{ background: 'var(--bg-surface)' }}>
        <div className="flex items-center gap-1.5 mb-4 px-1">
          <div className="w-5 h-5 rounded-md bg-forest-800 flex items-center justify-center">
            <BookMarked style={{ width: 10, height: 10 }} className="text-amber-300" />
          </div>
          <span className="text-xs font-bold text-[color:var(--text-primary)]">ScholarSynth</span>
        </div>
        {['Home', 'Search'].map((item) => (
          <div key={item} className="px-2 py-1.5 rounded-lg text-xs text-[color:var(--text-muted)] flex items-center gap-2 mb-0.5">
            <div className="w-3 h-3 rounded bg-[color:var(--border)]" />
            {item}
          </div>
        ))}
        <div className="mt-3 px-2 py-1 text-xs font-bold text-[color:var(--text-muted)] uppercase tracking-wider">Workspace</div>
        {['attention-is-all.pdf', 'bert-paper.pdf', 'gpt4-report.pdf'].map((f) => (
          <div key={f} className="px-2 py-1.5 rounded-lg flex items-center gap-1.5 mb-0.5">
            <FileText className="w-3 h-3 text-forest-500 shrink-0" />
            <span className="text-xs text-[color:var(--text-muted)] truncate">{f}</span>
          </div>
        ))}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col" style={{ background: 'var(--bg-base)' }}>
        <div className="flex-1 p-5 space-y-4 overflow-hidden">
          <MockMessage user text="Compare the attention mechanisms across all three papers" />
          <MockMessage user={false} text={`All three papers use multi-head self-attention, but differ in scale and application:\n\n• Attention Is All You Need — 8 heads, d_model=512, foundational encoder-decoder design\n• BERT — 12 or 24 heads (Base/Large), bidirectional pre-training objective\n• GPT-4 — Undisclosed head count, autoregressive decoder-only architecture\n\nBERT uses masked attention for pre-training while GPT-4 uses causal masking.`} />
        </div>
        <div className="border-t border-[color:var(--border)] px-4 py-3 flex items-center gap-2" style={{ background: 'var(--bg-surface)' }}>
          <div className="flex-1 h-8 rounded-xl border border-[color:var(--border)] px-3 flex items-center">
            <span className="text-xs text-[color:var(--text-muted)]">Ask anything about your research papers…</span>
          </div>
          <div className="w-8 h-8 rounded-xl bg-forest-700 flex items-center justify-center shrink-0">
            <ArrowRight className="w-3.5 h-3.5 text-white" />
          </div>
        </div>
      </div>

      {/* Context panel */}
      <div className="w-52 border-l border-[color:var(--border)] p-3 hidden lg:block shrink-0" style={{ background: 'var(--bg-surface)' }}>
        <p className="text-xs font-bold text-[color:var(--text-primary)] mb-3">Context Explorer</p>
        {[
          { title: 'attention-is-all.pdf', page: 4, score: 96 },
          { title: 'bert-paper.pdf', page: 7, score: 89 },
          { title: 'gpt4-report.pdf', page: 12, score: 81 },
        ].map((s) => (
          <div key={s.title} className="p-2 rounded-lg border border-[color:var(--border)] mb-2" style={{ background: 'var(--bg-elevated)' }}>
            <div className="flex items-center gap-1.5 mb-1">
              <FileText className="w-3 h-3 text-forest-500 shrink-0" />
              <span className="text-xs text-[color:var(--text-muted)] truncate">{s.title}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
                <div className="h-full bg-forest-500 rounded-full" style={{ width: `${s.score}%` }} />
              </div>
              <span className="text-xs text-forest-600 dark:text-forest-400 font-medium">{s.score}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MockMessage({ user, text }: { user: boolean; text: string }) {
  return (
    <div className={`flex ${user ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] px-3 py-2 rounded-xl text-xs leading-relaxed ${
        user
          ? 'bg-forest-700 dark:bg-forest-600 text-white'
          : 'border border-[color:var(--border)] text-[color:var(--text-primary)]'
      }`}
        style={!user ? { background: 'var(--bg-surface)' } : {}}
      >
        <pre className="whitespace-pre-wrap font-sans">{text}</pre>
      </div>
    </div>
  );
}

function UploadVisual() {
  return (
    <div className="p-7" style={{ background: 'var(--bg-surface)', minHeight: 280 }}>
      <div className="border-2 border-dashed border-forest-300 dark:border-forest-700 rounded-xl p-8 text-center mb-4">
        <div className="w-12 h-12 rounded-xl bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center mx-auto mb-3">
          <Upload className="w-5 h-5 text-forest-600 dark:text-forest-400" />
        </div>
        <p className="text-sm font-semibold text-[color:var(--text-primary)] mb-1">Drop PDFs here</p>
        <p className="text-xs text-[color:var(--text-muted)]">Up to 10 files, 20 MB each</p>
      </div>
      <div className="space-y-2">
        {['attention-is-all-you-need.pdf', 'bert-pretraining-deep.pdf'].map((f, i) => (
          <div key={f} className="flex items-center gap-2.5 px-3 py-2 rounded-lg border border-[color:var(--border)]" style={{ background: 'var(--bg-elevated)' }}>
            <div className="w-7 h-7 rounded-md bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center shrink-0">
              <FileText className="w-3.5 h-3.5 text-forest-600 dark:text-forest-400" />
            </div>
            <span className="flex-1 text-xs text-[color:var(--text-secondary)] truncate">{f}</span>
            <div className="flex items-center gap-1">
              <div className="w-14 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
                <div className="h-full bg-forest-500 rounded-full" style={{ width: i === 0 ? '100%' : '60%' }} />
              </div>
              <span className="text-xs text-forest-600 dark:text-forest-400">{i === 0 ? 'Ready' : '60%'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SearchVisual() {
  return (
    <div className="p-7" style={{ background: 'var(--bg-surface)', minHeight: 280 }}>
      <div className="relative mb-5">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[color:var(--text-muted)]" />
        <div className="input-base pl-9 py-2.5 text-sm">Retrieval-Augmented Generation</div>
      </div>
      <div className="space-y-3">
        {[
          { title: 'RAG for Knowledge-Intensive NLP Tasks', venue: 'NeurIPS 2020', score: 97 },
          { title: 'Dense Passage Retrieval for Open-Domain QA', venue: 'EMNLP 2020', score: 91 },
          { title: 'REALM: Retrieval-Augmented Language Model', venue: 'ICML 2020', score: 85 },
        ].map((r) => (
          <div key={r.title} className="p-3 rounded-xl border border-[color:var(--border)]" style={{ background: 'var(--bg-elevated)' }}>
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-[color:var(--text-primary)] leading-snug">{r.title}</p>
                <p className="text-xs text-[color:var(--text-muted)] mt-0.5">{r.venue}</p>
              </div>
              <span className="text-xs font-bold text-forest-700 dark:text-forest-400 shrink-0">{r.score}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Data ──────────────────────────────────────────────────────────────────────

const PILLARS = [
  {
    icon: <MessageSquare className="w-5 h-5" />,
    iconClass: 'bg-forest-100 dark:bg-forest-900/50 text-forest-700 dark:text-forest-400',
    title: 'Conversational Q&A',
    desc: 'Ask natural language questions across all your papers. Get precise, cited answers — not keyword matches.',
  },
  {
    icon: <Layers className="w-5 h-5" />,
    iconClass: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
    title: 'Cross-Paper Synthesis',
    desc: 'Compare methodologies, aggregate results, spot contradictions — across all your documents at once.',
  },
  {
    icon: <Search className="w-5 h-5" />,
    iconClass: 'bg-forest-100 dark:bg-forest-900/50 text-forest-700 dark:text-forest-400',
    title: 'Intelligent Discovery',
    desc: 'Search millions of papers with AI-generated summaries. Know if a paper is worth reading before you open it.',
  },
];

const TESTIMONIALS = [
  {
    quote: "I used to spend a full day doing a literature review. With ScholarSynth I'm done in an hour and I actually understand what I read.",
    name: 'Dr. Sarah Chen',
    role: 'ML Researcher, Stanford',
  },
  {
    quote: "The cross-paper synthesis is unreal. I uploaded 8 papers about attention mechanisms and asked it to compare them. The answer would have taken me a week to write manually.",
    name: 'James Okafor',
    role: 'PhD Candidate, Oxford',
  },
  {
    quote: "Every answer has a page citation. I can verify anything instantly. That trust is what makes it actually useful for serious research.",
    name: 'Prof. Ana Ruiz',
    role: 'Associate Professor, ETH Zürich',
  },
];
