/**
 * TypeScript types for Sales AI Dojo
 */

// User types
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'salesperson' | 'manager' | 'admin';
  company_id: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Company types
export interface Company {
  id: string;
  name: string;
  website?: string;
  created_at: string;
}

// Persona types
export interface Persona {
  id: string;
  company_id: string;
  name: string;
  role: 'decision_maker' | 'influencer' | 'gatekeeper' | 'user';
  personality_traits: Record<string, any>;
  pain_points: string[];
  objections: string[];
  background?: string;
  created_at: string;
}

// Training Session types
export interface TrainingSession {
  id: string;
  user_id: string;
  company_id: string;
  persona_id: string;
  vapi_call_id?: string;
  transcript?: Record<string, any>;
  duration_seconds?: number;
  status: 'ongoing' | 'completed' | 'abandoned';
  created_at: string;
}

export interface StartSessionResponse {
  session_id: string;
  persona_id: string;
  vapi_call_id: string;
  call_url?: string;
}

export interface SessionStats {
  total_sessions: number;
  completed_sessions: number;
  abandoned_sessions: number;
  total_duration_seconds: number;
  average_duration_seconds: number;
  average_score?: number;
}

// Feedback types
export interface CategoryScore {
  category: string;
  score: number;
  feedback: string;
  examples?: string[];
}

export interface Feedback {
  id: string;
  session_id: string;
  overall_score: number;
  strengths: string[];
  areas_for_improvement: string[];
  detailed_analysis: Record<string, any>;
  created_at: string;
}

export interface DetailedFeedback {
  overall_score: number;
  summary: string;
  category_scores: CategoryScore[];
  strengths: string[];
  areas_for_improvement: string[];
  key_moments?: Array<{
    timestamp: string;
    type: 'positive' | 'negative';
    description: string;
  }>;
  recommendations: string[];
}

// Knowledge Base types
export interface KnowledgeBaseEntry {
  id: string;
  company_id: string;
  content: string;
  source_type: 'document' | 'website' | 'manual';
  source_name: string;
  created_at: string;
}

export interface DocumentUploadResponse {
  file_id: string;
  filename: string;
  file_size_bytes: number;
  status: 'success' | 'error';
  message: string;
}

export interface OnboardingStatus {
  company_id: string;
  total_documents: number;
  total_kb_entries: number;
  total_embeddings: number;
  last_updated: string;
  is_ready: boolean;
}

// Dashboard types
export interface DashboardMetrics {
  total_sessions: number;
  average_score: number;
  total_duration_minutes: number;
  top_performers: Array<{
    user_id: string;
    user_name: string;
    average_score: number;
    total_sessions: number;
  }>;
  score_distribution: Record<string, number>;
  sessions_over_time: Array<{
    date: string;
    count: number;
  }>;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  user_name: string;
  average_score: number;
  total_sessions: number;
  best_category: string;
}
