import React, { useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, X } from 'lucide-react';
import { formatFileSize } from '../../lib/utils';
import { Button } from './Button';

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
}

export function FileUpload({ onFilesSelected, maxFiles = 10 }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState('');

  const addFiles = (incoming: File[]) => {
    setError('');
    const pdfs = incoming.filter((f) => f.type === 'application/pdf');
    if (pdfs.length < incoming.length) setError('Only PDF files accepted');
    const next = [...files, ...pdfs].slice(0, maxFiles);
    if (files.length + pdfs.length > maxFiles) setError(`Max ${maxFiles} files`);
    setFiles(next);
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDragging(false);
    addFiles(Array.from(e.dataTransfer.files));
  }, [files]);

  return (
    <div>
      <div
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-200 ${
          dragging
            ? 'border-forest-500 bg-forest-50 dark:border-forest-500 dark:bg-forest-950/30'
            : 'border-[color:var(--border)] hover:border-forest-400 surface'
        }`}
      >
        <input type="file" accept=".pdf" multiple onChange={(e) => { addFiles(Array.from(e.target.files ?? [])); e.target.value = ''; }}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
        <motion.div animate={{ scale: dragging ? 1.04 : 1 }} className="flex flex-col items-center">
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 ${dragging ? 'bg-forest-100 dark:bg-forest-900/50' : 'bg-parchment-200 dark:bg-dark-elevated'}`}>
            <Upload className={`w-7 h-7 ${dragging ? 'text-forest-600' : 'text-[color:var(--text-muted)]'}`} />
          </div>
          <p className="font-semibold text-[color:var(--text-primary)] mb-1">
            {dragging ? 'Drop your PDFs here' : 'Drag & drop PDF files'}
          </p>
          <p className="text-sm text-[color:var(--text-muted)]">or click to browse — up to {maxFiles} files</p>
        </motion.div>
      </div>

      {error && <p className="mt-2 text-sm text-red-500 dark:text-red-400">{error}</p>}

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mt-4 space-y-2">
            {files.map((f, i) => (
              <motion.div key={`${f.name}-${i}`} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }}
                className="flex items-center gap-3 px-3 py-2.5 surface-elevated rounded-xl border border-[color:var(--border)]">
                <div className="w-9 h-9 rounded-lg bg-forest-100 dark:bg-forest-900/50 flex items-center justify-center shrink-0">
                  <FileText className="w-4 h-4 text-forest-600 dark:text-forest-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[color:var(--text-primary)] truncate">{f.name}</p>
                  <p className="text-xs text-[color:var(--text-muted)]">{formatFileSize(f.size)}</p>
                </div>
                <button onClick={() => setFiles((p) => p.filter((_, idx) => idx !== i))}
                  className="p-1 hover:bg-forest-100 dark:hover:bg-dark-muted rounded-lg transition-colors">
                  <X className="w-4 h-4 text-[color:var(--text-muted)]" />
                </button>
              </motion.div>
            ))}
            <Button variant="primary" className="w-full mt-2" size="lg" onClick={() => onFilesSelected(files)}>
              Analyse {files.length} paper{files.length !== 1 ? 's' : ''}
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
