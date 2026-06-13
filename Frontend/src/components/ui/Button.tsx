import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'amber' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export function Button({
  children, variant = 'primary', size = 'md', isLoading, icon,
  className = '', disabled, ...props
}: ButtonProps) {
  const vs = { primary: 'btn-primary', amber: 'btn-amber', secondary: 'btn-secondary', ghost: 'btn-ghost' };
  const ss = { sm: 'px-3 py-1.5 text-xs gap-1.5', md: 'px-4 py-2.5 text-sm gap-2', lg: 'px-6 py-3 text-base gap-2.5' };
  const off = disabled || isLoading;
  return (
    <motion.button
      whileHover={off ? {} : { scale: 1.02 }}
      whileTap={off ? {} : { scale: 0.97 }}
      className={`${vs[variant]} ${ss[size]} ${off ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      disabled={off}
      {...props}
    >
      {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <>{icon}{children}</>}
    </motion.button>
  );
}
