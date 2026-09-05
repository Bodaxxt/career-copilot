'use client';

import { useState } from 'react';
import { fetchApi } from '../lib/api-client';
import { API_ENDPOINTS } from '@career/shared';

export function useCareerAssessment() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const runAssessment = async (skills: string[], targetRole?: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchApi(API_ENDPOINTS.CAREER_ASSESSMENT, {
        method: 'POST',
        body: JSON.stringify({ skills, target_role: targetRole }),
      });
      setData(result);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to analyze career data');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { runAssessment, loading, data, error };
}
