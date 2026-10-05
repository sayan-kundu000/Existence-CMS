import {
  Profile,
  ProfileEmail,
  Education,
  Experience,
  Skill,
  SkillRatingLevel,
  HobbyInterest,
  Hobby,
  Interest,
  AssessmentMeta,
  SessionStartResponse,
  AnswerItem,
  AssessmentResult,
  SessionResumeResponse,
  ResultComparisonResponse,
  PersonalitySynthesis,
  TokenResponse,
  User,
  PinStatus,
  PinVerifyResponse,
  DashboardStats,
  ContentRevision,
  AuditEvent,
  ConsolidatedPublicProfile,
  ProfileCompleteness,
  AssessmentDefinition,
  AssessmentQuestion,
  AssessmentStats,
  Project,
  ProjectCreateInput,
  ProjectUpdateInput,
  ProjectLink,
  ProjectTechnology,
  ProjectSkill,
  GitHubExtractionResponse,
  ExtractedProject,
  GitHubAccountLink,
  GitHubAccountLinkInput,
  GitHubSyncResult
} from '../types';

const rawApiUrl = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');
const API_BASE = rawApiUrl ? `${rawApiUrl}/api/v1` : '/api/v1';

class ApiClient {
  private token: string | null = null;
  private activePin: string | null = null;

