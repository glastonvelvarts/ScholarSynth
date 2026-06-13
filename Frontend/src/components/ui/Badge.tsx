import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'forest' | 'amber' | 'muted' | 'success';
  className?: string;
  dot?: boolean;
}

export function Badge({ children, variant = 'muted', className = '', dot }: BadgeProps) {
  const styles: Record<string, string> = {
    forest:  'bg-forest-100 text-forest-800 dark:bg-forest-900/60 dark:text-forest-300',
    amber:   'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300',
    muted:   'bg-parchment-200 text-[color:var(--text-secondary)] dark:bg-dark-elevated dark:text-[color:var(--text-muted)]',
    success: 'bg-forest-100 text-forest-700 dark:bg-forest-900/60 dark:text-forest-400',
  };
  const dots: Record<string, string> = {
    forest: 'bg-forest-500', amber: 'bg-amber-400', muted: 'bg-[color:var(--text-muted)]', success: 'bg-forest-500',
  };
  return (
    <span className={`badge px-2 py-0.5 text-xs ${styles[variant]} ${className}`}>
      {dot && <span className={`inline-block w-1.5 h-1.5 rounded-full mr-1.5 ${dots[variant]}`} />}
      {children}
    </span>
  );
}
