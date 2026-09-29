export interface ProfileEmail {
  id: number;
  profile_id: number;
  email: string;
  label: string;
  is_primary: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface Profile {
  id: number;
  name: string | null;
  email_ids: string[];
  emails?: ProfileEmail[] | null;
  mobile_number: string | null;
  linkedin: string | null;
  about: string | null;
  is_empty: boolean;
  created_at: string;
  updated_at: string;
}

export type EducationLevel =
  | "Doctorate"
  | "Post Graduate"
  | "Graduate"
  | "Undergraduate"
  | "High School"
  | "Matriculation";

export interface Education {
  id: number;
  level: EducationLevel;
  stream: string;
  institution?: string | null;
  starting_month_year: string;
  ending_month_year: string | null;
  currently_studying: boolean;
  ordering: number;
  created_at: string;
  updated_at: string;
}

export type WorkMode = "On-site" | "Remote" | "Hybrid";

export interface Experience {
  id: number;
  role: string;
  employer: string;
  work_mode: WorkMode;
  location: string | null;
  starting_month_year: string;
  ending_month_year: string | null;
  currently_working: boolean;
  ordering: number;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: number;
  name: string;
  category: string;
  rating: number; // 1 to 7
  level_label: string; // Beginner, Novice, Intermediate, Proficient, Advanced, Expert, Master
  visibility: boolean;
  ordering: number;
  metadata_info: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface HobbyInterest {
  id: number;
  type: "hobby" | "interest";
  name: string;
  category: string | null;
  icon: string | null;
  ordering: number;
  created_at: string;
  updated_at: string;
}

export interface Hobby {
  id: number;
  name: string;
  category: string | null;
  icon: string | null;
  visibility: boolean;
  ordering: number;
  created_at: string;
  updated_at: string;
}

export interface Interest {
  id: number;
  name: string;
  category: string | null;
  icon: string | null;
  visibility: boolean;
  ordering: number;
  created_at: string;
  updated_at: string;
}

export type PublicTabType =
  | 'home'
  | 'about'
  | 'education'
  | 'experience'
  | 'skills'
  | 'personality'
  | 'interests'
  | 'contact';

export type AssessmentType = "MBTI" | "DISC" | "BIG_FIVE";

export interface AssessmentMeta {
  type: AssessmentType;
  name: string;
  tagline: string;
  dimensions: string[];
  question_count: number;
  estimated_minutes: number;
  description: string;
}

export interface QuestionItem {
  id: string;
  dimension: string;
  text: string;
  positive_pole?: string | null;
  negative_pole?: string | null;
  scale_type: string;
}

export interface SessionStartResponse {
  session_id: string;
  assessment_type: AssessmentType;
  total_questions: number;
  questions: QuestionItem[];
  started_at: string;
}

export interface AnswerItem {
  question_id: string;
  dimension: string;
  selected_value: number;
}

export interface AssessmentResult {
  id: number;
  session_id: string;
  assessment_type: AssessmentType;
  result_code: string;
  result_title: string;
  summary: string | null;
  scores: Record<string, any>;
  soft_skills: string[];
  strengths: string[];
  weaknesses: string[];
  completed_at: string;
}

export interface PersonalitySynthesis {
  has_assessments: boolean;
  key_soft_skills: string[];
  key_strengths: string[];
  key_weaknesses: string[];
  summary_notes: string | null;
  assessments_completed: string[];
  latest_results: {
    MBTI: AssessmentResult | null;
    DISC: AssessmentResult | null;
    BIG_FIVE: AssessmentResult | null;
  };
  updated_at: string | null;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  pin_configured: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: number;
  username: string;
  role: string;
  pin_configured: boolean;
}

export interface PinStatus {
  is_configured: boolean;
  is_locked: boolean;
  attempts_remaining: number;
  locked_until: string | null;
  last_verified_at: string | null;
}

export interface PinVerifyResponse {
  success: boolean;
  message: string;
  pin_token?: string | null;
}

export interface DashboardStats {
  profile_configured: boolean;
  education_count: number;
  experience_count: number;
  skills_count: number;
  hobbies_interests_count: number;
  hobbies_count?: number;
  interests_count?: number;
  assessments_completed: number;
  pin_configured: boolean;
  revisions_count?: number;
  last_audit_event: string | null;
}

export interface ContentRevision {
  id: number;
  revision_id: string;
  entity_name: string;
  entity_id: string | null;
  action: string;
  editor_username: string;
  change_summary: string | null;
  previous_snapshot: any | null;
  current_snapshot: any | null;
  created_at: string;
}

export interface AuditEvent {
  id: number;
  event_type: string;
  username: string | null;
  status: string;
  details: Record<string, any> | null;
  ip_address: string | null;
  timestamp: string;
}
