export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'user' | 'admin';
  createdAt: string;
}

export interface CareerPlan {
  id: string;
  userId: string;
  targetRole: string;
  milestones: string[];
  skillsRequired: string[];
  status: 'draft' | 'active' | 'completed';
}

export interface ResumeAnalysis {
  id: string;
  overallScore: number;
  grammarFeedback: string[];
  keywordsFound: string[];
  suggestedBulletPoints: string[];
}
