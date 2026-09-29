import {
  Profile,
  ProfileEmail,
  Education,
  Experience,
  Skill,
  HobbyInterest,
  Hobby,
  Interest,
  AssessmentMeta,
  SessionStartResponse,
  AnswerItem,
  AssessmentResult,
  PersonalitySynthesis,
  TokenResponse,
  User,
  PinStatus,
  PinVerifyResponse,
  DashboardStats,
  ContentRevision,
  AuditEvent
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

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

      throw new Error(errorMessage);
    }

    return res.json() as Promise<T>;
  }

  // --- AUTH ---
  async login(username: string, password: string):Promise<TokenResponse> {
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

  logout() {
    this.setToken(null);
    this.setActivePin(null);
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
    data: { email: string; label?: string; is_primary?: boolean; display_order?: number },
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
  async getSkills(includeHidden = false): Promise<Skill[]> {
    return this.request<Skill[]>(`/skills?include_hidden=${includeHidden}`);
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

  async deleteSkill(id: number, pin?: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(
      `/skills/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  async reorderSkills(items: { id: number; ordering: number }[], pin?: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(
      '/skills/reorder',
      {
        method: 'POST',
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

  async deleteAssessmentResult(id: number, pin?: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(
      `/assessments/results/${id}`,
      { method: 'DELETE' },
      pin
    );
  }

  // --- PERSONALITY SYNTHESIS ---
  async getPersonalitySynthesis(): Promise<PersonalitySynthesis> {
    return this.request<PersonalitySynthesis>('/personality/synthesis');
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
