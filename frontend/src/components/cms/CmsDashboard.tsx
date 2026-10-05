import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  User,
  GraduationCap,
  Briefcase,
  Sparkles,
  Heart,
  Compass,
  Brain,
  KeyRound,
  History,
  Shield,
  Plus,
  Trash2,
  Edit2,
  Save,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Clock,
  ArrowUpDown,
  RotateCcw,
  Eye,
  EyeOff,
  Mail,
  Phone,
  Link,
  MapPin,
  Calendar,
  Award,
  Search,
  Filter,
  Check,
  X,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  FolderCode
} from 'lucide-react';
import {
  Profile,
  ProfileEmail,
  Education,
  Experience,
  Skill,
  Project,
  HobbyInterest,
  PersonalitySynthesis,
  DashboardStats,
  ContentRevision,
  AuditEvent,
  AssessmentResult,
  AssessmentDefinition,
  AssessmentStats
} from '../../types';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { PinModal } from '../common/PinModal';
import { MonthYearPicker } from '../common/MonthYearPicker';
import { SkillRatingSelector } from '../skills/SkillRatingSelector';
import { SkillCard } from '../skills/SkillCard';
import { SkillCategorySelector } from '../skills/SkillCategorySelector';
import { SkillDomainSelector } from '../skills/SkillDomainSelector';
import { CmsProjectsSection } from './CmsProjectsSection';
import {
  calculateExperienceDuration,
  calculateOverallExperience,
  sortExperiencesByTimelineDesc
} from '../../utils/dateHelpers';

interface CmsDashboardProps {
  onRefreshAll: () => void;
  onOpenLogin: () => void;
}

export type CmsTab =
  | 'stats'
  | 'profile'
  | 'education'
  | 'experience'
  | 'skills'
  | 'projects'
  | 'hobbies'
  | 'interests'
  | 'personality'
  | 'revisions'
  | 'audit'
  | 'pin';

const SKILL_LEVEL_MAP: Record<number, string> = {
  1: 'Beginner',
  2: 'Novice',
  3: 'Intermediate',
  4: 'Proficient',
  5: 'Advanced',
  6: 'Expert',
  7: 'Master'
};

