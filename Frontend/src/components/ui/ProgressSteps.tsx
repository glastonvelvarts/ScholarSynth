import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import type { ProcessingStatus } from '../../types';

interface Step { id: ProcessingStatus; label: string; description: string; }

export function ProgressSteps({ steps, currentStep }: { steps: Step[]; currentStep: ProcessingStatus }) {
  const ci = steps.findIndex((s) => s.id === currentStep);
  return (
    <div className="space-y-3">
      {steps.map((step, i) => {
        const done = i < ci;
        const active = step.id === currentStep;
        return (
          <motion.div key={step.id} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
            className={`flex items-start gap-3 ${i > ci ? 'opacity-30' : ''}`}>
            <div className="mt-0.5 shrink-0">
              {done ? (
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 480 }}>
                  <CheckCircle2 className="w-5 h-5 text-forest-500" />
                </motion.div>
              ) : active ? (
                <Loader2 className="w-5 h-5 text-amber-500 animate-spin" />
              ) : (
                <Circle className="w-5 h-5 text-[color:var(--border)]" />
              )}
            </div>
            <div>
              <p className={`text-sm font-medium ${done ? 'text-[color:var(--text-secondary)]' : active ? 'text-amber-600 dark:text-amber-400' : 'text-[color:var(--text-muted)]'}`}>{step.label}</p>
              <p className="text-xs text-[color:var(--text-muted)]">{step.description}</p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
