import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ children, className = '', hoverable, onClick, padding = 'md' }: CardProps) {
  const pads = { none: '', sm: 'p-3', md: 'p-5', lg: 'p-7' };
  return (
    <motion.div
      whileHover={hoverable ? { y: -2 } : {}}
      onClick={onClick}
      className={`card ${pads[padding]} ${hoverable ? 'card-hover' : ''} ${className}`}
    >
      {children}
    </motion.div>
  );
}
