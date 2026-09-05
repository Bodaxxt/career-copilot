export const APP_NAME = 'Career Copilot';

export const API_ENDPOINTS = {
  AUTH_VERIFY: '/api/v1/auth/verify',
  CAREER_ASSESSMENT: '/api/v1/assessment',
  RESUME_UPLOAD: '/api/v1/resumes/upload',
  RESUME_ANALYZE: '/api/v1/resumes/analyze',
  HEALTH: '/api/v1/health',
} as const;

export const DEFAULT_PAGINATION = {
  PAGE: 1,
  LIMIT: 20,
} as const;