export const CmsDashboard: React.FC<CmsDashboardProps> = ({ onRefreshAll, onOpenLogin }) => {
  const { isAuthenticated, user, pinStatus, activePin, setActivePin } = useAuth();

  const [activeTab, setActiveTab] = useState<CmsTab>('stats');

  // Core Data
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [profileEmails, setProfileEmails] = useState<ProfileEmail[]>([]);
  const [educations, setEducations] = useState<Education[]>([]);
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [hobbiesInterests, setHobbiesInterests] = useState<HobbyInterest[]>([]);
  const [synthesis, setSynthesis] = useState<PersonalitySynthesis | null>(null);
  const [assessmentHistory, setAssessmentHistory] = useState<AssessmentResult[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [revisions, setRevisions] = useState<ContentRevision[]>([]);
  const [assessmentDefinitions, setAssessmentDefinitions] = useState<AssessmentDefinition[]>([]);
  const [assessmentStats, setAssessmentStats] = useState<AssessmentStats | null>(null);

  // UI States
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'warning'; text: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedRevision, setSelectedRevision] = useState<ContentRevision | null>(null);
  const [auditFilter, setAuditFilter] = useState<string>('ALL');

  // PIN security modal trigger for sensitive changes
  const [pinModalOpen, setPinModalOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<(() => Promise<void>) | null>(null);

  // Form: Profile
  const [profileForm, setProfileForm] = useState({
    name: '',
    mobile_number: '',
    linkedin: '',
    about: ''
  });

  // Form: Profile Email
  const [emailForm, setEmailForm] = useState({
    email: '',
    label: 'Primary',
    is_primary: false,
    is_public: true,
    display_order: 0
  });
  const [editingEmailId, setEditingEmailId] = useState<number | null>(null);

  // Form: Education
  const [eduForm, setEduForm] = useState<{
    id?: number;
    level: string;
    stream: string;
    institution: string;
    starting_month_year: string;
    ending_month_year: string;
    currently_studying: boolean;
    score_type: 'Percentage' | 'CGPA 10' | 'CGPA 5' | '';
    score_value: string;
    ordering: number;
  }>({
    level: 'Graduate',
    stream: '',
    institution: '',
    starting_month_year: 'Jan 2020',
    ending_month_year: 'Jun 2024',
    currently_studying: false,
    score_type: '',
    score_value: '',
    ordering: 0
  });
  const [editingEduId, setEditingEduId] = useState<number | null>(null);

  // Form: Experience
  const [expForm, setExpForm] = useState<{
    id?: number;
    role: string;
    employer: string;
    work_mode: 'On-site' | 'Remote' | 'Hybrid';
    location: string;
    starting_month_year: string;
    ending_month_year: string;
    currently_working: boolean;
    ordering: number;
  }>({
    role: '',
    employer: '',
    work_mode: 'On-site',
    location: '',
    starting_month_year: 'Jan 2022',
    ending_month_year: 'Dec 2024',
    currently_working: false,
    ordering: 0
  });
  const [editingExpId, setEditingExpId] = useState<number | null>(null);

  // Form: Skill
  const [skillForm, setSkillForm] = useState<{
    id?: number;
    name: string;
    domain: string;
    domains: string[];
    category: string;
    categories: string[];
    description: string;
    rating: number;
    visibility: boolean;
    ordering: number;
  }>({
    name: '',
    domain: '',
    domains: [],
    category: 'Technical',
    categories: ['Technical'],
    description: '',
    rating: 4,
    visibility: true,
    ordering: 0
  });
  const [editingSkillId, setEditingSkillId] = useState<number | null>(null);

  // Form: Hobby / Interest
  const [hiForm, setHiForm] = useState<{
    id?: number;
    type: 'hobby' | 'interest';
    name: string;
    category: string;
    icon: string;
  }>({
    type: 'hobby',
    name: '',
    category: '',
    icon: ''
  });
  const [editingHiId, setEditingHiId] = useState<number | null>(null);

  // Form: PIN change
  const [pinChangeForm, setPinChangeForm] = useState({ currentPin: '', newPin: '', confirmNewPin: '' });

  useEffect(() => {
    if (isAuthenticated) {
      loadAllCmsData();
    }
  }, [isAuthenticated]);

  const loadAllCmsData = async () => {
    try {
      const [st, prof, emails, edus, exps, sks, projs, his, syn, hist, evs, revs, defs, aStats] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getProfile().catch(() => null),
        api.getProfileEmails().catch(() => []),
        api.getEducation().catch(() => []),
        api.getExperience().catch(() => []),
        api.getSkills(true).catch(() => []),
        api.getProjects(true).catch(() => []),
        api.getHobbiesInterests().catch(() => []),
        api.getPersonalitySynthesis().catch(() => null),
        api.getAssessmentHistory().catch(() => []),
        api.getAuditEvents(50).catch(() => []),
        api.getContentRevisions(50).catch(() => []),
        api.getAssessmentDefinitions().catch(() => []),
        api.getAssessmentStats().catch(() => null)
      ]);

      if (st) setStats(st);
      if (prof) {
        setProfile(prof);
        setProfileForm({
          name: prof.name || '',
          mobile_number: prof.mobile_number || '',
          linkedin: prof.linkedin || '',
          about: prof.about || ''
        });
      }
      setProfileEmails(emails);
      const sortedSks = [...(sks || [])].sort((a, b) => {
        if (b.rating !== a.rating) return b.rating - a.rating;
        const orderA = a.ordering ?? a.display_order ?? 0;
        const orderB = b.ordering ?? b.display_order ?? 0;
        if (orderA !== orderB) return orderA - orderB;
        return a.name.localeCompare(b.name);
      });
      setSkills(sortedSks);
      setHobbiesInterests(his);
      if (syn) {
        setSynthesis(syn);
      }
      setAssessmentHistory(hist);
      setAuditEvents(evs);
      setRevisions(revs);
      setAssessmentDefinitions(defs);
      if (aStats) setAssessmentStats(aStats);
    } catch (e: any) {
      console.error('Failed to load CMS data', e);
    }
  };

  const notify = (type: 'success' | 'error' | 'warning', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), type === 'warning' ? 7000 : 4000);
  };

  // Safe executor checking for active PIN session
  const executeWithPin = async (action: () => Promise<void>) => {
    const pinToUse = activePin || api.getActivePin() || (typeof sessionStorage !== 'undefined' ? sessionStorage.getItem('existence_pin') : null);
    if (pinToUse) {
      try {
        api.setActivePin(pinToUse);
        await action();
      } catch (err: any) {
        notify('error', err.message);
      }
    } else {
      setPendingAction(() => action);
      setPinModalOpen(true);
    }
  };

  const handlePinVerified = async (pin: string) => {
    api.setActivePin(pin);
    setActivePin(pin);
    if (pendingAction) {
      try {
        await pendingAction();
      } catch (err: any) {
        notify('error', err.message);
      } finally {
        setPendingAction(null);
      }
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto py-16 px-4 text-center">
        <div className="p-8 rounded-3xl glass-panel border border-slate-800 shadow-2xl">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4">
            <Shield className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">CMS Authorization Required</h2>
          <p className="text-xs text-slate-400 mb-6">
            The Custom Content Management System is protected. Sign in with administrative credentials to access editing controls.
          </p>
          <button
            onClick={onOpenLogin}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
          >
            Authenticate Admin
          </button>
        </div>
      </div>
    );
  }

  // --- ACTIONS ---

  // 1. Profile Actions
  const handleSaveProfile = () => {
    executeWithPin(async () => {
      setLoading(true);
      try {
        const updated = await api.updateProfile({
          name: profileForm.name.trim() || null,
          mobile_number: profileForm.mobile_number.trim() || null,
          linkedin: profileForm.linkedin.trim() || null,
          about: profileForm.about.trim() || null
        });
        setProfile(updated);
        if (updated.assessments_reset) {
          localStorage.removeItem('existence_saved_session');
          notify('warning', 'Admin contact details (mobile / LinkedIn / email) changed. In accordance with policy, all assessment results have been reset and you must retake all assessments.');
        } else {
          notify('success', 'Profile coordinates updated successfully.');
        }
        onRefreshAll();
        loadAllCmsData();
      } finally {
        setLoading(false);
      }
    });
  };

  // 2. Email Actions
  const handleSaveEmail = (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailForm.email || !emailForm.email.includes('@')) {
      notify('error', 'Please enter a valid email address.');
      return;
    }
    executeWithPin(async () => {
      setLoading(true);
      try {
        let emailRes: ProfileEmail;
        if (editingEmailId) {
          emailRes = await api.updateProfileEmail(editingEmailId, {
            email: emailForm.email.trim(),
            label: emailForm.label.trim(),
            is_primary: emailForm.is_primary,
            is_public: emailForm.is_public,
            display_order: Number(emailForm.display_order)
          });
        } else {
          emailRes = await api.addProfileEmail({
            email: emailForm.email.trim(),
            label: emailForm.label.trim(),
            is_primary: emailForm.is_primary,
            is_public: emailForm.is_public,
            display_order: Number(emailForm.display_order)
          });
        }
        if (emailRes?.assessments_reset) {
          localStorage.removeItem('existence_saved_session');
          notify('warning', 'Admin email changed. All assessment results have been reset and must be retaken.');
        } else {
          notify('success', editingEmailId ? 'Profile email updated.' : 'New profile email registered.');
        }
        setEditingEmailId(null);
        setEmailForm({ email: '', label: 'Personal', is_primary: false, is_public: true, display_order: 0 });
        loadAllCmsData();
        onRefreshAll();
      } finally {
        setLoading(false);
      }
    });
  };

  const handleDeleteEmail = (id: number, emailAddr: string) => {
    if (!confirm(`Are you sure you want to delete ${emailAddr}?`)) return;
    executeWithPin(async () => {
      const res: any = await api.deleteProfileEmail(id);
      if (res?.assessments_reset) {
        localStorage.removeItem('existence_saved_session');
        notify('warning', `Deleted ${emailAddr}. Admin email changed: all assessment results have been reset and must be retaken.`);
      } else {
        notify('success', `Deleted ${emailAddr}.`);
      }
      loadAllCmsData();
      onRefreshAll();
    });
  };

  const handleSetPrimaryEmail = (emailItem: ProfileEmail) => {
    executeWithPin(async () => {
      const res: any = await api.setPrimaryEmail(emailItem.id);
      if (res?.assessments_reset) {
        localStorage.removeItem('existence_saved_session');
        notify('warning', `${emailItem.email} set as primary. Admin primary email changed: all assessment results have been reset and must be retaken.`);
      } else {
        notify('success', `${emailItem.email} set as primary.`);
      }
      loadAllCmsData();
      onRefreshAll();
    });
  };

  // 3. Education Actions
  const handleSaveEducation = () => {
    const isStreamLocked = eduForm.level === 'High School' || eduForm.level === 'Matriculation';
    if (!isStreamLocked && (!eduForm.stream || !eduForm.stream.trim())) {
      notify('error', 'Stream / Field of study is required.');
      return;
    }
    const startStr = eduForm.starting_month_year?.trim() || 'Jan 2020';
    let endStr: string | null = eduForm.ending_month_year?.trim() || null;
    let scoreTypeVal: 'Percentage' | 'CGPA 10' | 'CGPA 5' | null = null;
    let scoreNumVal: number | null = null;

    if (eduForm.currently_studying) {
      endStr = null;
      scoreTypeVal = null;
      scoreNumVal = null;
    } else {
      if (!endStr) {
        notify('error', 'Ending Month & Year is required when not currently studying.');
        return;
      }
      const rawType = eduForm.score_type?.trim();
      const rawVal = eduForm.score_value !== '' && eduForm.score_value !== undefined ? String(eduForm.score_value).trim() : '';

      if (rawType && !rawVal) {
        notify('error', 'Please enter marks number for the selected score category.');
        return;
      }
      if (!rawType && rawVal) {
        notify('error', 'Please select a score category (Percentage, CGPA 10, or CGPA 5).');
        return;
      }
      if (rawType && rawVal) {
        const parsed = parseFloat(rawVal);
        if (isNaN(parsed)) {
          notify('error', 'Please enter a valid numeric value for marks.');
          return;
        }
        if (rawVal.includes('.')) {
          const decDigits = rawVal.split('.')[1];
          if (decDigits.length > 2) {
            notify('error', 'Marks number can have at most 2 decimal places.');
            return;
          }
        }
        if (rawType === 'Percentage') {
          if (parsed < 0 || parsed > 100) {
            notify('error', 'Percentage marks must be between 0 and 100.');
            return;
          }
        } else if (rawType === 'CGPA 10') {
          if (parsed < 0 || parsed > 10) {
            notify('error', 'CGPA 10 marks must be between 0 and 10.');
            return;
          }
        } else if (rawType === 'CGPA 5') {
          if (parsed < 0 || parsed > 5) {
            notify('error', 'CGPA 5 marks must be between 0 and 5.');
            return;
          }
        }
        scoreTypeVal = rawType as 'Percentage' | 'CGPA 10' | 'CGPA 5';
        scoreNumVal = Math.round(parsed * 100) / 100;
      }
    }

    executeWithPin(async () => {
      setLoading(true);
      try {
        const payload = {
          level: eduForm.level as any,
          stream: isStreamLocked ? null : (eduForm.stream.trim() || null),
          institution: eduForm.institution?.trim() || null,
          starting_month_year: startStr,
          ending_month_year: endStr,
          currently_studying: eduForm.currently_studying,
          score_type: scoreTypeVal,
          score_value: scoreNumVal,
          ordering: Number(eduForm.ordering) || 0
        };

        if (editingEduId) {
          await api.updateEducation(editingEduId, payload);
          notify('success', 'Academic record updated successfully.');
        } else {
          await api.createEducation(payload);
          notify('success', 'Academic record registered successfully.');
        }
        setEditingEduId(null);
        setEduForm({
          level: 'Graduate',
          stream: '',
          institution: '',
          starting_month_year: 'Jan 2020',
          ending_month_year: 'Jun 2024',
          currently_studying: false,
          score_type: '',
          score_value: '',
          ordering: 0
        });
        loadAllCmsData();
        onRefreshAll();
      } finally {
        setLoading(false);
      }
    });
  };

  const handleDeleteEducation = (id: number) => {
    if (!confirm('Are you sure you want to delete this education record?')) return;
    executeWithPin(async () => {
      await api.deleteEducation(id);
      notify('success', 'Education record deleted.');
      loadAllCmsData();
      onRefreshAll();
    });
  };

  // 4. Experience Actions
  const handleSaveExperience = () => {
    if (!expForm.role || !expForm.role.trim()) {
      notify('error', 'Role / Designation is required.');
      return;
    }
    if (!expForm.employer || !expForm.employer.trim()) {
      notify('error', 'Employer / Organization is required.');
      return;
    }
    let loc = expForm.location?.trim() || '';
    if (expForm.work_mode === 'Remote') {
      loc = 'Remote';
    } else if (!loc) {
      notify('error', `Location is required when work mode is ${expForm.work_mode}.`);
      return;
    }
    const startStr = expForm.starting_month_year?.trim() || 'Jan 2022';
    let endStr: string | null = expForm.ending_month_year?.trim() || null;
    if (expForm.currently_working) {
      endStr = null;
    } else if (!endStr) {
      notify('error', 'Ending Month & Year is required when not currently working.');
      return;
    }

    executeWithPin(async () => {
      setLoading(true);
      try {
        if (editingExpId) {
          await api.updateExperience(editingExpId, {
            role: expForm.role.trim(),
            employer: expForm.employer.trim(),
            work_mode: expForm.work_mode,
            location: loc,
            starting_month_year: startStr,
            ending_month_year: endStr,
            currently_working: expForm.currently_working,
            ordering: Number(expForm.ordering) || 0
          });
          notify('success', 'Work experience record updated successfully.');
        } else {
          await api.createExperience({
            role: expForm.role.trim(),
            employer: expForm.employer.trim(),
            work_mode: expForm.work_mode,
            location: loc,
            starting_month_year: startStr,
            ending_month_year: endStr,
            currently_working: expForm.currently_working,
            ordering: Number(expForm.ordering) || 0
          });
          notify('success', 'Work experience record created successfully.');
        }
        setEditingExpId(null);
        setExpForm({
          role: '',
          employer: '',
          work_mode: 'On-site',
          location: '',
          starting_month_year: 'Jan 2022',
          ending_month_year: 'Dec 2024',
          currently_working: false,
          ordering: 0
        });
        loadAllCmsData();
        onRefreshAll();
      } finally {
        setLoading(false);
      }
    });
  };

  const handleDeleteExperience = (id: number) => {
    if (!confirm('Are you sure you want to delete this experience record?')) return;
    executeWithPin(async () => {
      await api.deleteExperience(id);
      notify('success', 'Experience record deleted.');
      loadAllCmsData();
      onRefreshAll();
    });
  };

  // 5. Skill Actions
  const handleSaveSkill = () => {
    const trimmedName = skillForm.name.trim();
    if (!trimmedName) {
      notify('error', 'Skill name is required.');
      return;
    }

    const finalDomains = skillForm.domains && skillForm.domains.length > 0
      ? skillForm.domains
      : (skillForm.domain ? skillForm.domain.split(',').map((d) => d.trim()).filter(Boolean) : []);
    const domainStr = finalDomains.length > 0 ? finalDomains.join(', ') : undefined;
    const ratingNum = Math.max(1, Math.min(7, Number(skillForm.rating) || 4));

    const finalCategories = skillForm.categories && skillForm.categories.length > 0
      ? skillForm.categories
      : (skillForm.category ? skillForm.category.split(',').map((c) => c.trim()).filter(Boolean) : ['Technical']);
    const categoryStr = finalCategories.join(', ');

    // Support bulk add if comma-separated names are provided (when creating new skills)
    if (!editingSkillId && trimmedName.includes(',')) {
      const names = trimmedName
        .split(/[,&]/)
        .map((n) => n.trim())
        .filter(Boolean);

      if (names.length > 1) {
        executeWithPin(async () => {
          setLoading(true);
          try {
            let createdCount = 0;
            for (const singleName of names) {
              const duplicate = skills.find(
                (s) => s.name.trim().toLowerCase() === singleName.toLowerCase()
              );
              if (!duplicate) {
                await api.createSkill({
                  name: singleName,
                  domain: domainStr,
                  domains: finalDomains,
                  category: categoryStr,
                  categories: finalCategories,
                  description: skillForm.description.trim() || undefined,
                  rating: ratingNum,
                  visibility: skillForm.visibility,
                  ordering: Number(skillForm.ordering) || 0,
                  metadata_info: domainStr ? { domain: domainStr, domains: finalDomains } : {}
                });
                createdCount++;
              }
            }
            notify('success', `Created ${createdCount} skills under domain "${domainStr || 'General'}".`);
            setSkillForm({
              name: '',
              domain: domainStr || '',
              domains: finalDomains,
              category: 'Technical',
              categories: ['Technical'],
              description: '',
              rating: 4,
              visibility: true,
              ordering: 0
            });
            loadAllCmsData();
            onRefreshAll();
          } catch (err: any) {
            notify('error', err?.message || 'Failed to save skills.');
          } finally {
            setLoading(false);
          }
        });
        return;
      }
    }

    if (trimmedName.length > 100) {
      notify('error', 'Skill name cannot exceed 100 characters.');
      return;
    }

    // Client-side duplicate check
    const duplicate = skills.find(
      (s) => s.id !== editingSkillId && s.name.trim().toLowerCase() === trimmedName.toLowerCase()
    );
    if (duplicate) {
      notify('error', `A skill named "${trimmedName}" already exists.`);
      return;
    }

    executeWithPin(async () => {
      setLoading(true);
      try {
        if (editingSkillId) {
          await api.updateSkill(editingSkillId, {
            name: trimmedName,
            domain: domainStr,
            domains: finalDomains,
            category: categoryStr,
            categories: finalCategories,
            description: skillForm.description.trim() || undefined,
            rating: ratingNum,
            visibility: skillForm.visibility,
            ordering: Number(skillForm.ordering) || 0,
            metadata_info: domainStr ? { domain: domainStr, domains: finalDomains } : {}
          });
          notify('success', 'Skill updated successfully.');
        } else {
          await api.createSkill({
            name: trimmedName,
            domain: domainStr,
            domains: finalDomains,
            category: categoryStr,
            categories: finalCategories,
            description: skillForm.description.trim() || undefined,
            rating: ratingNum,
            visibility: skillForm.visibility,
            ordering: Number(skillForm.ordering) || 0,
            metadata_info: domainStr ? { domain: domainStr, domains: finalDomains } : {}
          });
          notify('success', 'Skill created successfully.');
        }
        setEditingSkillId(null);
        setSkillForm({
          name: '',
          domain: domainStr || '',
          domains: finalDomains,
          category: 'Technical',
          categories: ['Technical'],
          description: '',
          rating: 4,
          visibility: true,
          ordering: 0
        });
        loadAllCmsData();
        onRefreshAll();
      } catch (err: any) {
        notify('error', err?.message || 'Failed to save skill.');
      } finally {
        setLoading(false);
      }
    });
  };

  const handleToggleSkillVisibility = (skill: Skill) => {
    const currentVis = skill.visibility ?? skill.is_visible ?? true;
    executeWithPin(async () => {
      setLoading(true);
      try {
        await api.patchSkill(skill.id, { visibility: !currentVis });
        notify('success', `Skill "${skill.name}" is now ${!currentVis ? 'visible' : 'hidden'}.`);
        loadAllCmsData();
        onRefreshAll();
      } catch (err: any) {
        notify('error', err?.message || 'Failed to toggle visibility.');
      } finally {
        setLoading(false);
      }
    });
  };

  const handleMoveSkill = (index: number, direction: 'up' | 'down') => {
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= skills.length) return;

    const newSkills = [...skills];
    const temp = newSkills[index];
    newSkills[index] = newSkills[targetIndex];
    newSkills[targetIndex] = temp;

    const reorderPayload = newSkills.map((s, idx) => ({
      id: s.id,
      ordering: idx + 1
    }));

    executeWithPin(async () => {
      setLoading(true);
      try {
        await api.reorderSkills(reorderPayload);
        notify('success', 'Skills reordered successfully.');
        loadAllCmsData();
        onRefreshAll();
      } catch (err: any) {
        notify('error', err?.message || 'Failed to reorder skills.');
      } finally {
        setLoading(false);
      }
    });
  };

  const handleDeleteSkill = (id: number) => {
    if (!confirm('Are you sure you want to delete this skill?')) return;
    executeWithPin(async () => {
      setLoading(true);
      try {
        await api.deleteSkill(id);
        notify('success', 'Skill deleted successfully.');
        loadAllCmsData();
        onRefreshAll();
      } catch (err: any) {
        notify('error', err?.message || 'Failed to delete skill.');
      } finally {
        setLoading(false);
      }
    });
  };

  // 6. Hobby / Interest Actions
  const handleSaveHi = (type: 'hobby' | 'interest') => {
    executeWithPin(async () => {
      setLoading(true);
      try {
        if (editingHiId) {
          await api.updateHobbyInterest(editingHiId, {
            type,
            name: hiForm.name,
            category: hiForm.category || null,
            icon: hiForm.icon || null
          });
          notify('success', `${type === 'hobby' ? 'Hobby' : 'Interest'} updated.`);
        } else {
          await api.createHobbyInterest({
            type,
            name: hiForm.name,
            category: hiForm.category || null,
            icon: hiForm.icon || null,
            ordering: 0
          });
          notify('success', `${type === 'hobby' ? 'Hobby' : 'Interest'} created.`);
        }
        setEditingHiId(null);
        setHiForm({ type, name: '', category: '', icon: '' });
        loadAllCmsData();
        onRefreshAll();
      } finally {
        setLoading(false);
      }
    });
  };

  const handleDeleteHi = (id: number, typeName: string) => {
    if (!confirm(`Are you sure you want to delete this ${typeName}?`)) return;
    executeWithPin(async () => {
      await api.deleteHobbyInterest(id);
      notify('success', `${typeName} deleted.`);
      loadAllCmsData();
      onRefreshAll();
    });
  };

  // 7. Personality Synthesis Refresh (Test-Governed)
  const handleRefreshSynthesis = async () => {
    setLoading(true);
    try {
      const syn = await api.refreshPersonalitySynthesis();
      setSynthesis(syn);
      const testCount = syn.assessments_completed?.length || 0;
      notify('success', `Personality synthesis re-evaluated on the basis of ${testCount} completed assessment${testCount !== 1 ? 's' : ''}.`);
      loadAllCmsData();
      onRefreshAll();
    } catch (err: any) {
      notify('error', err.message);
    } finally {
      setLoading(false);
    }
  };

  // 7b. Toggle Assessment Result Visibility
  const handleToggleResultVisibility = (resultId: number, currentPublic: boolean) => {
    executeWithPin(async () => {
      setLoading(true);
      try {
        await api.toggleResultVisibility(resultId, !currentPublic);
        notify('success', `Result visibility updated to ${!currentPublic ? 'Public' : 'Private'}`);
        loadAllCmsData();
        onRefreshAll();
      } catch (err: any) {
        notify('error', err.message);
      } finally {
        setLoading(false);
      }
    });
  };

  // 7c. Delete Assessment Result
  const handleDeleteAssessmentResult = (resultId: number) => {
    if (!confirm('Are you sure you want to delete this completed assessment record? This will purge underlying responses and recalculate synthesis. PIN verification is required.')) return;
    executeWithPin(async () => {
      setLoading(true);
      try {
        await api.deleteAssessmentResult(resultId);
        notify('success', 'Assessment result deleted and synthesis refreshed.');
        loadAllCmsData();
        onRefreshAll();
      } catch (err: any) {
        notify('error', err.message);
      } finally {
        setLoading(false);
      }
    });
  };

  // 7d. Toggle Definition Status
  const handleToggleDefinitionStatus = (defId: number, currentStatus: string) => {
    const nextStatus = currentStatus === 'PUBLISHED' ? 'ARCHIVED' : 'PUBLISHED';
    executeWithPin(async () => {
      setLoading(true);
      try {
        await api.updateDefinitionStatus(defId, nextStatus);
        notify('success', `Assessment definition status updated to ${nextStatus}.`);
        loadAllCmsData();
        onRefreshAll();
      } catch (err: any) {
        notify('error', err.message);
      } finally {
        setLoading(false);
      }
    });
  };


  // 8. Restore Revision Action
  const handleRestoreRevision = (rev: ContentRevision) => {
    if (!confirm(`Restore ${rev.entity_name} revision ${rev.revision_id}? This will overwrite current live content.`)) return;
    executeWithPin(async () => {
      setLoading(true);
      try {
        const res = await api.restoreContentRevision(rev.id);
        notify('success', res.message || `Successfully restored ${rev.entity_name} revision.`);
        setSelectedRevision(null);
        loadAllCmsData();
        onRefreshAll();
      } finally {
        setLoading(false);
      }
    });
  };

  // 9. PIN Change Action
  const handleChangePin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pinChangeForm.newPin !== pinChangeForm.confirmNewPin) {
      notify('error', 'New PIN confirmation does not match.');
      return;
    }
    try {
      await api.changePin(pinChangeForm.currentPin, pinChangeForm.newPin);
      notify('success', 'Security PIN successfully updated.');
      setPinChangeForm({ currentPin: '', newPin: '', confirmNewPin: '' });
      loadAllCmsData();
    } catch (err: any) {
      notify('error', err.message);
    }
  };

  const hobbiesList = hobbiesInterests.filter((h) => h.type === 'hobby');
  const interestsList = hobbiesInterests.filter((h) => h.type === 'interest');

  const filteredAuditEvents = auditFilter === 'ALL'
    ? auditEvents
    : auditEvents.filter((ev) => ev.event_type.includes(auditFilter));

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 space-y-8 animate-fadeIn">
      {/* CMS Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <span className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl">
              <LayoutDashboard className="w-6 h-6" />
            </span>
            Existence Custom CMS
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Authenticated Administration, PIN-Protected Content Mutation, and Versioning Audits.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {activePin ? (
            <div className="flex items-center gap-2">
              <span className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> PIN Session Active
              </span>
              <button
                onClick={() => setActivePin(null)}
                className="p-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 text-xs transition-colors cursor-pointer"
                title="Lock PIN session"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setPinModalOpen(true)}
              className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs font-semibold text-amber-300 hover:bg-amber-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <KeyRound className="w-4 h-4" /> Unlock PIN Session
            </button>
          )}
        </div>
      </div>

      {/* Alert banner */}
      {message && (
        <div
          className={`flex items-center gap-2.5 p-4 rounded-2xl text-xs font-medium border animate-fadeIn ${
            message.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-200'
              : message.type === 'warning'
              ? 'bg-amber-950/40 border-amber-800 text-amber-200'
              : 'bg-rose-950/40 border-rose-800 text-rose-200'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : message.type === 'warning' ? (
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* CMS Navigation Tabs (12 Tabs) */}
      <div className="flex items-center gap-1 bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 overflow-x-auto scrollbar-none">
        {[
          { id: 'stats', label: 'Dashboard', icon: LayoutDashboard },
          { id: 'profile', label: 'Profile & Emails', icon: User },
          { id: 'education', label: 'Education', icon: GraduationCap },
          { id: 'experience', label: 'Experience', icon: Briefcase },
          { id: 'skills', label: 'Skills (7-L)', icon: Sparkles },
          { id: 'projects', label: 'Projects', icon: FolderCode },
          { id: 'hobbies', label: 'Hobbies', icon: Heart },
          { id: 'interests', label: 'Interests', icon: Compass },
          { id: 'personality', label: 'Personality', icon: Brain },
          { id: 'revisions', label: 'Revisions', icon: RotateCcw },
          { id: 'audit', label: 'Audit Log', icon: History },
          { id: 'pin', label: 'Security & PIN', icon: KeyRound }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as CmsTab)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* 1. DASHBOARD OVERVIEW */}
      {activeTab === 'stats' && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-4">
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Profile</span>
              <p className={`text-base font-bold mt-1 ${stats.profile_configured ? 'text-emerald-400' : 'text-amber-400'}`}>
                {stats.profile_configured ? 'Populated' : 'Empty'}
              </p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Education</span>
              <p className="text-lg font-bold text-white mt-1 font-mono">{stats.education_count}</p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Experience</span>
              <p className="text-lg font-bold text-white mt-1 font-mono">{stats.experience_count}</p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Skills</span>
              <p className="text-lg font-bold text-white mt-1 font-mono">{stats.skills_count}</p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Projects</span>
              <p className="text-lg font-bold text-white mt-1 font-mono">{stats.projects_count ?? projects.length}</p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Hobbies</span>
              <p className="text-lg font-bold text-white mt-1 font-mono">{stats.hobbies_count ?? hobbiesList.length}</p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Interests</span>
              <p className="text-lg font-bold text-white mt-1 font-mono">{stats.interests_count ?? interestsList.length}</p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Revisions</span>
              <p className="text-lg font-bold text-white mt-1 font-mono">{stats.revisions_count ?? revisions.length}</p>
            </div>
            <div className="glass-card p-4 rounded-2xl border border-slate-800">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">PIN Status</span>
              <p className={`text-base font-bold mt-1 ${stats.pin_configured ? 'text-emerald-400' : 'text-rose-400'}`}>
                {stats.pin_configured ? 'Active' : 'Missing'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Revisions */}
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <RotateCcw className="w-4 h-4 text-indigo-400" />
                  Recent Content Revisions
                </h3>
                <button
                  onClick={() => setActiveTab('revisions')}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  View all ({revisions.length})
                </button>
              </div>
              <div className="space-y-2.5">
                {revisions.slice(0, 4).map((rev) => (
                  <div key={rev.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-indigo-300 uppercase text-[10px]">{rev.entity_name}</span>
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-slate-900 border border-slate-800 text-slate-400">
                          {rev.action}
                        </span>
                      </div>
                      <p className="text-slate-300 mt-1 line-clamp-1">{rev.change_summary || 'Content updated'}</p>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(rev.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
                {revisions.length === 0 && (
                  <p className="text-xs text-slate-500 py-4 text-center">No content revisions recorded yet.</p>
                )}
              </div>
            </div>

            {/* Recent Security Events */}
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  Recent Security Events
                </h3>
                <button
                  onClick={() => setActiveTab('audit')}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  View audit log ({auditEvents.length})
                </button>
              </div>
              <div className="space-y-2.5">
                {auditEvents.slice(0, 4).map((ev) => (
                  <div key={ev.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-200 text-[11px]">{ev.event_type}</span>
                        <span className={`text-[10px] font-bold ${ev.status === 'SUCCESS' ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {ev.status}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono">Actor: {ev.username || 'system'}</span>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(ev.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
                {auditEvents.length === 0 && (
                  <p className="text-xs text-slate-500 py-4 text-center">No security audit events recorded yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. PROFILE & EMAILS TAB */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Basic Coordinates */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-lg font-bold text-white">Profile Coordinates & Bio</h2>
                <p className="text-xs text-slate-400">Manage public identity, mobile, and bio narrative.</p>
              </div>
              <button
                onClick={handleSaveProfile}
                disabled={loading}
                className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all cursor-pointer"
              >
                <Save className="w-3.5 h-3.5" />
                <span>{loading ? 'Saving...' : 'Save Profile'}</span>
              </button>
            </div>

            <div className="space-y-4">
              {/* Admin Assessment Integrity Rule Alert */}
              <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-3">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div className="text-xs text-amber-200/90 leading-relaxed">
                  <strong className="text-amber-300 font-semibold block mb-0.5">Admin Assessment Integrity Rule</strong>
                  All psychometric assessment tests (MBTI, DISC, Big Five — 75 items each) are strictly calibrated for the platform administrator. If your <strong>Email ID</strong>, <strong>Mobile number</strong>, or <strong>LinkedIn account</strong> is changed, all assessment test results are automatically invalidated and reset, and you must take all assessment tests again.
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
                <input
                  type="text"
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                  placeholder="e.g. Elena Rostova"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Mobile Number</label>
                <input
                  type="text"
                  value={profileForm.mobile_number}
                  onChange={(e) => setProfileForm({ ...profileForm, mobile_number: e.target.value })}
                  placeholder="+1 (555) 0199"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">LinkedIn URL</label>
                <input
                  type="text"
                  value={profileForm.linkedin}
                  onChange={(e) => setProfileForm({ ...profileForm, linkedin: e.target.value })}
                  placeholder="https://linkedin.com/in/username"
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">About Narrative / Bio</label>
                <textarea
                  rows={6}
                  value={profileForm.about}
                  onChange={(e) => setProfileForm({ ...profileForm, about: e.target.value })}
                  placeholder="Compose executive overview..."
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-600 outline-none focus:border-indigo-500 resize-none font-sans"
                />
              </div>
            </div>
          </div>

          {/* Relational Email Management */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
            <div className="pb-4 border-b border-slate-800">
              <h2 className="text-lg font-bold text-white">Relational Email Management</h2>
              <p className="text-xs text-slate-400">Add, edit, or designate primary addresses for this profile.</p>
            </div>

            {/* Email Assessment Notice */}
            <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-200/90 leading-relaxed">
                <strong>Admin Notice:</strong> Adding, updating, deleting, or changing the primary email address resets all admin psychometric test results, requiring all assessments to be taken again.
              </p>
            </div>

            {/* Email Form */}
            <form onSubmit={handleSaveEmail} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                {editingEmailId ? 'Edit Email Address' : 'Add New Email Address'}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">Email Address</label>
                  <input
                    type="email"
                    required
                    value={emailForm.email}
                    onChange={(e) => setEmailForm({ ...emailForm, email: e.target.value })}
                    placeholder="name@domain.com"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">Label</label>
                  <input
                    type="text"
                    value={emailForm.label}
                    onChange={(e) => setEmailForm({ ...emailForm, label: e.target.value })}
                    placeholder="e.g. Work, Personal, Academic"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="is_primary"
                      checked={emailForm.is_primary}
                      onChange={(e) => setEmailForm({ ...emailForm, is_primary: e.target.checked })}
                      className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-800"
                    />
                    <label htmlFor="is_primary" className="text-xs text-slate-300 cursor-pointer">
                      Primary Contact Email
                    </label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="is_public"
                      checked={emailForm.is_public}
                      onChange={(e) => setEmailForm({ ...emailForm, is_public: e.target.checked })}
                      className="w-4 h-4 rounded text-emerald-600 bg-slate-900 border-slate-800"
                    />
                    <label htmlFor="is_public" className="text-xs text-slate-300 cursor-pointer">
                      Public Portfolio Visible
                    </label>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {editingEmailId && (
                    <button
                      type="button"
                      onClick={() => {
                        setEditingEmailId(null);
                        setEmailForm({ email: '', label: 'Personal', is_primary: false, is_public: true, display_order: 0 });
                      }}
                      className="px-3 py-1.5 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs cursor-pointer"
                    >
                      Cancel
                    </button>
                  )}
                  <button
                    type="submit"
                    className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold cursor-pointer shadow-md"
                  >
                    {editingEmailId ? 'Update Email' : 'Add Email'}
                  </button>
                </div>
              </div>
            </form>

            {/* Email List */}
            <div className="space-y-2.5">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Configured Addresses ({profileEmails.length})
              </h3>
              {profileEmails.map((item) => (
                <div
                  key={item.id}
                  className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between"
                >
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-bold text-white font-mono">{item.email}</span>
                      {item.is_primary && (
                        <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/30 text-[10px] font-semibold text-indigo-300">
                          Primary
                        </span>
                      )}
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold ${item.is_public ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-900 text-slate-500 border border-slate-800'}`}>
                        {item.is_public ? 'Public' : 'Private'}
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-slate-900 text-[10px] text-slate-400 font-mono">
                        {item.label}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {!item.is_primary && (
                      <button
                        onClick={() => handleSetPrimaryEmail(item)}
                        className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-[11px] text-slate-300 font-medium cursor-pointer"
                      >
                        Make Primary
                      </button>
                    )}
                    <button
                      onClick={() => {
                        setEditingEmailId(item.id);
                        setEmailForm({
                          email: item.email,
                          label: item.label,
                          is_primary: item.is_primary,
                          is_public: item.is_public ?? true,
                          display_order: item.display_order
                        });
                      }}
                      className="p-1.5 text-slate-400 hover:text-white rounded-lg cursor-pointer"
                      title="Edit"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDeleteEmail(item.id, item.email)}
                      className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg cursor-pointer"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
              {profileEmails.length === 0 && (
                <p className="text-xs text-slate-500 text-center py-4">No emails configured yet.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 3. EDUCATION TAB */}
      {activeTab === 'education' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">
              {editingEduId ? 'Edit Academic Trajectory' : 'Add Academic Trajectory'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Level</label>
                <select
                  value={eduForm.level}
                  onChange={(e) => {
                    const newLevel = e.target.value;
                    const locked = newLevel === 'High School' || newLevel === 'Matriculation';
                    setEduForm({
                      ...eduForm,
                      level: newLevel,
                      stream: locked ? '' : eduForm.stream
                    });
                  }}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                >
                  <option value="Doctorate">Doctorate</option>
                  <option value="Post Graduate">Post Graduate</option>
                  <option value="Graduate">Graduate</option>
                  <option value="Diploma">Diploma</option>
                  <option value="High School">High School</option>
                  <option value="Matriculation">Matriculation</option>
                </select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-medium text-slate-300">Stream / Field</label>
                  {(eduForm.level === 'High School' || eduForm.level === 'Matriculation') && (
                    <span className="text-[10px] text-amber-400 font-semibold">Locked ({eduForm.level})</span>
                  )}
                </div>
                <input
                  type="text"
                  value={eduForm.level === 'High School' || eduForm.level === 'Matriculation' ? '' : eduForm.stream}
                  onChange={(e) => setEduForm({ ...eduForm, stream: e.target.value })}
                  disabled={eduForm.level === 'High School' || eduForm.level === 'Matriculation'}
                  placeholder={
                    eduForm.level === 'High School' || eduForm.level === 'Matriculation'
                      ? 'Not applicable for High School / Matriculation (Locked)'
                      : 'e.g. Computer Science & AI'
                  }
                  className={`w-full px-3 py-2 bg-slate-950 border rounded-xl text-xs outline-none transition-all ${
                    eduForm.level === 'High School' || eduForm.level === 'Matriculation'
                      ? 'border-slate-800/50 text-slate-500 bg-slate-900/40 cursor-not-allowed'
                      : 'border-slate-800 text-white focus:border-indigo-500'
                  }`}
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Institution</label>
                <input
                  type="text"
                  value={eduForm.institution}
                  onChange={(e) => setEduForm({ ...eduForm, institution: e.target.value })}
                  placeholder="e.g. Massachusetts Institute of Technology"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="sm:col-span-2 lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-800/80">
                <MonthYearPicker
                  label="Starting Date"
                  value={eduForm.starting_month_year}
                  onChange={(val) => setEduForm({ ...eduForm, starting_month_year: val })}
                  minYear={1800}
                  maxYear={3000}
                  required
                />

                <MonthYearPicker
                  label="Ending Date"
                  value={eduForm.ending_month_year}
                  onChange={(val) => setEduForm({ ...eduForm, ending_month_year: val })}
                  disabled={eduForm.currently_studying}
                  disabledPlaceholder="Currently Studying (Ending Date Not Required)"
                  minYear={1800}
                  maxYear={3000}
                  required={!eduForm.currently_studying}
                />
              </div>

              <div className="flex items-center gap-2 pt-2 sm:col-span-2 lg:col-span-3">
                <input
                  type="checkbox"
                  id="edu_currently_studying"
                  checked={eduForm.currently_studying}
                  onChange={(e) => {
                    const checked = e.target.checked;
                    setEduForm({
                      ...eduForm,
                      currently_studying: checked,
                      ...(checked ? { score_type: '', score_value: '' } : {})
                    });
                  }}
                  className="w-4 h-4 rounded text-indigo-600 bg-slate-950 border-slate-800 cursor-pointer"
                />
                <label htmlFor="edu_currently_studying" className="text-xs text-slate-300 cursor-pointer font-medium">
                  Currently Studying (In Progress — Ending Date & CGPA/Percentage Locked)
                </label>
              </div>

              {/* 2 BOXES: CGPA / Percentage Category & Marks Number */}
              <div className="sm:col-span-2 lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-800/80">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-xs font-medium text-slate-300">
                      Score Category (Box 1)
                    </label>
                    {eduForm.currently_studying && (
                      <span className="text-[10px] text-amber-400 font-semibold">Locked (Currently Studying)</span>
                    )}
                  </div>
                  <select
                    value={eduForm.currently_studying ? '' : eduForm.score_type}
                    onChange={(e) => setEduForm({ ...eduForm, score_type: e.target.value as any })}
                    disabled={eduForm.currently_studying}
                    className={`w-full px-3 py-2 bg-slate-950 border rounded-xl text-xs outline-none transition-all ${
                      eduForm.currently_studying
                        ? 'border-slate-800/50 text-slate-500 bg-slate-900/40 cursor-not-allowed'
                        : 'border-slate-800 text-white focus:border-indigo-500'
                    }`}
                  >
                    <option value="">None / Not Applicable</option>
                    <option value="Percentage">Percentage (0 – 100%)</option>
                    <option value="CGPA 10">CGPA 10 (0 – 10.00)</option>
                    <option value="CGPA 5">CGPA 5 (0 – 5.00)</option>
                  </select>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-xs font-medium text-slate-300">
                      Marks / Score Number (Box 2)
                    </label>
                    {eduForm.currently_studying && (
                      <span className="text-[10px] text-amber-400 font-semibold">Locked (Currently Studying)</span>
                    )}
                  </div>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max={
                      eduForm.score_type === 'Percentage'
                        ? '100'
                        : eduForm.score_type === 'CGPA 10'
                        ? '10'
                        : eduForm.score_type === 'CGPA 5'
                        ? '5'
                        : '100'
                    }
                    value={eduForm.currently_studying ? '' : eduForm.score_value}
                    onChange={(e) => setEduForm({ ...eduForm, score_value: e.target.value })}
                    disabled={eduForm.currently_studying || !eduForm.score_type}
                    placeholder={
                      eduForm.currently_studying
                        ? 'Locked while currently studying'
                        : !eduForm.score_type
                        ? 'Select a category first'
                        : eduForm.score_type === 'Percentage'
                        ? 'e.g. 88.50 (0 to 100)'
                        : eduForm.score_type === 'CGPA 10'
                        ? 'e.g. 8.75 (0 to 10)'
                        : 'e.g. 4.25 (0 to 5)'
                    }
                    className={`w-full px-3 py-2 bg-slate-950 border rounded-xl text-xs outline-none transition-all ${
                      eduForm.currently_studying || !eduForm.score_type
                        ? 'border-slate-800/50 text-slate-500 bg-slate-900/40 cursor-not-allowed'
                        : 'border-slate-800 text-white focus:border-indigo-500'
                    }`}
                  />
                  <p className="text-[10px] text-slate-400 mt-1">
                    {eduForm.score_type === 'Percentage' && 'Enter percentage between 0 and 100 (up to 2 decimal places).'}
                    {eduForm.score_type === 'CGPA 10' && 'Enter CGPA between 0 and 10.00 (up to 2 decimal places).'}
                    {eduForm.score_type === 'CGPA 5' && 'Enter CGPA between 0 and 5.00 (up to 2 decimal places).'}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-800">
              <button
                onClick={handleSaveEducation}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-md"
              >
                {editingEduId ? 'Update Education' : 'Add Education'}
              </button>
              {editingEduId && (
                <button
                  onClick={() => {
                    setEditingEduId(null);
                    setEduForm({
                      level: 'Graduate',
                      stream: '',
                      institution: '',
                      starting_month_year: '',
                      ending_month_year: '',
                      currently_studying: false,
                      score_type: '',
                      score_value: '',
                      ordering: 0
                    });
                  }}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-medium cursor-pointer"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Education List */}
          <div className="space-y-3">
            {(() => {
              const LEVEL_ORDER: Record<string, number> = {
                'Doctorate': 1,
                'Post Graduate': 2,
                'Graduate': 3,
                'Diploma': 4,
                'Undergraduate': 4,
                'High School': 5,
                'Matriculation': 6
              };
              const sorted = [...educations].sort((a, b) => {
                const orderA = LEVEL_ORDER[a.level] ?? 99;
                const orderB = LEVEL_ORDER[b.level] ?? 99;
                if (orderA !== orderB) return orderA - orderB;
                if (a.ordering !== b.ordering) return a.ordering - b.ordering;
                return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
              });
              return sorted.map((edu) => (
              <div
                key={edu.id}
                className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-purple-400">{edu.level}</span>
                    {edu.score_type && edu.score_value != null && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                        {edu.score_type === 'Percentage'
                          ? `${edu.score_value}%`
                          : `${edu.score_value} / ${edu.score_type === 'CGPA 10' ? '10' : '5'} CGPA`}
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-bold text-white">{edu.stream || `${edu.level} Education`}</h4>
                  <p className="text-xs text-slate-400">
                    {edu.institution || 'Unspecified'} • {edu.starting_month_year} –{' '}
                    {edu.currently_studying ? 'Currently Studying' : edu.ending_month_year}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setEditingEduId(edu.id);
                      setEduForm({
                        level: edu.level,
                        stream: edu.stream || '',
                        institution: edu.institution || '',
                        starting_month_year: edu.starting_month_year,
                        ending_month_year: edu.ending_month_year || '',
                        currently_studying: edu.currently_studying,
                        score_type: edu.score_type || '',
                        score_value: edu.score_value != null ? String(edu.score_value) : '',
                        ordering: edu.ordering
                      });
                    }}
                    className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg cursor-pointer"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteEducation(edu.id)}
                    className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg cursor-pointer"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ));
            })()}
            {educations.length === 0 && (
              <p className="text-xs text-slate-500 py-6 text-center">No education records configured yet.</p>
            )}
          </div>
        </div>
      )}

      {/* 4. WORK EXPERIENCE TAB */}
      {activeTab === 'experience' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">
              {editingExpId ? 'Edit Work Experience' : 'Add Work Experience'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Role / Designation</label>
                <input
                  type="text"
                  value={expForm.role}
                  onChange={(e) => setExpForm({ ...expForm, role: e.target.value })}
                  placeholder="e.g. Lead Systems Architect"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Employer / Organization</label>
                <input
                  type="text"
                  value={expForm.employer}
                  onChange={(e) => setExpForm({ ...expForm, employer: e.target.value })}
                  placeholder="e.g. Existence Labs"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Work Mode</label>
                <select
                  value={expForm.work_mode}
                  onChange={(e) => setExpForm({ ...expForm, work_mode: e.target.value as any })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                >
                  <option value="On-site">On-site</option>
                  <option value="Remote">Remote</option>
                  <option value="Hybrid">Hybrid</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Location {expForm.work_mode === 'Remote' ? '(Optional)' : '(Required)'}
                </label>
                <input
                  type="text"
                  value={expForm.location}
                  onChange={(e) => setExpForm({ ...expForm, location: e.target.value })}
                  placeholder={expForm.work_mode === 'Remote' ? 'Remote' : 'e.g. Zurich, Switzerland'}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="sm:col-span-2 lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-800/80">
                <MonthYearPicker
                  label="Starting Date"
                  value={expForm.starting_month_year}
                  onChange={(val) => setExpForm({ ...expForm, starting_month_year: val })}
                  minYear={1800}
                  maxYear={3000}
                  required
                />

                <MonthYearPicker
                  label="Ending Date"
                  value={expForm.ending_month_year}
                  onChange={(val) => setExpForm({ ...expForm, ending_month_year: val })}
                  disabled={expForm.currently_working}
                  disabledPlaceholder="Currently Working (Ending Date Not Required)"
                  minYear={1800}
                  maxYear={3000}
                  required={!expForm.currently_working}
                />
              </div>

              <div className="flex items-center gap-2 pt-2 sm:col-span-2 lg:col-span-3">
                <input
                  type="checkbox"
                  id="exp_currently_working"
                  checked={expForm.currently_working}
                  onChange={(e) => setExpForm({ ...expForm, currently_working: e.target.checked })}
                  className="w-4 h-4 rounded text-indigo-600 bg-slate-950 border-slate-800 cursor-pointer"
                />
                <label htmlFor="exp_currently_working" className="text-xs text-slate-300 cursor-pointer font-medium">
                  Currently Working (Present Role)
                </label>
              </div>
            </div>

            <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-800">
              <button
                onClick={handleSaveExperience}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-md"
              >
                {editingExpId ? 'Update Experience' : 'Add Experience'}
              </button>
              {editingExpId && (
                <button
                  onClick={() => {
                    setEditingExpId(null);
                    setExpForm({
                      role: '',
                      employer: '',
                      work_mode: 'On-site',
                      location: '',
                      starting_month_year: '',
                      ending_month_year: '',
                      currently_working: false,
                      ordering: 0
                    });
                  }}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-medium cursor-pointer"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Overall Experience Summary Banner */}
          {experiences.length > 0 && (() => {
            const overall = calculateOverallExperience(experiences);
            return (
              <div className="p-4 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-500/30 flex items-center justify-between flex-wrap gap-4 shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shadow-inner">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] font-semibold text-indigo-300 uppercase tracking-wider">
                      Overall Career Duration
                    </span>
                    <p className="text-base font-bold text-white">
                      {overall.formatted}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1.5 font-medium">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    {experiences.filter((e) => e.currently_working).length > 0 ? 'Currently Active' : 'Completed Positions'}
                  </span>
                  <span>•</span>
                  <span>{experiences.length} Position{experiences.length === 1 ? '' : 's'} Sorted by Timeline</span>
                </div>
              </div>
            );
          })()}

          {/* Experience List - Sorted Descending by Timeline */}
          <div className="space-y-3">
            {sortExperiencesByTimelineDesc(experiences).map((exp) => {
              const duration = calculateExperienceDuration(
                exp.starting_month_year,
                exp.ending_month_year,
                exp.currently_working
              );
              return (
                <div
                  key={exp.id}
                  className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center justify-between transition-all hover:border-slate-700"
                >
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-sm font-bold text-white">{exp.role}</h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
                        {exp.work_mode}
                      </span>
                      {exp.currently_working && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          Currently Working
                        </span>
                      )}
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800/80 border border-slate-700 text-slate-300 flex items-center gap-1">
                        <Clock className="w-3 h-3 text-indigo-400" />
                        {duration.formatted}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {exp.employer} • {exp.location || 'Remote'} • {exp.starting_month_year} –{' '}
                      {exp.currently_working ? 'Present' : exp.ending_month_year}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setEditingExpId(exp.id);
                        setExpForm({
                          role: exp.role,
                          employer: exp.employer,
                          work_mode: exp.work_mode,
                          location: exp.location || '',
                          starting_month_year: exp.starting_month_year,
                          ending_month_year: exp.ending_month_year || '',
                          currently_working: exp.currently_working,
                          ordering: exp.ordering
                        });
                      }}
                      className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg cursor-pointer"
                      title="Edit"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteExperience(exp.id)}
                      className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg cursor-pointer"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
            {experiences.length === 0 && (
              <p className="text-xs text-slate-500 py-6 text-center">No experience records configured yet.</p>
            )}
          </div>
        </div>
      )}

      {/* 5. SKILLS TAB (7-LEVEL CALIBRATION & MANAGEMENT) */}
      {activeTab === 'skills' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                {editingSkillId ? 'Edit Skill & 7-Level Mastery Rating' : 'Add Skill & Calibrate 7-Level Rating'}
              </h3>
              <span className="text-xs font-mono text-slate-400">
                {skills.length} Registered Competencies
              </span>
            </div>

            {/* Multi-Domain Selector with Search & Taxonomy across all Engineering, Medical, Business, Legal & Other fields */}
            <div className="mb-4">
              <SkillDomainSelector
                selectedDomains={skillForm.domains && skillForm.domains.length > 0
                  ? skillForm.domains
                  : (skillForm.domain ? skillForm.domain.split(',').map((d) => d.trim()).filter(Boolean) : [])}
                onChange={(doms) => {
                  setSkillForm({
                    ...skillForm,
                    domains: doms,
                    domain: doms.join(', ')
                  });
                }}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Skill Name *</label>
                <input
                  type="text"
                  value={skillForm.name}
                  onChange={(e) => setSkillForm({ ...skillForm, name: e.target.value })}
                  placeholder="e.g. NumPy, SciPy, Pandas, TensorFlow"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-amber-500"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  Tip: Comma-separate names to bulk add under selected domain(s).
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Display Ordering</label>
                <input
                  type="number"
                  min={0}
                  value={skillForm.ordering}
                  onChange={(e) => setSkillForm({ ...skillForm, ordering: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-amber-500"
                />
              </div>
            </div>

            {/* Multi-Category Selector across 17 Categories */}
            <div className="mt-4">
              <SkillCategorySelector
                selectedCategories={skillForm.categories}
                onChange={(cats) =>
                  setSkillForm({
                    ...skillForm,
                    categories: cats,
                    category: cats.join(', ')
                  })
                }
              />
            </div>

            {/* Optional Description */}
            <div className="mt-4">
              <label className="block text-xs font-medium text-slate-300 mb-1">Description (Optional)</label>
              <input
                type="text"
                value={skillForm.description}
                onChange={(e) => setSkillForm({ ...skillForm, description: e.target.value })}
                placeholder="Brief implementation note or context (e.g. Raft, Paxos, Multi-Leader systems)"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
              />
            </div>

            {/* Visibility Toggle */}
            <div className="mt-4 flex items-center gap-2">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={skillForm.visibility}
                  onChange={(e) => setSkillForm({ ...skillForm, visibility: e.target.checked })}
                  className="rounded border-slate-800 bg-slate-950 text-indigo-600 focus:ring-indigo-500"
                />
                <span>Visible on Public Profile</span>
              </label>
            </div>

            {/* Reusable 7-Level Rating Selector Component */}
            <div className="mt-5 pt-4 border-t border-slate-800">
              <SkillRatingSelector
                value={skillForm.rating}
                onChange={(lvl) => setSkillForm({ ...skillForm, rating: lvl })}
                label="Select Calibrated Mastery Rating (1 to 7)"
              />
            </div>

            <div className="flex items-center gap-3 mt-5 pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={handleSaveSkill}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-md flex items-center gap-1.5"
              >
                <Save className="w-3.5 h-3.5" />
                {editingSkillId ? 'Update Skill' : 'Add Skill'}
              </button>
              {editingSkillId && (
                <button
                  type="button"
                  onClick={() => {
                    setEditingSkillId(null);
                    setSkillForm({
                      name: '',
                      domain: '',
                      domains: [],
                      category: 'Technical',
                      categories: ['Technical'],
                      description: '',
                      rating: 4,
                      visibility: true,
                      ordering: 0
                    });
                  }}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-medium cursor-pointer"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Skill List with Reusable SkillCards & Reorder Support */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills.map((sk, idx) => (
              <SkillCard
                key={sk.id}
                skill={sk}
                isAdmin={true}
                onEdit={(item) => {
                  const itemCats = item.categories && item.categories.length > 0
                    ? item.categories
                    : (item.category ? item.category.split(',').map((c) => c.trim()).filter(Boolean) : ['Technical']);
                  const itemDoms = item.domains && item.domains.length > 0
                    ? item.domains
                    : (item.domain ? item.domain.split(',').map((d) => d.trim()).filter(Boolean) : (item.metadata_info?.domain ? String(item.metadata_info.domain).split(',').map((d: string) => d.trim()).filter(Boolean) : []));
                  setEditingSkillId(item.id);
                  setSkillForm({
                    name: item.name,
                    domain: itemDoms.join(', '),
                    domains: itemDoms,
                    category: itemCats.join(', '),
                    categories: itemCats,
                    description: item.description || '',
                    rating: item.rating,
                    visibility: item.visibility ?? item.is_visible ?? true,
                    ordering: item.ordering ?? item.display_order ?? 0
                  });
                }}
                onDelete={(id) => handleDeleteSkill(id)}
                onToggleVisibility={(item) => handleToggleSkillVisibility(item)}
                onMoveUp={() => handleMoveSkill(idx, 'up')}
                onMoveDown={() => handleMoveSkill(idx, 'down')}
                canMoveUp={idx > 0}
                canMoveDown={idx < skills.length - 1}
              />
            ))}
            {skills.length === 0 && (
              <p className="col-span-full text-xs text-slate-500 py-8 text-center glass-panel rounded-2xl border border-slate-800">
                No skills configured yet. Add your verified technical competencies above.
              </p>
            )}
          </div>
        </div>
      )}

      {/* 6. PROJECTS TAB */}
      {activeTab === 'projects' && (
        <CmsProjectsSection
          projects={projects}
          skills={skills}
          onRefresh={() => {
            loadAllCmsData();
            onRefreshAll();
          }}
          executeWithPin={executeWithPin}
          notify={notify}
        />
      )}

      {/* 7. HOBBIES TAB */}
      {activeTab === 'hobbies' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">
              {editingHiId ? 'Edit Hobby' : 'Add Hobby'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Hobby Name</label>
                <input
                  type="text"
                  value={hiForm.name}
                  onChange={(e) => setHiForm({ ...hiForm, name: e.target.value })}
                  placeholder="e.g. Film Photography"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Category (Optional)</label>
                <input
                  type="text"
                  value={hiForm.category}
                  onChange={(e) => setHiForm({ ...hiForm, category: e.target.value })}
                  placeholder="e.g. Creative Arts"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Icon Keyword</label>
                <input
                  type="text"
                  value={hiForm.icon}
                  onChange={(e) => setHiForm({ ...hiForm, icon: e.target.value })}
                  placeholder="e.g. camera, music"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-800">
              <button
                onClick={() => handleSaveHi('hobby')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-md"
              >
                {editingHiId ? 'Update Hobby' : 'Add Hobby'}
              </button>
              {editingHiId && (
                <button
                  onClick={() => {
                    setEditingHiId(null);
                    setHiForm({ type: 'hobby', name: '', category: '', icon: '' });
                  }}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-medium cursor-pointer"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Hobbies List */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {hobbiesList.map((item) => (
              <div
                key={item.id}
                className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <h4 className="text-sm font-bold text-white">{item.name}</h4>
                  <span className="text-[11px] text-slate-400 font-medium">{item.category || 'General'}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => {
                      setEditingHiId(item.id);
                      setHiForm({
                        type: 'hobby',
                        name: item.name,
                        category: item.category || '',
                        icon: item.icon || ''
                      });
                    }}
                    className="p-1.5 text-slate-400 hover:text-white rounded-lg cursor-pointer"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteHi(item.id, 'hobby')}
                    className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
            {hobbiesList.length === 0 && (
              <p className="col-span-full text-xs text-slate-500 py-6 text-center">No hobbies registered yet.</p>
            )}
          </div>
        </div>
      )}

      {/* 7. INTERESTS TAB */}
      {activeTab === 'interests' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">
              {editingHiId ? 'Edit Intellectual Interest' : 'Add Intellectual Interest'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Interest Topic</label>
                <input
                  type="text"
                  value={hiForm.name}
                  onChange={(e) => setHiForm({ ...hiForm, name: e.target.value })}
                  placeholder="e.g. Type Theory, Astrophysics"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Category (Optional)</label>
                <input
                  type="text"
                  value={hiForm.category}
                  onChange={(e) => setHiForm({ ...hiForm, category: e.target.value })}
                  placeholder="e.g. Theoretical Computer Science"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Icon Keyword</label>
                <input
                  type="text"
                  value={hiForm.icon}
                  onChange={(e) => setHiForm({ ...hiForm, icon: e.target.value })}
                  placeholder="e.g. book, atom"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-800">
              <button
                onClick={() => handleSaveHi('interest')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-md"
              >
                {editingHiId ? 'Update Interest' : 'Add Interest'}
              </button>
              {editingHiId && (
                <button
                  onClick={() => {
                    setEditingHiId(null);
                    setHiForm({ type: 'interest', name: '', category: '', icon: '' });
                  }}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-medium cursor-pointer"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Interests List */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {interestsList.map((item) => (
              <div
                key={item.id}
                className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <h4 className="text-sm font-bold text-white">{item.name}</h4>
                  <span className="text-[11px] text-slate-400 font-medium">{item.category || 'General'}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => {
                      setEditingHiId(item.id);
                      setHiForm({
                        type: 'interest',
                        name: item.name,
                        category: item.category || '',
                        icon: item.icon || ''
                      });
                    }}
                    className="p-1.5 text-slate-400 hover:text-white rounded-lg cursor-pointer"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteHi(item.id, 'interest')}
                    className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
            {interestsList.length === 0 && (
              <p className="col-span-full text-xs text-slate-500 py-6 text-center">No interests registered yet.</p>
            )}
          </div>
        </div>
      )}

      {/* 8. PERSONALITY TAB */}
      {activeTab === 'personality' && (
        <div className="space-y-6">
          {/* Assessment Results Overview */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Brain className="w-4 h-4 text-purple-400" />
                Completed Assessment Records ({assessmentHistory.length})
              </h3>
              <span className="text-[11px] text-slate-400">
                {assessmentHistory.filter((r) => r.is_public ?? true).length} Public ·{' '}
                {assessmentHistory.filter((r) => !(r.is_public ?? true)).length} Private
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {assessmentHistory.map((item) => (
                <div key={item.id} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-bold text-indigo-400 uppercase bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                        {item.assessment_type}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">v{item.result_version || '1.0'}</span>
                    </div>
                    <span className="text-xs font-bold text-white font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      {item.result_code}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-200">{item.result_title}</h4>
                    <p className="text-xs text-slate-400 line-clamp-2 mt-1">{item.summary}</p>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-900 text-[10px]">
                    <span className="text-slate-500 font-mono">
                      {new Date(item.completed_at).toLocaleDateString()}
                    </span>

                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleToggleResultVisibility(item.id, item.is_public ?? true)}
                        className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold transition-all cursor-pointer ${
                          item.is_public ?? true
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/30 hover:bg-amber-500/20'
                        }`}
                        title="Toggle public visibility (PIN required)"
                      >
                        {item.is_public ?? true ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                        <span>{item.is_public ?? true ? 'Public' : 'Private'}</span>
                      </button>

                      <button
                        onClick={() => handleDeleteAssessmentResult(item.id)}
                        className="p-1 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors cursor-pointer"
                        title="Delete assessment result (PIN required)"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              {assessmentHistory.length === 0 && (
                <div className="col-span-full text-center py-6 text-xs text-slate-500">
                  Assessments not completed yet. Complete an empirical assessment in the Psychology view to generate results.
                </div>
              )}
            </div>
          </div>

          {/* Assessment Model Definitions & Version Management */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Shield className="w-4 h-4 text-indigo-400" />
                Assessment Model Definitions & Versions ({assessmentDefinitions.length})
              </h3>
              <span className="text-[10px] text-slate-400 font-mono">Immutable Version Locking Enabled</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {assessmentDefinitions.map((def) => (
                <div key={def.id} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white font-mono">{def.code}</span>
                    <span
                      className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                        def.status === 'PUBLISHED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {def.status}
                    </span>
                  </div>

                  <h4 className="text-sm font-semibold text-slate-200">{def.name}</h4>
                  <p className="text-xs text-slate-400 line-clamp-2">{def.description || def.tagline || 'Standardized psychometric model'}</p>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-900 text-[10px] text-slate-500">
                    <span>v{def.version} · {def.question_count} Qs</span>
                    <button
                      onClick={() => handleToggleDefinitionStatus(def.id, def.status)}
                      className="px-2 py-0.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded border border-slate-800 transition-colors cursor-pointer"
                      title="Toggle between PUBLISHED and ARCHIVED (PIN required)"
                    >
                      {def.status === 'PUBLISHED' ? 'Archive' : 'Publish'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Assessment Telemetry Statistics */}
          {assessmentStats && (
            <div className="glass-panel p-5 rounded-3xl border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-3 bg-slate-950 rounded-2xl border border-slate-900">
                <span className="text-[10px] uppercase font-bold text-slate-400">Total Attempts</span>
                <p className="text-lg font-bold text-white font-mono mt-0.5">{assessmentStats.total_sessions}</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-2xl border border-slate-900">
                <span className="text-[10px] uppercase font-bold text-emerald-400">Completed Sessions</span>
                <p className="text-lg font-bold text-emerald-400 font-mono mt-0.5">{assessmentStats.completed_sessions}</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-2xl border border-slate-900">
                <span className="text-[10px] uppercase font-bold text-indigo-400">Public Results</span>
                <p className="text-lg font-bold text-indigo-400 font-mono mt-0.5">{assessmentStats.public_results}</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-2xl border border-slate-900">
                <span className="text-[10px] uppercase font-bold text-amber-400">Private Results</span>
                <p className="text-lg font-bold text-amber-400 font-mono mt-0.5">{assessmentStats.private_results}</p>
              </div>
            </div>
          )}


          {/* Test-Governed Personality Intelligence Overview */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Brain className="w-5 h-5 text-indigo-400" />
                  Test-Governed Personality Intelligence
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Empirical personality assessments determine all psychological traits automatically. Manual entry is disabled.
                </p>
              </div>
              <button
                onClick={handleRefreshSynthesis}
                className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold cursor-pointer shadow-md transition-all self-start sm:self-auto"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Re-sync Synthesis</span>
              </button>
            </div>

            {/* Explanatory Rule Banner */}
            <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-800/40 text-xs text-indigo-200 space-y-1.5">
              <span className="font-bold text-indigo-300">Psychological Assessment Invariants:</span>
              <p className="text-slate-300 leading-relaxed">
                • Strengths and weaknesses are evaluated dynamically based on the number of completed tests:
                <br />
                <span className="text-indigo-300 font-mono text-[11px] pl-3 block my-0.5">
                  – 1 test given &rarr; evaluated on the basis of that 1 test
                  <br />
                  – 2 tests given &rarr; evaluated on the basis of those 2 tests
                  <br />
                  – 3 tests given &rarr; evaluated on the basis of those 3 tests (11 core strengths total)
                </span>
                • Exactly <strong className="text-white">11 core strengths</strong> (derived across completed assessments without mandatory Communication override).
                <br />
                • Categorized by empirical personality types (MBTI, DISC, Big Five) with <strong className="text-white">no soft skills</strong>.
              </p>
            </div>

            {/* Personality Types */}
            {synthesis && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-indigo-400">MBTI Cognitive Style</span>
                    <h4 className="text-sm font-bold text-white mt-1 font-mono">
                      {synthesis.latest_results.MBTI?.result_code || 'Pending Test'}
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {synthesis.latest_results.MBTI?.result_title || 'Cognitive style not yet assessed.'}
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-purple-400">DISC Operational Drive</span>
                    <h4 className="text-sm font-bold text-white mt-1 font-mono">
                      {synthesis.latest_results.DISC?.result_code || 'Pending Test'}
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {synthesis.latest_results.DISC?.result_title || 'Behavioral profile not yet assessed.'}
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-amber-400">Big Five Archetype</span>
                    <h4 className="text-sm font-bold text-white mt-1 font-mono">
                      {synthesis.latest_results.BIG_FIVE?.result_code || 'Pending Test'}
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {synthesis.latest_results.BIG_FIVE?.result_title || 'Five-factor indices not yet assessed.'}
                    </p>
                  </div>
                </div>

                {/* Key Strengths & Weaknesses Side-by-Side (Dynamic Evaluation per Completed Tests) */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* 11 Core Strengths */}
                  <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Award className="w-4 h-4" />
                          11 Core Strengths
                        </span>
                        <p className="text-[10px] text-slate-400 mt-0.5">
                          Evaluated on {synthesis.assessments_completed.length} completed test{synthesis.assessments_completed.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                      <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        {synthesis.key_strengths.length} Strengths
                      </span>
                    </div>

                    <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                      {synthesis.key_strengths.map((str, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-xl border text-xs flex items-start gap-2.5 transition-colors bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700"
                        >
                          <span className="font-mono text-[10px] text-emerald-400 font-bold shrink-0 mt-0.5">
                            #{idx + 1}
                          </span>
                          <div className="flex-1">
                            <span>{str}</span>
                          </div>
                        </div>
                      ))}
                      {synthesis.key_strengths.length === 0 && (
                        <p className="text-xs text-slate-500 py-3 text-center">No strengths synthesized yet.</p>
                      )}
                    </div>
                  </div>

                  {/* Growth Areas & Weaknesses */}
                  <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                          <AlertCircle className="w-4 h-4" />
                          Growth Blindspots & Weaknesses
                        </span>
                        <p className="text-[10px] text-slate-400 mt-0.5">
                          Evaluated on {synthesis.assessments_completed.length} completed test{synthesis.assessments_completed.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                      <span className="text-[11px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        {synthesis.key_weaknesses.length} Weaknesses
                      </span>
                    </div>

                    <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                      {synthesis.key_weaknesses.map((wk, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs flex items-start gap-2.5 text-slate-300"
                        >
                          <span className="font-mono text-[10px] text-amber-500 font-bold shrink-0 mt-0.5">
                            #{idx + 1}
                          </span>
                          <span className="flex-1">{wk}</span>
                        </div>
                      ))}
                      {synthesis.key_weaknesses.length === 0 && (
                        <p className="text-xs text-slate-500 py-3 text-center">No weaknesses synthesized yet.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Synthesis Summary Notes */}
                {synthesis.summary_notes && (
                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-xs">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                      Assessment Synthesis Summary
                    </span>
                    <p className="text-slate-300 font-mono text-[11px] leading-relaxed">
                      {synthesis.summary_notes}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 9. CONTENT REVISIONS TAB (WITH RESTORE) */}
      {activeTab === 'revisions' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <RotateCcw className="w-5 h-5 text-indigo-400" />
                  Content Revision History & Snapshots
                </h2>
                <p className="text-xs text-slate-400">
                  Inspect immutable mutation versions and restore past snapshots with PIN verification.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-400">
                {revisions.length} total revisions
              </span>
            </div>

            <div className="space-y-3">
              {revisions.map((rev) => (
                <div
                  key={rev.id}
                  className="p-4 rounded-2xl bg-slate-950 border border-slate-800/90 text-xs space-y-2 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className="font-bold text-indigo-300 uppercase text-xs tracking-wider">
                        {rev.entity_name}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        rev.action === 'RESTORE'
                          ? 'bg-amber-500/10 border border-amber-500/30 text-amber-300'
                          : 'bg-slate-900 border border-slate-800 text-slate-300'
                      }`}>
                        {rev.action}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        Rev #{rev.id}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setSelectedRevision(selectedRevision?.id === rev.id ? null : rev)}
                        className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-[11px] font-medium transition-colors cursor-pointer"
                      >
                        {selectedRevision?.id === rev.id ? 'Hide Diff' : 'Inspect Diff'}
                      </button>
                      <button
                        onClick={() => handleRestoreRevision(rev)}
                        className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 border border-amber-500/30 text-amber-300 text-[11px] font-bold transition-all cursor-pointer"
                      >
                        <RotateCcw className="w-3 h-3" /> Restore
                      </button>
                    </div>
                  </div>

                  <p className="text-slate-300">{rev.change_summary || 'No summary provided'}</p>

                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-2 border-t border-slate-900">
                    <span>Editor: {rev.editor_username}</span>
                    <span>{new Date(rev.created_at).toLocaleString()}</span>
                  </div>

                  {/* Expandable Diff Inspector */}
                  {selectedRevision?.id === rev.id && (
                    <div className="mt-3 pt-3 border-t border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-3 animate-fadeIn">
                      <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                        <span className="text-[10px] font-bold uppercase text-rose-400 mb-1 block">Previous State</span>
                        <pre className="text-[10px] text-slate-400 font-mono overflow-x-auto whitespace-pre-wrap max-h-48">
                          {rev.previous_snapshot ? JSON.stringify(rev.previous_snapshot, null, 2) : 'None (Initial Creation)'}
                        </pre>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                        <span className="text-[10px] font-bold uppercase text-emerald-400 mb-1 block">Snapshot (Restorable)</span>
                        <pre className="text-[10px] text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap max-h-48">
                          {rev.current_snapshot ? JSON.stringify(rev.current_snapshot, null, 2) : 'None'}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {revisions.length === 0 && (
                <p className="text-xs text-slate-500 py-8 text-center">No content revisions recorded yet.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 10. AUDIT LOG TAB */}
      {activeTab === 'audit' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Shield className="w-5 h-5 text-emerald-400" />
                  Security & Operations Audit Trail
                </h2>
                <p className="text-xs text-slate-400">
                  Immutable record of logins, PIN verifications, mutations, and security events.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-slate-400" />
                <select
                  value={auditFilter}
                  onChange={(e) => setAuditFilter(e.target.value)}
                  className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                >
                  <option value="ALL">All Event Types</option>
                  <option value="PIN">PIN Events</option>
                  <option value="PROFILE">Profile Events</option>
                  <option value="EDUCATION">Education Events</option>
                  <option value="EXPERIENCE">Experience Events</option>
                  <option value="REVISION">Revision Events</option>
                  <option value="LOGIN">Auth Events</option>
                </select>
              </div>
            </div>

            <div className="space-y-2.5">
              {filteredAuditEvents.map((ev) => (
                <div
                  key={ev.id}
                  className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-200 text-xs">{ev.event_type}</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          ev.status === 'SUCCESS' ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'
                        }`}
                      >
                        {ev.status}
                      </span>
                    </div>
                    {ev.details && (
                      <p className="text-slate-400 text-[11px] mt-1 font-mono">
                        {typeof ev.details === 'string' ? ev.details : JSON.stringify(ev.details)}
                      </p>
                    )}
                  </div>

                  <div className="flex sm:flex-col items-end text-[10px] text-slate-500 font-mono gap-1">
                    <span>Actor: {ev.username || 'system'}</span>
                    <span>IP: {ev.ip_address || 'local'}</span>
                    <span>{new Date(ev.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              ))}
              {filteredAuditEvents.length === 0 && (
                <p className="text-xs text-slate-500 py-6 text-center">No matching audit events found.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 11. PIN SECURITY TAB */}
      {activeTab === 'pin' && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 max-w-md space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white">Security PIN Management</h2>
            <p className="text-xs text-slate-400">Manage the PIN protecting content changes and deletions.</p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">PIN Configured:</span>
              <span className={`font-bold ${pinStatus?.is_configured ? 'text-emerald-400' : 'text-rose-400'}`}>
                {pinStatus?.is_configured ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Account Lockout Status:</span>
              <span className={`font-bold ${pinStatus?.is_locked ? 'text-rose-400' : 'text-emerald-400'}`}>
                {pinStatus?.is_locked ? 'Locked' : 'Normal'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Attempts Remaining:</span>
              <span className="font-mono text-white">{pinStatus?.attempts_remaining ?? 5}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">PIN Session State:</span>
              <span className={`font-bold ${activePin ? 'text-emerald-400' : 'text-slate-500'}`}>
                {activePin ? 'Active / Unlocked' : 'Locked'}
              </span>
            </div>
          </div>

          {activePin && (
            <button
              onClick={() => {
                setActivePin(null);
                notify('success', 'Active PIN session cleared and locked.');
              }}
              className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold rounded-xl border border-slate-800 cursor-pointer"
            >
              Lock PIN Session Now
            </button>
          )}

          {pinStatus?.is_configured ? (
            <form onSubmit={handleChangePin} className="space-y-4 pt-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Change PIN</h3>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Current PIN</label>
                <input
                  type="password"
                  maxLength={8}
                  value={pinChangeForm.currentPin}
                  onChange={(e) => setPinChangeForm({ ...pinChangeForm, currentPin: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">New PIN (4-8 digits)</label>
                <input
                  type="password"
                  maxLength={8}
                  value={pinChangeForm.newPin}
                  onChange={(e) => setPinChangeForm({ ...pinChangeForm, newPin: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Confirm New PIN</label>
                <input
                  type="password"
                  maxLength={8}
                  value={pinChangeForm.confirmNewPin}
                  onChange={(e) => setPinChangeForm({ ...pinChangeForm, confirmNewPin: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md cursor-pointer"
              >
                Update PIN
              </button>
            </form>
          ) : (
            <button
              onClick={() => setPinModalOpen(true)}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-md cursor-pointer"
            >
              Configure Security PIN Now
            </button>
          )}
        </div>
      )}

      {/* PIN Security Modal */}
      <PinModal
        isOpen={pinModalOpen}
        onClose={() => {
          setPinModalOpen(false);
          setPendingAction(null);
        }}
        onSuccess={handlePinVerified}
      />
    </div>
  );
};

export default CmsDashboard;
