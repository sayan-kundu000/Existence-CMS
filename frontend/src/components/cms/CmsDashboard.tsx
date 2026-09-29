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
  RefreshCw
} from 'lucide-react';
import {
  Profile,
  ProfileEmail,
  Education,
  Experience,
  Skill,
  HobbyInterest,
  PersonalitySynthesis,
  DashboardStats,
  ContentRevision,
  AuditEvent,
  AssessmentResult
} from '../../types';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { PinModal } from '../common/PinModal';
import { MonthYearPicker } from '../common/MonthYearPicker';

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
  const [hobbiesInterests, setHobbiesInterests] = useState<HobbyInterest[]>([]);
  const [synthesis, setSynthesis] = useState<PersonalitySynthesis | null>(null);
  const [assessmentHistory, setAssessmentHistory] = useState<AssessmentResult[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [revisions, setRevisions] = useState<ContentRevision[]>([]);

  // UI States
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
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
    ordering: number;
  }>({
    level: 'Graduate',
    stream: '',
    institution: '',
    starting_month_year: 'Jan 2020',
    ending_month_year: 'Jun 2024',
    currently_studying: false,
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
    category: string;
    rating: number;
    ordering: number;
  }>({
    name: '',
    category: 'Technical',
    rating: 4,
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
      const [st, prof, emails, edus, exps, sks, his, syn, hist, evs, revs] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getProfile().catch(() => null),
        api.getProfileEmails().catch(() => []),
        api.getEducation().catch(() => []),
        api.getExperience().catch(() => []),
        api.getSkills(true).catch(() => []),
        api.getHobbiesInterests().catch(() => []),
        api.getPersonalitySynthesis().catch(() => null),
        api.getAssessmentHistory().catch(() => []),
        api.getAuditEvents(50).catch(() => []),
        api.getContentRevisions(50).catch(() => [])
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
      setEducations(edus);
      setExperiences(exps);
      setSkills(sks);
      setHobbiesInterests(his);
      if (syn) {
        setSynthesis(syn);
      }
      setAssessmentHistory(hist);
      setAuditEvents(evs);
      setRevisions(revs);
    } catch (e: any) {
      console.error('Failed to load CMS data', e);
    }
  };

  const notify = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 4000);
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
        notify('success', 'Profile coordinates updated successfully.');
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
        if (editingEmailId) {
          await api.updateProfileEmail(editingEmailId, {
            email: emailForm.email.trim(),
            label: emailForm.label.trim(),
            is_primary: emailForm.is_primary,
            display_order: Number(emailForm.display_order)
          });
          notify('success', 'Profile email updated.');
        } else {
          await api.addProfileEmail({
            email: emailForm.email.trim(),
            label: emailForm.label.trim(),
            is_primary: emailForm.is_primary,
            display_order: Number(emailForm.display_order)
          });
          notify('success', 'New profile email registered.');
        }
        setEditingEmailId(null);
        setEmailForm({ email: '', label: 'Personal', is_primary: false, display_order: 0 });
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
      await api.deleteProfileEmail(id);
      notify('success', `Deleted ${emailAddr}.`);
      loadAllCmsData();
      onRefreshAll();
    });
  };

  const handleSetPrimaryEmail = (emailItem: ProfileEmail) => {
    executeWithPin(async () => {
      await api.updateProfileEmail(emailItem.id, { is_primary: true });
      notify('success', `${emailItem.email} set as primary.`);
      loadAllCmsData();
      onRefreshAll();
    });
  };

  // 3. Education Actions
  const handleSaveEducation = () => {
    if (!eduForm.stream || !eduForm.stream.trim()) {
      notify('error', 'Stream / Field of study is required.');
      return;
    }
    const startStr = eduForm.starting_month_year?.trim() || 'Jan 2020';
    let endStr: string | null = eduForm.ending_month_year?.trim() || null;
    if (eduForm.currently_studying) {
      endStr = null;
    } else if (!endStr) {
      notify('error', 'Ending Month & Year is required when not currently studying.');
      return;
    }

    executeWithPin(async () => {
      setLoading(true);
      try {
        if (editingEduId) {
          await api.updateEducation(editingEduId, {
            level: eduForm.level as any,
            stream: eduForm.stream.trim(),
            institution: eduForm.institution?.trim() || null,
            starting_month_year: startStr,
            ending_month_year: endStr,
            currently_studying: eduForm.currently_studying,
            ordering: Number(eduForm.ordering) || 0
          });
          notify('success', 'Academic record updated successfully.');
        } else {
          await api.createEducation({
            level: eduForm.level as any,
            stream: eduForm.stream.trim(),
            institution: eduForm.institution?.trim() || null,
            starting_month_year: startStr,
            ending_month_year: endStr,
            currently_studying: eduForm.currently_studying,
            ordering: Number(eduForm.ordering) || 0
          });
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
    executeWithPin(async () => {
      setLoading(true);
      try {
        if (editingSkillId) {
          await api.updateSkill(editingSkillId, {
            name: skillForm.name,
            category: skillForm.category,
            rating: Number(skillForm.rating),
            ordering: Number(skillForm.ordering)
          });
          notify('success', 'Skill updated.');
        } else {
          await api.createSkill({
            name: skillForm.name,
            category: skillForm.category,
            rating: Number(skillForm.rating),
            visibility: true,
            ordering: Number(skillForm.ordering),
            metadata_info: {}
          });
          notify('success', 'Skill created.');
        }
        setEditingSkillId(null);
        setSkillForm({ name: '', category: 'Technical', rating: 4, ordering: 0 });
        loadAllCmsData();
        onRefreshAll();
      } finally {
        setLoading(false);
      }
    });
  };

  const handleDeleteSkill = (id: number) => {
    if (!confirm('Are you sure you want to delete this skill?')) return;
    executeWithPin(async () => {
      await api.deleteSkill(id);
      notify('success', 'Skill deleted.');
      loadAllCmsData();
      onRefreshAll();
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
      const syn = await api.getPersonalitySynthesis();
      setSynthesis(syn);
      notify('success', 'Personality synthesis refreshed from assessment tests.');
      loadAllCmsData();
      onRefreshAll();
    } catch (err: any) {
      notify('error', err.message);
    } finally {
      setLoading(false);
    }
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
              : 'bg-rose-950/40 border-rose-800 text-rose-200'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* CMS Navigation Tabs (11 Tabs) */}
      <div className="flex items-center gap-1 bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 overflow-x-auto scrollbar-none">
        {[
          { id: 'stats', label: 'Dashboard', icon: LayoutDashboard },
          { id: 'profile', label: 'Profile & Emails', icon: User },
          { id: 'education', label: 'Education', icon: GraduationCap },
          { id: 'experience', label: 'Experience', icon: Briefcase },
          { id: 'skills', label: 'Skills (7-L)', icon: Sparkles },
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
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-4">
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

              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_primary"
                    checked={emailForm.is_primary}
                    onChange={(e) => setEmailForm({ ...emailForm, is_primary: e.target.checked })}
                    className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-800"
                  />
                  <label htmlFor="is_primary" className="text-xs text-slate-300 cursor-pointer">
                    Set as Primary Contact Email
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  {editingEmailId && (
                    <button
                      type="button"
                      onClick={() => {
                        setEditingEmailId(null);
                        setEmailForm({ email: '', label: 'Personal', is_primary: false, display_order: 0 });
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
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white font-mono">{item.email}</span>
                      {item.is_primary && (
                        <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/30 text-[10px] font-semibold text-indigo-300">
                          Primary
                        </span>
                      )}
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
                  onChange={(e) => setEduForm({ ...eduForm, level: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                >
                  <option value="Doctorate">Doctorate</option>
                  <option value="Post Graduate">Post Graduate</option>
                  <option value="Graduate">Graduate</option>
                  <option value="Undergraduate">Undergraduate</option>
                  <option value="High School">High School</option>
                  <option value="Matriculation">Matriculation</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Stream / Field</label>
                <input
                  type="text"
                  value={eduForm.stream}
                  onChange={(e) => setEduForm({ ...eduForm, stream: e.target.value })}
                  placeholder="e.g. Computer Science & AI"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
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
                  onChange={(e) => setEduForm({ ...eduForm, currently_studying: e.target.checked })}
                  className="w-4 h-4 rounded text-indigo-600 bg-slate-950 border-slate-800 cursor-pointer"
                />
                <label htmlFor="edu_currently_studying" className="text-xs text-slate-300 cursor-pointer font-medium">
                  Currently Studying (In Progress)
                </label>
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
            {educations.map((edu) => (
              <div
                key={edu.id}
                className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <span className="text-[10px] uppercase font-bold text-purple-400">{edu.level}</span>
                  <h4 className="text-sm font-bold text-white">{edu.stream}</h4>
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
                        stream: edu.stream,
                        institution: edu.institution || '',
                        starting_month_year: edu.starting_month_year,
                        ending_month_year: edu.ending_month_year || '',
                        currently_studying: edu.currently_studying,
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
            ))}
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

          {/* Experience List */}
          <div className="space-y-3">
            {experiences.map((exp) => (
              <div
                key={exp.id}
                className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-white">{exp.role}</h4>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
                      {exp.work_mode}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
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
            ))}
            {experiences.length === 0 && (
              <p className="text-xs text-slate-500 py-6 text-center">No experience records configured yet.</p>
            )}
          </div>
        </div>
      )}

      {/* 5. SKILLS TAB (7-LEVEL CALIBRATION) */}
      {activeTab === 'skills' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">
              {editingSkillId ? 'Edit Skill & 7-Level Rating' : 'Add Skill & 7-Level Rating'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Skill Name</label>
                <input
                  type="text"
                  value={skillForm.name}
                  onChange={(e) => setSkillForm({ ...skillForm, name: e.target.value })}
                  placeholder="e.g. Distributed Consensus"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Category</label>
                <input
                  type="text"
                  value={skillForm.category}
                  onChange={(e) => setSkillForm({ ...skillForm, category: e.target.value })}
                  placeholder="e.g. Backend Architecture"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Display Ordering</label>
                <input
                  type="number"
                  min={0}
                  value={skillForm.ordering}
                  onChange={(e) => setSkillForm({ ...skillForm, ordering: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* 7-Level Rating Selector */}
            <div className="mt-4 pt-4 border-t border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-slate-300">Calibrated Mastery Level (1–7)</label>
                <span className="text-xs font-bold text-indigo-400 font-mono">
                  Level {skillForm.rating} — {SKILL_LEVEL_MAP[skillForm.rating] || 'Proficient'}
                </span>
              </div>
              <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
                {[1, 2, 3, 4, 5, 6, 7].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setSkillForm({ ...skillForm, rating: lvl })}
                    className={`py-2 rounded-xl text-xs font-bold transition-all cursor-pointer text-center ${
                      skillForm.rating === lvl
                        ? 'bg-indigo-600 text-white ring-2 ring-indigo-400/50 shadow-lg shadow-indigo-600/30'
                        : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-900'
                    }`}
                  >
                    <div>{lvl}</div>
                    <div className="text-[9px] font-normal truncate mt-0.5 hidden sm:block">
                      {SKILL_LEVEL_MAP[lvl]}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-800">
              <button
                onClick={handleSaveSkill}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-md"
              >
                {editingSkillId ? 'Update Skill' : 'Add Skill'}
              </button>
              {editingSkillId && (
                <button
                  onClick={() => {
                    setEditingSkillId(null);
                    setSkillForm({ name: '', category: 'Technical', rating: 4, ordering: 0 });
                  }}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs font-medium cursor-pointer"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Skill List */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {skills.map((sk) => (
              <div
                key={sk.id}
                className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-500">{sk.category}</span>
                  <h4 className="text-sm font-bold text-white">{sk.name}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-mono">
                      Rating {sk.rating} / 7
                    </span>
                    <span className="text-[11px] text-slate-400 font-medium">{sk.level_label}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => {
                      setEditingSkillId(sk.id);
                      setSkillForm({
                        name: sk.name,
                        category: sk.category,
                        rating: sk.rating,
                        ordering: sk.ordering
                      });
                    }}
                    className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg cursor-pointer"
                    title="Edit"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteSkill(sk.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg cursor-pointer"
                    title="Delete"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
            {skills.length === 0 && (
              <p className="col-span-full text-xs text-slate-500 py-6 text-center">No skills registered yet.</p>
            )}
          </div>
        </div>
      )}

      {/* 6. HOBBIES TAB */}
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
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Brain className="w-4 h-4 text-purple-400" />
              Completed Assessment Records ({assessmentHistory.length})
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {assessmentHistory.map((item) => (
                <div key={item.id} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-indigo-400 uppercase">{item.assessment_type}</span>
                    <span className="text-xs font-bold text-white font-mono">{item.result_code}</span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-200">{item.result_title}</h4>
                  <p className="text-xs text-slate-400 line-clamp-2">{item.summary}</p>
                  <div className="text-[10px] text-slate-500 pt-2 border-t border-slate-900 font-mono">
                    Completed: {new Date(item.completed_at).toLocaleDateString()}
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
            <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-800/40 text-xs text-indigo-200 space-y-1">
              <span className="font-bold text-indigo-300">Psychological Assessment Invariants:</span>
              <p className="text-slate-300">
                • <strong className="text-white">Communication</strong> is the mandatory core strength.
                <br />
                • Exactly <strong className="text-white">14 key strengths</strong> (13 derived + mandatory Communication).
                <br />
                • Exactly <strong className="text-white">7 weaknesses</strong> (growth blindspots).
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

                {/* 14 Key Strengths & 7 Weaknesses Side-by-Side */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* 14 Key Strengths (Communication Mandatory) */}
                  <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Award className="w-4 h-4" />
                        14 Key Strengths
                      </span>
                      <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        {synthesis.key_strengths.length} Strengths
                      </span>
                    </div>

                    <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                      {synthesis.key_strengths.map((str, idx) => {
                        const isMandatory = str.toLowerCase() === 'communication';
                        return (
                          <div
                            key={idx}
                            className={`p-2.5 rounded-xl border text-xs flex items-start gap-2.5 transition-colors ${
                              isMandatory
                                ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                                : 'bg-slate-900 border-slate-800 text-slate-300'
                            }`}
                          >
                            <span className="font-mono text-[10px] text-slate-500 font-bold shrink-0 mt-0.5">
                              #{idx + 1}
                            </span>
                            <div className="flex-1">
                              <span>{str}</span>
                              {isMandatory && (
                                <span className="ml-2 inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-emerald-500 text-slate-950 tracking-wider">
                                  Mandatory Core Strength
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                      {synthesis.key_strengths.length === 0 && (
                        <p className="text-xs text-slate-500 py-3 text-center">No strengths synthesized yet.</p>
                      )}
                    </div>
                  </div>

                  {/* 7 Weaknesses / Growth Areas */}
                  <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4" />
                        7 Growth Blindspots / Weaknesses
                      </span>
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
