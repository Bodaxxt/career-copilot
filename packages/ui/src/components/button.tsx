import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-bold transition-all rounded-lg focus:outline-none focus:ring-2 disabled:opacity-50';
    
    const variants = {
      primary: 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md',
      secondary: 'bg-purple-600 text-white hover:bg-purple-700',
      outline: 'border border-slate-700 text-slate-200 hover:bg-slate-800',
      ghost: 'text-slate-300 hover:bg-slate-800/50',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-5 py-2.5 text-base',
      lg: 'px-7 py-3.5 text-lg',
    };

    return (
      <button
        ref={ref}
        className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';
