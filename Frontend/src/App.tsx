import React, { useState, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { LandingPage } from './components/LandingPage';
import { Workspace } from './components/workspace/Workspace';
import { SearchPage } from './components/SearchPage';
import type { AppView, SearchResult } from './types';

function App() {
  const [view, setView] = useState<AppView>('landing');
  const [pendingImportIds, setPendingImportIds] = useState<string[]>([]);
  const [pendingImportTitles, setPendingImportTitles] = useState<Record<string, string>>({});

  const handleAddToWorkspace = useCallback((results: SearchResult[]) => {
    const ids = results.map((r) => r.id);
    const titles = Object.fromEntries(results.map((r) => [r.id, r.title]));
    setPendingImportIds((prev) => [...new Set([...prev, ...ids])]);
    setPendingImportTitles((prev) => ({ ...prev, ...titles }));
    setView('workspace');
  }, []);

  const handleImportsHandled = useCallback(() => {
    setPendingImportIds([]);
    setPendingImportTitles({});
  }, []);

  return (
    <AnimatePresence mode="wait">
      {view === 'landing' && (
        <motion.div key="landing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
          <LandingPage onNavigate={setView} />
        </motion.div>
      )}
      {view === 'workspace' && (
        <motion.div key="workspace" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
          <Workspace
            onNavigate={setView}
            pendingImportIds={pendingImportIds}
            pendingImportTitles={pendingImportTitles}
            onImportsHandled={handleImportsHandled}
          />
        </motion.div>
      )}
      {view === 'search' && (
        <motion.div key="search" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
          <SearchPage onNavigate={setView} onAddToWorkspace={handleAddToWorkspace} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default App;
