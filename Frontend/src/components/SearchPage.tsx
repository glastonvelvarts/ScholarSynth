import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, X, Filter, BookmarkPlus, ExternalLink,
  FileText, Calendar, Building2, ChevronLeft, BookMarked,
  AlertCircle,
} from 'lucide-react';
import { Badge, Card } from './ui';
import { ThemeToggle } from './ui/ThemeToggle';
import type { SearchResult, AppView } from '../types';
import { TRENDING_TOPICS } from '../types';
import { searchPapers } from '../lib/api';

interface SearchPageProps {
  onNavigate: (v: AppView) => void;
  onAddToWorkspace: (results: SearchResult[]) => void;
}

export function SearchPage({ onNavigate, onAddToWorkspace }: SearchPageProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [added, setAdded] = useState<Set<string>>(new Set());
  const [error, setError] = useState('');
  const [yearsBack, setYearsBack] = useState(10);
  const [openAccessOnly, setOpenAccessOnly] = useState(false);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) return;
    setQuery(q);
    setLoading(true);
    setSearched(true);
    setError('');

    try {
      const data = await searchPapers(q.trim(), { limit: 20, yearsBack });
      let mapped: SearchResult[] = data.results.map((r) => ({
        id: r.id,
        title: r.title,
        authors: r.authors,
        abstract: r.abstract,
        publicationVenue: r.publication_venue,
        year: r.year,
        tags: r.tags,
        relevanceScore: r.relevance_score,
        isOpenAccess: r.is_open_access,
        pdfUrl: r.pdf_url,
        url: r.url,
      }));
      if (openAccessOnly) {
        mapped = mapped.filter((r) => r.isOpenAccess);
      }
      setResults(mapped);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [yearsBack, openAccessOnly]);

  const handleAdd = (r: SearchResult) => {
    if (!r.isOpenAccess) return;
    setAdded((p) => new Set(p).add(r.id));
    onAddToWorkspace([r]);
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-base)' }}>
      <header className="border-b border-[color:var(--border)] sticky top-0 z-10" style={{ background: 'var(--bg-surface)' }}>
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
          <button onClick={() => onNavigate('landing')} className="flex items-center gap-1.5 text-sm text-[color:var(--text-muted)] hover:text-[color:var(--text-primary)] transition-colors">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <button onClick={() => onNavigate('landing')} className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-forest-800 dark:bg-forest-700 flex items-center justify-center">
              <BookMarked style={{ width: 13, height: 13 }} className="text-amber-300" />
            </div>
            <span className="font-bold text-sm text-[color:var(--text-primary)] tracking-tight">ScholarSynth</span>
          </button>
          <div className="flex items-center gap-2">
            <button onClick={() => onNavigate('workspace')} className="btn-primary px-4 py-1.5 text-xs">My Workspace</button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-10">
        <div className="mb-8">
          <div className="relative">
            <Search className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 ${loading ? 'text-amber-500 animate-pulse' : 'text-[color:var(--text-muted)]'}`} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && doSearch(query)}
              placeholder="Search papers by topic, title, keyword, author…"
              className="input-base pl-12 pr-12 py-4 text-base rounded-2xl border-2 focus:ring-4"
            />
            {query && (
              <button onClick={() => setQuery('')} className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-forest-100 dark:hover:bg-dark-card rounded-full">
                <X className="w-4 h-4 text-[color:var(--text-muted)]" />
              </button>
            )}
          </div>

          <div className="flex items-center justify-between mt-3 flex-wrap gap-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-[color:var(--text-muted)] font-medium">Trending:</span>
              {TRENDING_TOPICS.slice(0, 5).map((t) => (
                <button key={t} onClick={() => doSearch(t)}
                  className="text-xs px-2.5 py-1 rounded-full border border-[color:var(--border)] text-[color:var(--text-secondary)] hover:bg-forest-100 hover:border-forest-300 dark:hover:bg-forest-950/40 dark:hover:border-forest-700 transition-colors"
                  style={{ background: 'var(--bg-surface)' }}
                >
                  {t}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border border-[color:var(--border)] ${
                showFilters
                  ? 'bg-forest-100 dark:bg-forest-900/40 text-forest-700 dark:text-forest-400 border-forest-300 dark:border-forest-700'
                  : 'text-[color:var(--text-muted)] hover:bg-forest-50 dark:hover:bg-dark-card'
              }`}
              style={!showFilters ? { background: 'var(--bg-surface)' } : {}}
            >
              <Filter className="w-3.5 h-3.5" /> Filters
            </button>
          </div>

          <AnimatePresence>
            {showFilters && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
                className="mt-3 p-4 rounded-xl border border-[color:var(--border)] grid grid-cols-2 gap-4"
                style={{ background: 'var(--bg-elevated)' }}
              >
                <div>
                  <label className="block text-xs font-semibold text-[color:var(--text-muted)] mb-1">Years back</label>
                  <select
                    value={yearsBack}
                    onChange={(e) => setYearsBack(Number(e.target.value))}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-[color:var(--border)] text-[color:var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-forest-500/30"
                    style={{ background: 'var(--bg-surface)' }}
                  >
                    {[5, 10, 15, 20].map((y) => (
                      <option key={y} value={y}>{y} years</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm text-[color:var(--text-secondary)] cursor-pointer">
                    <input
                      type="checkbox"
                      checked={openAccessOnly}
                      onChange={(e) => setOpenAccessOnly(e.target.checked)}
                      className="rounded border-[color:var(--border)] text-forest-600 focus:ring-forest-500"
                    />
                    Open access only
                  </label>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {error && (
          <div className="mb-6 flex items-start gap-2 px-4 py-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 text-sm text-red-700 dark:text-red-400">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            {error}
          </div>
        )}

        {!searched ? (
          <EmptySearch onTopic={doSearch} />
        ) : (
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div key="sk" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                {[0,1,2].map((i) => (
                  <div key={i} className="card p-6 animate-pulse">
                    <div className="h-4 rounded w-3/4 mb-3" style={{ background: 'var(--border)' }} />
                    <div className="h-3 rounded w-2/5 mb-4" style={{ background: 'var(--bg-elevated)' }} />
                    <div className="h-3 rounded w-full mb-2" style={{ background: 'var(--bg-elevated)' }} />
                    <div className="h-3 rounded w-4/5" style={{ background: 'var(--bg-elevated)' }} />
                  </div>
                ))}
              </motion.div>
            ) : results.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-[color:var(--text-muted)]">No papers found. Try a different query or broaden your filters.</p>
              </div>
            ) : (
              <motion.div key="res" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                <p className="text-sm text-[color:var(--text-muted)] mb-1">
                  <strong className="text-[color:var(--text-secondary)]">{results.length}</strong> results for "<strong className="text-[color:var(--text-primary)]">{query}</strong>"
                </p>
                {results.map((r, i) => (
                  <motion.div key={r.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                    <ResultCard result={r} added={added.has(r.id)} onAdd={() => handleAdd(r)} />
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </main>
    </div>
  );
}

function EmptySearch({ onTopic }: { onTopic: (t: string) => void }) {
  return (
    <div className="text-center py-20">
      <div className="w-20 h-20 rounded-3xl bg-forest-100 dark:bg-forest-900/40 flex items-center justify-center mx-auto mb-5">
        <Search className="w-9 h-9 text-forest-600 dark:text-forest-400" />
      </div>
      <h2 className="text-2xl font-bold text-[color:var(--text-primary)] mb-2">Discover Research Papers</h2>
      <p className="text-sm text-[color:var(--text-muted)] max-w-sm mx-auto mb-8">
        Search Semantic Scholar for relevant papers. Open-access PDFs can be imported directly into your workspace.
      </p>
      <div className="flex flex-wrap gap-2 justify-center">
        {TRENDING_TOPICS.map((t) => (
          <button key={t} onClick={() => onTopic(t)}
            className="px-4 py-2 rounded-xl text-sm font-medium border border-forest-200 dark:border-forest-800 text-forest-700 dark:text-forest-400 hover:bg-forest-100 dark:hover:bg-forest-900/40 transition-colors"
            style={{ background: 'var(--bg-surface)' }}
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}

function ResultCard({ result, added, onAdd }: { result: SearchResult; added: boolean; onAdd: () => void }) {
  const [expanded, setExpanded] = useState(false);
  const canImport = result.isOpenAccess;

  return (
    <Card className="group">
      <div className="flex gap-4">
        <div className="w-11 h-11 rounded-xl bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center shrink-0">
          <FileText className="w-5 h-5 text-forest-600 dark:text-forest-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-3">
            <div className="flex-1 min-w-0">
              <h3 className="text-base font-bold text-[color:var(--text-primary)] group-hover:text-forest-700 dark:group-hover:text-forest-400 transition-colors leading-snug">{result.title}</h3>
              <p className="text-xs text-[color:var(--text-muted)] mt-0.5">{result.authors.slice(0,3).join(', ')}{result.authors.length > 3 ? ` +${result.authors.length-3}` : ''}</p>
            </div>
            <div className="text-right shrink-0">
              <div className="text-base font-extrabold text-forest-700 dark:text-forest-400">{Math.round(result.relevanceScore * 100)}%</div>
              <div className="text-xs text-[color:var(--text-muted)]">match</div>
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5 mt-3">
            {result.year && <Badge variant="muted"><Calendar className="w-3 h-3 mr-1" />{result.year}</Badge>}
            {result.publicationVenue && <Badge variant="muted"><Building2 className="w-3 h-3 mr-1" />{result.publicationVenue}</Badge>}
            {result.isOpenAccess ? <Badge variant="success" dot>Open Access</Badge> : <Badge variant="muted">Paywalled</Badge>}
            {result.tags.slice(0,2).map((t) => <Badge key={t} variant="forest">{t}</Badge>)}
          </div>

          {result.abstract && (
            <>
              <p className={`mt-3 text-sm text-[color:var(--text-secondary)] leading-relaxed ${expanded ? '' : 'line-clamp-2'}`}>{result.abstract}</p>
              <button onClick={() => setExpanded(!expanded)} className="text-xs text-forest-600 dark:text-forest-400 hover:text-forest-800 dark:hover:text-forest-300 mt-1 font-medium">
                {expanded ? 'Show less' : 'Show more'}
              </button>
            </>
          )}

          <div className="flex items-center gap-2 mt-4">
            <button
              onClick={onAdd}
              disabled={added || !canImport}
              title={canImport ? 'Download and index this paper' : 'No open-access PDF available'}
              className={`btn text-xs px-3 py-2 gap-1.5 ${added ? 'btn-secondary opacity-70 cursor-default' : canImport ? 'btn-primary' : 'btn-secondary opacity-50 cursor-not-allowed'}`}
            >
              <BookmarkPlus className="w-3.5 h-3.5" />
              {added ? 'Importing…' : canImport ? 'Add to Workspace' : 'No PDF available'}
            </button>
            {result.url && (
              <a href={result.url} target="_blank" rel="noopener noreferrer" className="btn-secondary text-xs px-3 py-2 gap-1.5">
                <ExternalLink className="w-3.5 h-3.5" /> View
              </a>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
