export interface ProfileEmail {
  id: number;
  profile_id: number;
  email: string;
  label: string;
  is_primary: boolean;
  is_public: boolean;
  display_order: number;
  assessments_reset?: boolean;
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
  assessments_reset?: boolean;
  created_at: string;
  updated_at: string;
}

export type EducationLevel =
  | "Doctorate"
  | "Post Graduate"
  | "Graduate"
  | "Diploma"
  | "Undergraduate"
  | "High School"
  | "Matriculation";

export type EducationScoreType = "Percentage" | "CGPA 10" | "CGPA 5";

export interface Education {
  id: number;
  level: EducationLevel;
  stream: string | null;
  institution?: string | null;
  starting_month_year: string;
  ending_month_year: string | null;
  currently_studying: boolean;
  score_type?: EducationScoreType | null;
  score_value?: number | null;
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

export interface SkillRatingLevel {
  rating: number;
  level: string;
  description: string;
  display_order: number;
}

export const SKILL_CATEGORIES = [
  'Technical',
  'Financial',
  'Analytical',
  'Business',
  'Leadership',
  'Management',
  'Diplomatic',
  'Creative',
  'Research',
  'Medical',
  'Legal',
  'Psychological',
  'Scientific',
  'Educational',
  'Environmental',
  'Operational',
  'Ethical',
] as const;

export type SkillCategory = (typeof SKILL_CATEGORIES)[number];

export interface Skill {
  id: number;
  profile_id?: number | null;
  name: string;
  domain?: string | null;
  domains?: string[];
  category: string;
  categories?: string[];
  description?: string | null;
  rating: number; // 1 to 7
  level_label: string; // Beginner, Novice, Intermediate, Proficient, Advanced, Expert, Master
  level?: string;
  visibility: boolean;
  is_visible?: boolean;
  ordering: number;
  display_order?: number;
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

export type ProjectStatus = 'Planned' | 'In Progress' | 'Completed' | 'Archived';

export type ProjectLinkType =
  | 'Live Demo'
  | 'Deployment'
  | 'GitHub'
  | 'Repository'
  | 'Documentation'
  | 'API'
  | 'Video Demo'
  | 'Case Study'
  | 'Other';

export type TechCategory =
  | 'Programming Language'
  | 'Framework'
  | 'Database'
  | 'Cloud/Deployment'
  | 'Frontend'
  | 'Backend'
  | 'DevOps'
  | 'Testing'
  | 'Data/AI'
  | 'Other';

export interface ProjectTechnology {
  id: number;
  technology_id: number;
  name: string;
  category: string;
  display_order: number;
}

export interface ProjectLink {
  id: number;
  project_id: number;
  label: string;
  url: string;
  link_type: ProjectLinkType;
  is_primary: boolean;
  is_visible: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectSkill {
  id: number;
  name: string;
  category: string;
  rating: number;
  level_label: string;
}

export interface Project {
  id: number;
  profile_id?: number | null;
  name: string;
  short_description?: string | null;
  description?: string | null;
  status?: ProjectStatus;
  start_month?: number | null;
  start_year?: number | null;
  end_month?: number | null;
  end_year?: number | null;
  is_current: boolean;
  is_featured: boolean;
  is_visible: boolean;
  visibility?: boolean;
  display_order: number;
  ordering?: number;
  technologies: ProjectTechnology[];
  links: ProjectLink[];
  skills?: ProjectSkill[];
  primary_link?: ProjectLink | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectTechnologyInput {
  name: string;
  category?: string;
  display_order?: number;
}

export interface ProjectLinkInput {
  label: string;
  url: string;
  link_type: ProjectLinkType;
  is_primary?: boolean;
  is_visible?: boolean;
  display_order?: number;
}

export interface ProjectCreateInput {
  name: string;
  short_description?: string | null;
  description?: string | null;
  status?: ProjectStatus;
  start_month?: number | null;
  start_year?: number | null;
  end_month?: number | null;
  end_year?: number | null;
  is_ongoing?: boolean;
  is_current?: boolean;
  is_featured?: boolean;
  is_visible?: boolean;
  visibility?: boolean;
  display_order?: number;
  ordering?: number;
  technologies?: ProjectTechnologyInput[];
  links?: ProjectLinkInput[];
  skill_ids?: number[];
}

export type ProjectUpdateInput = Partial<ProjectCreateInput>;

export interface ExtractedProjectLink {
  label: string;
  url: string;
  link_type: ProjectLinkType;
  is_primary: boolean;
  is_visible?: boolean;
  display_order?: number;
}

export interface ExtractedTechnology {
  name: string;
  category: string;
}

export interface ExtractedProject {
  name: string;
  short_description?: string | null;
  description?: string | null;
  full_ai_dossier?: string | null;
  status: ProjectStatus;
  technologies: ExtractedTechnology[];
  links: ExtractedProjectLink[];
  stars: number;
  forks: number;
  repo_url: string;
  homepage_url?: string | null;
  is_featured: boolean;
  start_month?: number | null;
  start_year?: number | null;
  end_month?: number | null;
  end_year?: number | null;
}

export interface GitHubExtractionResponse {
  username: string;
  source_type: 'user' | 'repo';
  projects_count: number;
  projects: ExtractedProject[];
}

export interface GitHubAccountLink {
  id: number;
  profile_id: number;
  github_url: string;
  username: string;
  auto_sync: boolean;
  webhook_secret?: string | null;
  last_synced_at?: string | null;
  last_sync_status: 'idle' | 'syncing' | 'success' | 'error';
  last_sync_summary?: string | null;
  created_at: string;
  updated_at: string;
}

export interface GitHubAccountLinkInput {
  github_url: string;
  custom_token?: string | null;
  auto_sync?: boolean;
  webhook_secret?: string | null;
}

export interface GitHubSyncResult {
  status: string;
  message: string;
  username: string;
  total_found: number;
  created_count: number;
  updated_count: number;
  created_projects: string[];
  updated_projects: string[];
  synced_at: string;
}


export type PublicTabType =
  | 'home'
  | 'about'
  | 'education'
  | 'experience'
  | 'skills'
  | 'projects'
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
  result_version?: string;
  is_public?: boolean;
  summary: string | null;
  scores: Record<string, any>;
  soft_skills: string[];
  strengths: string[];
  weaknesses: string[];
  completed_at: string;
}

export interface SessionResumeResponse {
  session_id: string;
  assessment_type: AssessmentType;
  assessment_version: string;
  status: string;
  progress_index: number;
  total_questions: number;
  answered_count: number;
  answers: Record<string, number>;
  questions: QuestionItem[];
  started_at: string;
}

export interface DimensionComparison {
  dimension: string;
  baseline_score: number;
  target_score: number;
  delta: number;
  direction: 'INCREASED' | 'DECREASED' | 'UNCHANGED';
  interpretation: string;
}

export interface ResultComparisonResponse {
  assessment_type: AssessmentType;
  baseline_session_id: string;
  target_session_id: string;
  baseline_result_code: string;
  target_result_code: string;
  baseline_completed_at: string;
  target_completed_at: string;
  dimensions_comparison: DimensionComparison[];
  summary: string;
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

export interface AssessmentDefinition {
  id: number;
  code: string;
  name: string;
  version: string;
  tagline: string | null;
  description: string | null;
  is_active: boolean;
  question_count: number;
  estimated_minutes: number;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  created_at: string;
  updated_at: string;
}

export interface AssessmentQuestion {
  id: string;
  assessment_definition_id: number | null;
  definition_type: string | null;
  question_key: string | null;
  dimension: string;
  question_text: string;
  positive_pole: string | null;
  negative_pole: string | null;
  scale_type: string;
  question_order: number;
  is_active: boolean;
  scoring_configuration: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssessmentStats {
  total_sessions: number;
  completed_sessions: number;
  in_progress_sessions: number;
  total_results: number;
  public_results: number;
  private_results: number;
  models: Record<string, {
    total_sessions: number;
    completed_sessions: number;
    total_results: number;
    public_results: number;
    completion_rate: number;
  }>;
}


export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  pin_configured: boolean;
  permissions?: string[];
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
  permissions?: string[];
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
  projects_count?: number;
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

export interface ProfileCompleteness {
  score_percentage: number;
  dimensions_completed: number;
  dimensions_total: number;
  breakdown: Record<string, boolean>;
}

export interface ConsolidatedPublicProfile {
  profile: Profile;
  education: Education[];
  experience: Experience[];
  hobbies: Hobby[];
  interests: Interest[];
  skills: Skill[];
  projects?: Project[];
  personality: PersonalitySynthesis | null;
}