  constructor() {
    this.token = localStorage.getItem('existence_token');
    this.activePin = sessionStorage.getItem('existence_pin');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('existence_token', token);
    } else {
      localStorage.removeItem('existence_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  setActivePin(pin: string | null) {
    this.activePin = pin;
    if (pin) {
      sessionStorage.setItem('existence_pin', pin);
    } else {
      sessionStorage.removeItem('existence_pin');
    }
  }

  getActivePin(): string | null {
    return this.activePin;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    customPin?: string
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {})
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const pinToUse = customPin || this.activePin || (typeof sessionStorage !== 'undefined' ? sessionStorage.getItem('existence_pin') : null);
    if (pinToUse) {
      headers['X-Action-PIN'] = pinToUse;
    }

    const res = await fetch(url, { ...options, headers });

    if (!res.ok) {
      let errorMessage = 'Request failed';
      try {
        const errorData = await res.json();
        if (errorData.error) {
          const mainMsg = errorData.error.message || 'Operation failed';
          if (errorData.error.details && Array.isArray(errorData.error.details) && errorData.error.details.length > 0) {
            const detailMsgs = errorData.error.details
              .map((d: any) => (d.field ? `${d.field}: ${d.message}` : d.message || JSON.stringify(d)))
              .join('; ');
            errorMessage = `${mainMsg} (${detailMsgs})`;
          } else {
            errorMessage = mainMsg;
          }
        } else if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
          } else {
            errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch {
        errorMessage = `HTTP Error ${res.status}: ${res.statusText}`;
      }

      if (res.status === 401 && endpoint !== '/auth/login' && endpoint !== '/pin/verify') {
        this.setToken(null);
      }
      if (res.status === 423 || (res.status === 401 && endpoint.startsWith('/pin/'))) {
        this.setActivePin(null);
      }

      throw new Error(errorMessage);
    }

    return res.json() as Promise<T>;
  }

  // --- AUTH ---
  async login(username: string, password: string): Promise<TokenResponse> {
    const data = await this.request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setToken(data.access_token);
    return data;
  }

  async register(username: string, email: string, password: string): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password })
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  async logout(): Promise<void> {
    try {
      if (this.token) {
        await this.request<{ success: boolean; message: string }>('/auth/logout', {
          method: 'POST'
        });
      }
    } catch {
      // Clean up client credentials even if network failure occurs
    } finally {
      this.setToken(null);
      this.setActivePin(null);
    }
  }

  async logoutAll(): Promise<void> {
    try {
      if (this.token) {
        await this.request<{ success: boolean; message: string }>('/auth/logout-all', {
          method: 'POST'
        });
      }
    } finally {
      this.setToken(null);
      this.setActivePin(null);
    }
  }

  async lockPin(): Promise<void> {
    try {
      if (this.token) {
        await this.request<PinVerifyResponse>('/pin/lock', {
          method: 'POST'
        });
      }
    } finally {
      this.setActivePin(null);
    }
  }


  // --- PIN ---
  async getPinStatus(): Promise<PinStatus> {
    return this.request<PinStatus>('/pin/status');
  }

  async setupPin(pin: string): Promise<PinVerifyResponse> {
    const res = await this.request<PinVerifyResponse>('/pin/setup', {
      method: 'POST',
      body: JSON.stringify({ pin })
    });
    this.setActivePin(pin);
    return res;
  }

  async verifyPin(pin: string): Promise<PinVerifyResponse> {
    const res = await this.request<PinVerifyResponse>('/pin/verify', {
      method: 'POST',
      body: JSON.stringify({ pin })
    });
    this.setActivePin(pin);
    return res;
  }

  async changePin(current_pin: string, new_pin: string): Promise<PinVerifyResponse> {
    const res = await this.request<PinVerifyResponse>('/pin/change', {
      method: 'POST',
      body: JSON.stringify({ current_pin, new_pin })
    });
    this.setActivePin(new_pin);
    return res;
  }

  // --- PROFILE ---
  async getProfile(): Promise<Profile> {
    return this.request<Profile>('/profile');
  }

  async getConsolidatedPublicProfile(): Promise<ConsolidatedPublicProfile> {
    return this.request<ConsolidatedPublicProfile>('/profile/public');
  }

  async getProfileCompleteness(): Promise<ProfileCompleteness> {
    return this.request<ProfileCompleteness>('/profile/completeness');
  }

  async updateProfile(profile: Partial<Profile>, pin?: string): Promise<Profile> {
    return this.request<Profile>(
      '/profile',
      {
        method: 'PUT',
        body: JSON.stringify(profile)
      },
      pin
    );
  }

  // --- PROFILE EMAILS ---
  async getProfileEmails(): Promise<ProfileEmail[]> {
    return this.request<ProfileEmail[]>('/profile/emails');
  }

  async addProfileEmail(
    data: { email: string; label?: string; is_primary?: boolean; display_order?: number; is_public?: boolean },
    pin?: string
  ): Promise<ProfileEmail> {
    return this.request<ProfileEmail>(
      '/profile/emails',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateProfileEmail(
    id: number,
    data: Partial<ProfileEmail>,
    pin?: string
  ): Promise<ProfileEmail> {
    return this.request<ProfileEmail>(
      `/profile/emails/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async setPrimaryEmail(id: number, pin?: string): Promise<ProfileEmail> {
    return this.request<ProfileEmail>(
      `/profile/emails/${id}/primary`,
      { method: 'POST' },
      pin
    );
  }

  async deleteProfileEmail(id: number, pin?: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(
      `/profile/emails/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  // --- EDUCATION ---
  async getEducation(): Promise<Education[]> {
    return this.request<Education[]>('/education');
  }

  async createEducation(data: Omit<Education, 'id' | 'created_at' | 'updated_at'>, pin?: string): Promise<Education> {
    return this.request<Education>(
      '/education',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateEducation(id: number, data: Partial<Education>, pin?: string): Promise<Education> {
    return this.request<Education>(
      `/education/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async deleteEducation(id: number, pin?: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(
      `/education/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  // --- EXPERIENCE ---
  async getExperience(): Promise<Experience[]> {
    return this.request<Experience[]>('/experience');
  }

  async createExperience(data: Omit<Experience, 'id' | 'created_at' | 'updated_at'>, pin?: string): Promise<Experience> {
    return this.request<Experience>(
      '/experience',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateExperience(id: number, data: Partial<Experience>, pin?: string): Promise<Experience> {
    return this.request<Experience>(
      `/experience/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async deleteExperience(id: number, pin?: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(
      `/experience/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  // --- SKILLS ---
  async getSkillLevels(): Promise<SkillRatingLevel[]> {
    return this.request<SkillRatingLevel[]>('/skills/levels');
  }

  async getSkillCategories(): Promise<string[]> {
    const res = await this.request<{ categories: string[] }>('/skills/categories');
    return res.categories;
  }

  async getSkills(includeHidden = false, category?: string, search?: string, rating?: number, sortBy = 'rating', domain?: string): Promise<Skill[]> {
    const params = new URLSearchParams();
    if (includeHidden) params.set('include_hidden', 'true');
    if (category && category !== 'all') params.set('category', category);
    if (domain && domain !== 'all') params.set('domain', domain);
    if (search && search.trim()) params.set('search', search.trim());
    if (rating && rating >= 1 && rating <= 7) params.set('rating', String(rating));
    if (sortBy) params.set('sort_by', sortBy);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return this.request<Skill[]>(`/skills${qs}`);
  }

  async getSkill(id: number): Promise<Skill> {
    return this.request<Skill>(`/skills/${id}`);
  }

  async createSkill(data: Omit<Skill, 'id' | 'level_label' | 'created_at' | 'updated_at'>, pin?: string): Promise<Skill> {
    return this.request<Skill>(
      '/skills',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateSkill(id: number, data: Partial<Skill>, pin?: string): Promise<Skill> {
    return this.request<Skill>(
      `/skills/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async patchSkill(id: number, data: Partial<Skill>, pin?: string): Promise<Skill> {
    return this.request<Skill>(
      `/skills/${id}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async deleteSkill(id: number, pin?: string): Promise<{ success: boolean; message?: string }> {
    return this.request<{ success: boolean; message?: string }>(
      `/skills/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  async reorderSkills(items: { id: number; ordering: number }[], pin?: string): Promise<{ success: boolean; message?: string }> {
    return this.request<{ success: boolean; message?: string }>(
      '/skills/reorder',
      {
        method: 'PATCH',
        body: JSON.stringify(items)
      },
      pin
    );
  }

  // --- HOBBIES & INTERESTS ---
  async getHobbiesInterests(type?: 'hobby' | 'interest'): Promise<HobbyInterest[]> {
    const query = type ? `?item_type=${type}` : '';
    return this.request<HobbyInterest[]>(`/hobbies-interests${query}`);
  }

  async getHobbies(includeHidden = false): Promise<Hobby[]> {
    return this.request<Hobby[]>(`/hobbies?include_hidden=${includeHidden}`);
  }

  async getInterests(includeHidden = false): Promise<Interest[]> {
    return this.request<Interest[]>(`/interests?include_hidden=${includeHidden}`);
  }

  async createHobbyInterest(data: Omit<HobbyInterest, 'id' | 'created_at' | 'updated_at'>, pin?: string): Promise<HobbyInterest> {
    return this.request<HobbyInterest>(
      '/hobbies-interests',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateHobbyInterest(id: number, data: Partial<HobbyInterest>, pin?: string): Promise<HobbyInterest> {
    return this.request<HobbyInterest>(
      `/hobbies-interests/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async deleteHobbyInterest(id: number, pin?: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(
      `/hobbies-interests/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  // --- ASSESSMENTS ---
  async getAssessmentRegistry(): Promise<AssessmentMeta[]> {
    return this.request<AssessmentMeta[]>('/assessments/registry');
  }

  async startAssessment(assessment_type: string): Promise<SessionStartResponse> {
    return this.request<SessionStartResponse>('/assessments/start', {
      method: 'POST',
      body: JSON.stringify({ assessment_type })
    });
  }

  async submitAssessment(session_id: string, answers: AnswerItem[]): Promise<AssessmentResult> {
    return this.request<AssessmentResult>('/assessments/submit', {
      method: 'POST',
      body: JSON.stringify({ session_id, answers })
    });
  }

  async getAssessmentResult(session_id: string): Promise<AssessmentResult> {
    return this.request<AssessmentResult>(`/assessments/results/${session_id}`);
  }

  async getAssessmentHistory(): Promise<AssessmentResult[]> {
    return this.request<AssessmentResult[]>('/assessments/history');
  }

  async resumeAssessmentSession(sessionId: string): Promise<SessionResumeResponse> {
    return this.request<SessionResumeResponse>(`/personality/sessions/${sessionId}/resume`);
  }

  async updateAssessmentProgress(sessionId: string, progressIndex: number): Promise<{ success: boolean; progress_index: number }> {
    return this.request<{ success: boolean; progress_index: number }>(`/personality/sessions/${sessionId}/progress`, {
      method: 'PATCH',
      body: JSON.stringify({ progress_index: progressIndex })
    });
  }

  async saveAssessmentResponses(sessionId: string, responses: AnswerItem[]): Promise<{ success: boolean; saved_count: number }> {
    return this.request<{ success: boolean; saved_count: number }>(`/personality/sessions/${sessionId}/responses`, {
      method: 'POST',
      body: JSON.stringify({ responses })
    });
  }

  async toggleResultVisibility(resultId: number, isPublic: boolean, pin?: string): Promise<AssessmentResult> {
    return this.request<AssessmentResult>(
      `/personality/results/${resultId}/visibility`,
      {
        method: 'PATCH',
        body: JSON.stringify({ is_public: isPublic })
      },
      pin
    );
  }

  async compareAssessmentResults(baselineSessionId: string, targetSessionId: string): Promise<ResultComparisonResponse> {
    return this.request<ResultComparisonResponse>(
      `/personality/compare?baseline_session_id=${baselineSessionId}&target_session_id=${targetSessionId}`
    );
  }

  async getPublicPersonality(): Promise<PersonalitySynthesis> {
    return this.request<PersonalitySynthesis>('/personality/public');
  }

  async deleteAssessmentResult(id: number, pin?: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(
      `/personality/results/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  // --- PERSONALITY SYNTHESIS ---
  async getPersonalitySynthesis(): Promise<PersonalitySynthesis> {
    return this.request<PersonalitySynthesis>('/personality/synthesis');
  }

  async refreshPersonalitySynthesis(): Promise<PersonalitySynthesis> {
    return this.request<PersonalitySynthesis>('/personality/synthesis/refresh', {
      method: 'POST'
    });
  }

  async updatePersonalitySynthesis(
    data: { key_soft_skills: string[]; key_strengths: string[]; key_weaknesses: string[]; summary_notes?: string },
    pin?: string
  ): Promise<PersonalitySynthesis> {
    return this.request<PersonalitySynthesis>(
      '/personality/synthesis',
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  // --- ADMINISTRATIVE ASSESSMENT & QUESTION MANAGEMENT ---
  async getAssessmentStats(): Promise<AssessmentStats> {
    return this.request<AssessmentStats>('/personality/admin/stats');
  }

  async getAssessmentDefinitions(): Promise<AssessmentDefinition[]> {
    return this.request<AssessmentDefinition[]>('/personality/admin/definitions');
  }

  async createAssessmentDefinition(
    data: { code: string; name: string; version: string; tagline?: string; description?: string; question_count?: number; estimated_minutes?: number; status?: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' },
    pin?: string
  ): Promise<AssessmentDefinition> {
    return this.request<AssessmentDefinition>(
      '/personality/admin/definitions',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateDefinitionStatus(id: number, status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED', pin?: string): Promise<AssessmentDefinition> {
    return this.request<AssessmentDefinition>(
      `/personality/admin/definitions/${id}/status`,
      {
        method: 'PATCH',
        body: JSON.stringify({ status })
      },
      pin
    );
  }

  async getDefinitionQuestions(definitionId: number): Promise<AssessmentQuestion[]> {
    return this.request<AssessmentQuestion[]>(`/personality/admin/definitions/${definitionId}/questions`);
  }

  async createAssessmentQuestion(
    data: { id: string; assessment_definition_id?: number; definition_type: string; dimension: string; question_text: string; positive_pole?: string; negative_pole?: string; scale_type?: string; question_order?: number; scoring_configuration?: string },
    pin?: string
  ): Promise<AssessmentQuestion> {
    return this.request<AssessmentQuestion>(
      '/personality/admin/questions',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateAssessmentQuestion(
    questionId: string,
    data: Partial<AssessmentQuestion>,
    pin?: string
  ): Promise<AssessmentQuestion> {
    return this.request<AssessmentQuestion>(
      `/personality/admin/questions/${questionId}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async toggleAssessmentQuestion(questionId: string, pin?: string): Promise<AssessmentQuestion> {
    return this.request<AssessmentQuestion>(
      `/personality/admin/questions/${questionId}/toggle`,
      {
        method: 'PATCH'
      },
      pin
    );
  }


  // --- Projects Engine ---
  async getProjectCategories(): Promise<{ statuses: string[]; link_types: string[]; tech_categories: string[] }> {
    return this.request<{ statuses: string[]; link_types: string[]; tech_categories: string[] }>('/projects/categories');
  }

  async getProjects(
    includeHidden = false,
    options: {
      search?: string;
      status?: string;
      technology?: string;
      is_featured?: boolean;
      sort_by?: string;
    } = {}
  ): Promise<Project[]> {
    const params = new URLSearchParams();
    if (includeHidden) params.append('include_hidden', 'true');
    if (options.search) params.append('search', options.search);
    if (options.status) params.append('status', options.status);
    if (options.technology) params.append('technology', options.technology);
    if (options.is_featured !== undefined) params.append('is_featured', String(options.is_featured));
    if (options.sort_by) params.append('sort_by', options.sort_by);

    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<Project[]>(`/projects${query}`);
  }

  async getProject(projectId: number, includeHidden = false): Promise<Project> {
    const query = includeHidden ? '?include_hidden=true' : '';
    return this.request<Project>(`/projects/${projectId}${query}`);
  }

  async createProject(data: ProjectCreateInput | Partial<Project>, pin?: string): Promise<Project> {
    return this.request<Project>(
      '/projects',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateProject(projectId: number, data: ProjectUpdateInput | Partial<Project>, pin?: string): Promise<Project> {
    return this.request<Project>(
      `/projects/${projectId}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async patchProject(projectId: number, data: ProjectUpdateInput | Partial<Project>, pin?: string): Promise<Project> {
    return this.request<Project>(
      `/projects/${projectId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async deleteProject(projectId: number, pin?: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(
      `/projects/${projectId}`,
      {
        method: 'DELETE'
      },
      pin
    );
  }

  async reorderProjects(items: { id: number; display_order: number }[], pin?: string): Promise<Project[]> {
    return this.request<Project[]>(
      '/projects/reorder',
      {
        method: 'PATCH',
        body: JSON.stringify(items)
      },
      pin
    );
  }

  async addProjectLink(projectId: number, data: Partial<ProjectLink>, pin?: string): Promise<ProjectLink> {
    return this.request<ProjectLink>(
      `/projects/${projectId}/links`,
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async updateProjectLink(projectId: number, linkId: number, data: Partial<ProjectLink>, pin?: string): Promise<ProjectLink> {
    return this.request<ProjectLink>(
      `/projects/${projectId}/links/${linkId}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async patchProjectLink(projectId: number, linkId: number, data: Partial<ProjectLink>, pin?: string): Promise<ProjectLink> {
    return this.request<ProjectLink>(
      `/projects/${projectId}/links/${linkId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data)
      },
      pin
    );
  }

  async deleteProjectLink(projectId: number, linkId: number, pin?: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(
      `/projects/${projectId}/links/${linkId}`,
      {
        method: 'DELETE'
      },
      pin
    );
  }

  async reorderProjectLinks(projectId: number, items: { id: number; display_order: number }[], pin?: string): Promise<ProjectLink[]> {
    return this.request<ProjectLink[]>(
      `/projects/${projectId}/links/reorder`,
      {
        method: 'PATCH',
        body: JSON.stringify(items)
      },
      pin
    );
  }

  async extractGithubProjects(
    githubUrl: string,
    customToken?: string
  ): Promise<GitHubExtractionResponse> {
    return this.request<GitHubExtractionResponse>('/projects/extract-github', {
      method: 'POST',
      body: JSON.stringify({
        github_url: githubUrl,
        custom_token: customToken?.trim() || undefined
      })
    });
  }

  async generateAiDossier(data: {
    name: string;
    raw_description?: string;
    language?: string;
    technologies?: (string | { name: string; category?: string })[];
    topics?: string[];
    links?: { label: string; url: string; link_type?: string; is_primary?: boolean }[];
    stars?: number;
    forks?: number;
  }): Promise<{ short_description: string; description: string }> {
    return this.request<{ short_description: string; description: string }>('/projects/generate-ai-dossier', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async bulkImportProjects(
    projects: ProjectCreateInput[],
    pin?: string
  ): Promise<Project[]> {
    return this.request<Project[]>('/projects/bulk-import', {
      method: 'POST',
      body: JSON.stringify({ projects })
    }, pin);
  }

  async getGithubLink(pin?: string): Promise<GitHubAccountLink | null> {
    return this.request<GitHubAccountLink | null>('/projects/github-link', {}, pin);
  }

  async saveGithubLink(data: GitHubAccountLinkInput, pin?: string): Promise<GitHubAccountLink> {
    return this.request<GitHubAccountLink>('/projects/github-link', {
      method: 'POST',
      body: JSON.stringify(data)
    }, pin);
  }

  async unlinkGithubAccount(pin?: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('/projects/github-link', {
      method: 'DELETE'
    }, pin);
  }

  async syncGithubProjects(githubUrl?: string, pin?: string): Promise<GitHubSyncResult> {
    const query = githubUrl ? `?github_url=${encodeURIComponent(githubUrl)}` : '';
    return this.request<GitHubSyncResult>(`/projects/sync-github${query}`, {
      method: 'POST'
    }, pin);
  }



  // --- CMS ---
  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>('/cms/dashboard');
  }

  async getAuditEvents(limit = 50): Promise<AuditEvent[]> {
    return this.request<AuditEvent[]>(`/audit/events?limit=${limit}`);
  }

  async getContentRevisions(limit = 50): Promise<ContentRevision[]> {
    return this.request<ContentRevision[]>(`/audit/revisions?limit=${limit}`);
  }

  async restoreContentRevision(revisionId: string | number, pin?: string): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(
      `/audit/revisions/${revisionId}/restore`,
      { method: 'POST' },
      pin
    );
  }
}

export const api = new ApiClient();
