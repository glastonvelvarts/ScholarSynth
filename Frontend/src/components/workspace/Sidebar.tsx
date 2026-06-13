import React from 'react';
import { motion } from 'framer-motion';
import { BookMarked, Plus, Search, FileText, Home, Settings, HelpCircle } from 'lucide-react';
import { ThemeToggle } from '../ui/ThemeToggle';
import { Badge } from '../ui';
import type { Paper, AppView } from '../../types';

interface SidebarProps {
  papers: Paper[];
  currentView: AppView;
  onNavigate: (v: AppView) => void;
  onNewWorkspace: () => void;
}

export function Sidebar({ papers, currentView, onNavigate, onNewWorkspace }: SidebarProps) {
  const ready = papers.filter((p) => p.processingStatus === 'ready');
  return (
    <aside className="w-60 h-screen border-r border-[color:var(--border)] flex flex-col shrink-0" style={{ background: 'var(--bg-surface)' }}>
      <div className="px-4 py-5 border-b border-[color:var(--border)] flex items-center justify-between">
        <motion.button whileHover={{ scale: 1.02 }} onClick={() => onNavigate('landing')} className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-forest-800 dark:bg-forest-700 flex items-center justify-center">
            <BookMarked style={{ width: 14, height: 14 }} className="text-amber-300" />
          </div>
          <span className="font-bold text-sm text-[color:var(--text-primary)] tracking-tight">ScholarSynth</span>
        </motion.button>
        <ThemeToggle />
      </div>

      <div className="p-3 border-b border-[color:var(--border)]">
        <button onClick={onNewWorkspace} className="w-full btn-primary py-2 text-xs flex items-center justify-center gap-1.5">
          <Plus className="w-3.5 h-3.5" /> New Workspace
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto scrollbar-thin p-3 space-y-0.5">
        <SideNavItem icon={<Home className="w-4 h-4" />} label="Home" active={currentView === 'landing'} onClick={() => onNavigate('landing')} />
        <SideNavItem icon={<Search className="w-4 h-4" />} label="Search Papers" active={currentView === 'search'} onClick={() => onNavigate('search')} />

        <div className="pt-5">
          <div className="flex items-center justify-between px-3 py-1.5 mb-1">
            <span className="text-xs font-bold text-[color:var(--text-muted)] uppercase tracking-widest">Workspace</span>
            <Badge variant="forest">{ready.length}</Badge>
          </div>
          {ready.length === 0 ? (
            <p className="px-3 py-2 text-xs text-[color:var(--text-muted)] italic">No papers yet</p>
          ) : (
            ready.map((p) => (
              <SideNavItem key={p.id} icon={<FileText className="w-3.5 h-3.5" />} label={p.title} active={false} onClick={() => {}} truncate />
            ))
          )}
        </div>
      </nav>

      <div className="border-t border-[color:var(--border)] p-3 space-y-0.5">
        <SideNavItem icon={<Settings className="w-4 h-4" />} label="Settings" active={false} onClick={() => {}} />
        <SideNavItem icon={<HelpCircle className="w-4 h-4" />} label="Help" active={false} onClick={() => {}} />
      </div>
    </aside>
  );
}

function SideNavItem({ icon, label, active, onClick, truncate }: {
  icon: React.ReactNode; label: string; active: boolean; onClick: () => void; truncate?: boolean;
}) {
  return (
    <motion.button
      whileHover={{ x: 2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
        active
          ? 'bg-forest-100 dark:bg-forest-900/50 text-forest-800 dark:text-forest-300 font-semibold'
          : 'text-[color:var(--text-secondary)] hover:bg-forest-50 dark:hover:bg-dark-card'
      }`}
    >
      <span className={active ? 'text-forest-600 dark:text-forest-400' : 'text-[color:var(--text-muted)]'}>{icon}</span>
      <span className={truncate ? 'truncate' : ''}>{label}</span>
    </motion.button>
  );
}
