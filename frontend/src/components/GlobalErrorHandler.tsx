'use client';

import { useEffect } from 'react';
import { setupGlobalErrorHandling } from '@/lib/utils/errorHandler';

export function GlobalErrorHandler() {
  useEffect(() => {
    const cleanup = setupGlobalErrorHandling();
    
    return cleanup;
  }, []);

  return null;
}
