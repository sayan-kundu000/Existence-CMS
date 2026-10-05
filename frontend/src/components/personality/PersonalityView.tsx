import React, { useState, useEffect } from 'react';
import {
  Brain,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Play,
  RotateCcw,
  CheckCircle2,
  BarChart3,
  Award,
  Layers,
  Flame,
  Compass,
  ArrowRight,
  Lock,
  Globe,
  Eye,
  EyeOff,
  Save,
  GitCompare,
  ChevronRight,
  X,
  Clock,
  Info,
  Download,
  Printer,
  Copy,
  Check,
  FileText
} from 'lucide-react';
import {
  AssessmentMeta,
  AssessmentResult,
  PersonalitySynthesis,
  QuestionItem,
  AnswerItem,
  PublicTabType,
  ResultComparisonResponse
} from '../../types';
import { api } from '../../services/api';
import { EmptyState } from '../common/EmptyState';

interface PersonalityViewProps {
  synthesis: PersonalitySynthesis | null;
  onRefreshSynthesis: () => void;
  onNavigate?: (tab: PublicTabType) => void;
}

interface SavedSessionMeta {
  sessionId: string;
  type: string;
  answeredCount: number;
  totalQuestions: number;
  savedAt: string;
}

export const PersonalityView: React.FC<PersonalityViewProps> = ({
  synthesis,
  onRefreshSynthesis,
  onNavigate
}) => {
  const [registry, setRegistry] = useState<AssessmentMeta[]>([]);
  const [history, setHistory] = useState<AssessmentResult[]>([]);
  const [activeSession, setActiveSession] = useState<{
    sessionId: string;
    type: string;
    questions: QuestionItem[];
    currentIdx: number;
    answers: Record<string, number>;
  } | null>(null);
  const [savedSessionMeta, setSavedSessionMeta] = useState<SavedSessionMeta | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'take' | 'history'>('overview');
  const [showQuestionGrid, setShowQuestionGrid] = useState<boolean>(false);

  // Modals
  const [detailResult, setDetailResult] = useState<AssessmentResult | null>(null);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [compareBaselineId, setCompareBaselineId] = useState<string>('');
  const [compareTargetId, setCompareTargetId] = useState<string>('');
  const [comparisonResult, setComparisonResult] = useState<ResultComparisonResponse | null>(null);
  const [comparing, setComparing] = useState(false);
  const [copiedDossier, setCopiedDossier] = useState(false);

  const generateDossierText = (result: AssessmentResult): string => {
    const lines: string[] = [];
    lines.push('================================================================');
    lines.push('EXISTENCE CMS — PSYCHOMETRIC ASSESSMENT DOSSIER');
    lines.push('CALIBRATED FOR: PLATFORM ADMINISTRATOR');
    lines.push('================================================================');
    lines.push(`Assessment Type   : ${result.assessment_type} (75 Questions)`);
    lines.push(`Result Code       : ${result.result_code}`);
    lines.push(`Result Title      : ${result.result_title}`);
    lines.push(`Version           : ${result.result_version || '1.0'}`);
    lines.push(`Completed At      : ${new Date(result.completed_at).toLocaleString()}`);
    lines.push(`Visibility        : ${result.is_public ?? true ? 'Public' : 'Private'}`);
    lines.push('');
    lines.push('----------------------------------------------------------------');
    lines.push('EXECUTIVE SUMMARY');
    lines.push('----------------------------------------------------------------');
    lines.push(result.summary || 'No summary available.');
    lines.push('');

    lines.push('----------------------------------------------------------------');
    lines.push('DIMENSIONAL SCORES & METRICS');
    lines.push('----------------------------------------------------------------');
    if (result.assessment_type === 'MBTI' && result.scores?.dimensions) {
      const dims = [
        { left: 'Extraversion (E)', right: 'Introversion (I)', leftKey: 'Extraversion', rightKey: 'Introversion' },
        { left: 'Sensing (S)', right: 'Intuition (N)', leftKey: 'Sensing', rightKey: 'Intuition' },
        { left: 'Thinking (T)', right: 'Feeling (F)', leftKey: 'Thinking', rightKey: 'Feeling' },
        { left: 'Judging (J)', right: 'Perceiving (P)', leftKey: 'Judging', rightKey: 'Perceiving' }
      ];
      dims.forEach(d => {
        const l = result.scores.dimensions[d.leftKey] ?? 50;
        const r = result.scores.dimensions[d.rightKey] ?? 50;
        lines.push(`${d.left}: ${l}% | ${d.right}: ${r}%`);
      });
    } else if (result.assessment_type === 'DISC' && result.scores?.percentages) {
      const dims = [
        { code: 'D', name: 'Dominance' },
        { code: 'I', name: 'Influence' },
        { code: 'S', name: 'Steadiness' },
        { code: 'C', name: 'Conscientiousness' }
      ];
      dims.forEach(d => {
        const val = result.scores.percentages[d.code] ?? 0;
        lines.push(`${d.code} (${d.name}): ${val}%`);
      });
    } else if (result.assessment_type === 'BIG_FIVE') {
      const dims = [
        { code: 'O', name: 'Openness to Experience' },
        { code: 'C', name: 'Conscientiousness' },
        { code: 'E', name: 'Extraversion' },
        { code: 'A', name: 'Agreeableness' },
        { code: 'N', name: 'Neuroticism' }
      ];
      dims.forEach(d => {
        const val = result.scores?.[d.code] ?? 50;
        lines.push(`${d.name} (${d.code}): ${val}%`);
      });
    } else if (result.scores) {
      lines.push(JSON.stringify(result.scores, null, 2));
    }
    lines.push('');

    lines.push('----------------------------------------------------------------');
    lines.push('ASSESSMENT-BASED STRENGTHS');
    lines.push('----------------------------------------------------------------');
    if (result.strengths && result.strengths.length > 0) {
      result.strengths.forEach((s, i) => lines.push(`  ${i + 1}. ${s}`));
    } else {
      lines.push('  None recorded.');
    }
    lines.push('');

    lines.push('----------------------------------------------------------------');
    lines.push('POTENTIAL DEVELOPMENT AREAS');
    lines.push('----------------------------------------------------------------');
    if (result.weaknesses && result.weaknesses.length > 0) {
      result.weaknesses.forEach((w, i) => lines.push(`  ${i + 1}. ${w}`));
    } else {
      lines.push('  None recorded.');
    }
    lines.push('');

    lines.push('----------------------------------------------------------------');
    lines.push('IDENTIFIED SOFT SKILLS');
    lines.push('----------------------------------------------------------------');
    if (result.soft_skills && result.soft_skills.length > 0) {
      result.soft_skills.forEach((sk, i) => lines.push(`  ${i + 1}. ${sk}`));
    } else {
      lines.push('  None recorded.');
    }
    lines.push('');
    lines.push('================================================================');
    lines.push(`CONFIDENTIAL ASSESSMENT REPORT — GENERATED ON ${new Date().toISOString()}`);
    lines.push('================================================================');
    return lines.join('\n');
  };

  const handleDownloadDossier = (result: AssessmentResult) => {
    const text = generateDossierText(result);
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${result.assessment_type}_${result.result_code}_Assessment_Dossier.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleDownloadJson = (result: AssessmentResult) => {
    const data = JSON.stringify(result, null, 2);
    const blob = new Blob([data], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${result.assessment_type}_${result.result_code}_Result_Data.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCopyDossier = async (result: AssessmentResult) => {
    try {
      const text = generateDossierText(result);
      await navigator.clipboard.writeText(text);
      setCopiedDossier(true);
      setTimeout(() => setCopiedDossier(false), 2500);
    } catch {
      alert('Could not copy to clipboard.');
    }
  };

  const handlePrintResult = () => {
    window.print();
  };

  useEffect(() => {
    loadRegistryAndHistory();
    checkSavedSession();
  }, []);

  const loadRegistryAndHistory = async () => {
    try {
      const [regData, histData] = await Promise.all([
        api.getAssessmentRegistry(),
        api.getAssessmentHistory()
      ]);
      setRegistry(regData);
      setHistory(histData);
    } catch (e) {
      console.error('Failed to load assessment data', e);
    }
  };

  const checkSavedSession = () => {
    try {
      const raw = localStorage.getItem('existence_saved_session');
      if (raw) {
        const parsed = JSON.parse(raw);
        setSavedSessionMeta(parsed);
      } else {
        setSavedSessionMeta(null);
      }
    } catch {
      setSavedSessionMeta(null);
    }
  };

  const handleStartTest = async (testType: string) => {
    try {
      const session = await api.startAssessment(testType);
      setActiveSession({
        sessionId: session.session_id,
        type: session.assessment_type,
        questions: session.questions,
        currentIdx: 0,
        answers: {}
      });
      setSelectedTab('take');
      setShowQuestionGrid(false);
    } catch (err: any) {
      alert(`Could not start assessment: ${err.message}`);
    }
  };

  const handleResumeSavedSession = async (sessionIdToResume?: string) => {
    const sId = sessionIdToResume || savedSessionMeta?.sessionId;
    if (!sId) return;

    try {
      const resumed = await api.resumeAssessmentSession(sId);
      setActiveSession({
        sessionId: resumed.session_id,
        type: resumed.assessment_type,
        questions: resumed.questions,
        currentIdx: Math.min(resumed.progress_index || 0, resumed.questions.length - 1),
        answers: resumed.answers || {}
      });
      setSelectedTab('take');
      setShowQuestionGrid(false);
    } catch (err: any) {
      alert(`Could not resume assessment: ${err.message}`);
      localStorage.removeItem('existence_saved_session');
      setSavedSessionMeta(null);
    }
  };

  const handleSaveAndExit = async () => {
    if (!activeSession) return;
    try {
      // 1. Send all answered responses to backend
      const formattedAnswers: AnswerItem[] = Object.entries(activeSession.answers).map(([qId, val]) => {
        const qObj = activeSession.questions.find((q) => q.id === qId);
        return {
          question_id: qId,
          dimension: qObj ? qObj.dimension : 'UNKNOWN',
          selected_value: val
        };
      });

      if (formattedAnswers.length > 0) {
        await api.saveAssessmentResponses(activeSession.sessionId, formattedAnswers);
      }

      // 2. Update progress on backend
      await api.updateAssessmentProgress(activeSession.sessionId, activeSession.currentIdx);

      // 3. Save session in localStorage
      const meta: SavedSessionMeta = {
        sessionId: activeSession.sessionId,
        type: activeSession.type,
        answeredCount: Object.keys(activeSession.answers).length,
        totalQuestions: activeSession.questions.length,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem('existence_saved_session', JSON.stringify(meta));
      setSavedSessionMeta(meta);

      setActiveSession(null);
      setSelectedTab('overview');
      alert('Assessment progress saved successfully. You can resume at any time.');
    } catch (err: any) {
      alert(`Could not save session: ${err.message}`);
    }
  };

  const handleDiscardSavedSession = () => {
    if (confirm('Discard your saved in-progress assessment? This cannot be undone.')) {
      localStorage.removeItem('existence_saved_session');
      setSavedSessionMeta(null);
    }
  };

  const handleSelectAnswer = (questionId: string, value: number) => {
    if (!activeSession) return;
    setActiveSession({
      ...activeSession,
      answers: { ...activeSession.answers, [questionId]: value }
    });
  };

  const handleSubmitAnswers = async () => {
    if (!activeSession) return;
    const answeredCount = Object.keys(activeSession.answers).length;
    const totalQ = activeSession.questions.length;

    if (answeredCount < totalQ) {
      if (
        !confirm(
          `You have answered ${answeredCount} of ${totalQ} items. Unanswered items will receive a neutral default score. Complete and generate psychometric results?`
        )
      ) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const formattedAnswers: AnswerItem[] = activeSession.questions.map((q) => ({
        question_id: q.id,
        dimension: q.dimension,
        selected_value: activeSession.answers[q.id] || 3 // Default neutral if unanswered
      }));

      const res = await api.submitAssessment(activeSession.sessionId, formattedAnswers);
      localStorage.removeItem('existence_saved_session');
      setSavedSessionMeta(null);
      setActiveSession(null);
      setSelectedTab('overview');
      setDetailResult(res);
      await loadRegistryAndHistory();
      onRefreshSynthesis();
    } catch (err: any) {
      alert(`Submission error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleVisibility = async (result: AssessmentResult) => {
    const pin = prompt('Enter 4-digit Action PIN to toggle visibility of this assessment result:');
    if (!pin) return;

    try {
      const newStatus = !(result.is_public ?? true);
      const updated = await api.toggleResultVisibility(result.id, newStatus, pin);
      // Update local history
      setHistory((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      if (detailResult && detailResult.id === updated.id) {
        setDetailResult(updated);
      }
      onRefreshSynthesis();
      alert(`Result visibility updated to: ${newStatus ? 'PUBLIC' : 'PRIVATE'}`);
    } catch (err: any) {
      alert(`Failed to update visibility: ${err.message}`);
    }
  };

  const handleRunComparison = async () => {
    if (!compareBaselineId || !compareTargetId) {
      alert('Please select both a baseline attempt and a target attempt to compare.');
      return;
    }
    if (compareBaselineId === compareTargetId) {
      alert('Please select two distinct assessment attempts.');
      return;
    }

    setComparing(true);
    try {
      const res = await api.compareAssessmentResults(compareBaselineId, compareTargetId);
      setComparisonResult(res);
    } catch (err: any) {
      alert(`Comparison failed: ${err.message}`);
    } finally {
      setComparing(false);
    }
  };

  // =========================================================================
  // SUB-RENDER: ASSESSMENT RUNNER
  // =========================================================================
  if (activeSession) {
    const q = activeSession.questions[activeSession.currentIdx];
    const totalQ = activeSession.questions.length;
    const answeredCount = Object.keys(activeSession.answers).length;
    const progress = Math.round(((activeSession.currentIdx + 1) / totalQ) * 100);
    const answeredPct = Math.round((answeredCount / totalQ) * 100);
    const currentVal = activeSession.answers[q.id];

    return (
      <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6 space-y-6 animate-fadeIn">
        {/* Session Progress Header */}
        <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-semibold text-slate-400">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30">
                {activeSession.type} v1.0
              </span>
              <span className="text-white text-sm font-bold">Standardized Psychometric Assessment</span>
              <span className="text-slate-500 font-mono">({totalQ} Questions)</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setShowQuestionGrid(!showQuestionGrid)}
                className="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-750 text-indigo-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5 font-medium"
              >
                <span>Question Matrix ({answeredCount}/{totalQ})</span>
              </button>

              <button
                type="button"
                onClick={handleSaveAndExit}
                className="px-3 py-1.5 rounded-xl border border-indigo-500/30 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 transition-all cursor-pointer flex items-center gap-1.5"
                title="Save answers and resume later"
              >
                <Save className="w-3.5 h-3.5" />
                <span>Save & Exit</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  if (confirm('Exit without saving? Unsaved changes in this session may be lost.')) {
                    setActiveSession(null);
                    setSelectedTab('overview');
                  }
                }}
                className="px-3 py-1.5 rounded-xl border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white transition-all cursor-pointer"
              >
                Exit
              </button>
            </div>
          </div>

          {/* Progress Indicators */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span className="text-indigo-400">
                Question {activeSession.currentIdx + 1} of {totalQ} ({progress}% progress)
              </span>
              <span className="text-emerald-400">
                {answeredCount} of {totalQ} answered ({answeredPct}%)
              </span>
            </div>
            <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800/80">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-full transition-all duration-300"
                style={{ width: `${Math.max(progress, answeredPct)}%` }}
              />
            </div>
          </div>

          {/* Question Grid Matrix */}
          {showQuestionGrid && (
            <div className="pt-4 border-t border-slate-800/80 space-y-3 animate-fadeIn">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-300">Quick Navigation Palette:</span>
                <div className="flex items-center gap-3 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Answered</span>
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span> Current</span>
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-slate-800"></span> Unanswered</span>
                </div>
              </div>
              <div className="grid grid-cols-8 sm:grid-cols-11 md:grid-cols-15 gap-1.5 sm:gap-2 max-h-48 overflow-y-auto p-1">
                {activeSession.questions.map((item, idx) => {
                  const isAnswered = activeSession.answers[item.id] !== undefined;
                  const isCurrent = activeSession.currentIdx === idx;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setActiveSession({ ...activeSession, currentIdx: idx })}
                      className={`h-8 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer flex items-center justify-center ${
                        isCurrent
                          ? 'bg-indigo-600 text-white ring-2 ring-indigo-400 shadow-md shadow-indigo-600/50 scale-105'
                          : isAnswered
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30'
                          : 'bg-slate-900 border border-slate-800 text-slate-500 hover:border-slate-700 hover:text-slate-300'
                      }`}
                      title={`Item ${idx + 1}: Dimension ${item.dimension}`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Question Card */}
        <div className="glass-panel p-8 sm:p-12 rounded-3xl border border-slate-800 shadow-2xl relative space-y-6">
          <div>
            <div className="flex items-center justify-between gap-2 mb-4">
              <span className="inline-block px-3 py-1 rounded-lg text-[10px] font-bold tracking-wider uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Question {activeSession.currentIdx + 1} of {totalQ} · Dimension {q.dimension}
              </span>
              {currentVal !== undefined && (
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Recorded: Option {currentVal}
                </span>
              )}
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white leading-relaxed">
              "{q.text}"
            </h2>
          </div>

          {/* 5-point Likert Scale */}
          <div className="space-y-4 my-6">
            <div className="grid grid-cols-5 gap-2 sm:gap-4">
              {[
                { val: 1, label: 'Strongly Disagree' },
                { val: 2, label: 'Disagree' },
                { val: 3, label: 'Neutral' },
                { val: 4, label: 'Agree' },
                { val: 5, label: 'Strongly Agree' }
              ].map((opt) => (
                <button
                  key={opt.val}
                  type="button"
                  onClick={() => handleSelectAnswer(q.id, opt.val)}
                  className={`p-3 sm:p-4 rounded-2xl border text-center transition-all cursor-pointer ${
                    currentVal === opt.val
                      ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/40 scale-105'
                      : 'bg-slate-900/80 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-850'
                  }`}
                >
                  <span className="block text-xl sm:text-2xl font-black font-mono mb-1">{opt.val}</span>
                  <span className="block text-[10px] sm:text-xs font-medium opacity-90 leading-tight">
                    {opt.label}
                  </span>
                </button>
              ))}
            </div>

            {(q.positive_pole || q.negative_pole) && (
              <div className="flex justify-between text-[11px] text-slate-500 px-2 italic">
                <span>← {q.negative_pole || 'Low preference'}</span>
                <span>{q.positive_pole || 'High preference'} →</span>
              </div>
            )}
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center justify-between pt-6 border-t border-slate-800">
            <button
              type="button"
              disabled={activeSession.currentIdx === 0}
              onClick={() => setActiveSession({ ...activeSession, currentIdx: activeSession.currentIdx - 1 })}
              className="px-5 py-2.5 rounded-xl border border-slate-800 hover:border-slate-700 text-xs font-semibold text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed transition-all cursor-pointer"
            >
              Previous
            </button>

            <div className="flex items-center gap-3">
              {activeSession.currentIdx < totalQ - 1 ? (
                <button
                  type="button"
                  onClick={() => setActiveSession({ ...activeSession, currentIdx: activeSession.currentIdx + 1 })}
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all cursor-pointer flex items-center gap-1.5"
                >
                  <span>Next Question</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="button"
                  disabled={submitting}
                  onClick={handleSubmitAnswers}
                  className="px-8 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 transition-all cursor-pointer flex items-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{submitting ? 'Scoring Assessment...' : 'Finalize & Generate Result'}</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // =========================================================================
  // MAIN DASHBOARD VIEW
  // =========================================================================
  return (
    <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2.5 mb-2">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Brain className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold tracking-wider uppercase text-indigo-400">
              Personality Intelligence Engine
            </span>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">
            Psychometric Personality Profile
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Standardized multi-framework personality measurement across MBTI, DISC, and Big Five/OCEAN.
            Results are calibrated directly from assessment session responses.
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center p-1 rounded-2xl bg-slate-900 border border-slate-800">
          <button
            onClick={() => setSelectedTab('overview')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              selectedTab === 'overview'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Overview & Synthesis
          </button>
          <button
            onClick={() => setSelectedTab('take')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              selectedTab === 'take'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Take Assessments
          </button>
          <button
            onClick={() => setSelectedTab('history')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              selectedTab === 'history'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>History</span>
            {history.length > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-800 text-slate-300">
                {history.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Admin Verification & Assessment Integrity Policy Banner */}
      <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-500/20 flex items-start gap-3.5 shadow-lg">
        <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs text-indigo-200/90 leading-relaxed space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white uppercase tracking-wider text-[11px] bg-indigo-500/20 px-2 py-0.5 rounded-md border border-indigo-500/30">
              Admin Exclusive Assessment Suite
            </span>
            <span className="text-[11px] text-indigo-300 font-semibold">75 Questions per Framework (MBTI · DISC · Big Five)</span>
          </div>
          <p>
            The psychometric assessment tests are calibrated exclusively for the <strong>platform administrator</strong>. To maintain profile authenticity and psychological identity integrity, modifying the administrator's <strong>Email ID</strong>, <strong>Mobile number</strong>, or <strong>LinkedIn account</strong> will automatically reset all assessment tests and results, requiring the admin to give all assessment tests again.
          </p>
        </div>
      </div>

      {/* Resume Banner If Session In Progress */}
      {savedSessionMeta && (
        <div className="glass-card p-5 rounded-2xl border border-indigo-500/30 bg-indigo-950/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">
                Unfinished {savedSessionMeta.type} Assessment Available
              </h4>
              <p className="text-xs text-slate-400">
                Saved with {savedSessionMeta.answeredCount} of {savedSessionMeta.totalQuestions} questions answered on{' '}
                {new Date(savedSessionMeta.savedAt).toLocaleDateString()}.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 self-end sm:self-auto">
            <button
              onClick={() => handleResumeSavedSession()}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Resume Session</span>
            </button>
            <button
              onClick={handleDiscardSavedSession}
              className="px-3 py-2 rounded-xl border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-rose-300 text-xs transition-all cursor-pointer"
            >
              Discard
            </button>
          </div>
        </div>
      )}

      {/* VIEW: OVERVIEW & SYNTHESIS */}
      {selectedTab === 'overview' && (
        <div className="space-y-8">
          {!synthesis?.has_assessments ? (
            <EmptyState
              icon={Brain}
              title="Personality assessment not completed"
              description="No assessment results have been recorded yet. Complete the MBTI, DISC, or Big Five assessments to generate synthesized behavioral profiles, soft skills, and strengths."
              actionText="Take Your First Assessment"
              onAction={() => setSelectedTab('take')}
            />
          ) : (
            <>
              {/* Dynamic Assessment Evaluation Basis Indicator */}
              <div className="p-5 rounded-3xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start md:items-center gap-3.5">
                  <div className="p-2.5 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shrink-0">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-sm font-bold text-white">
                        Evaluation Basis: {synthesis.assessments_completed.length} Completed Test{synthesis.assessments_completed.length !== 1 ? 's' : ''}
                      </h4>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                        {synthesis.assessments_completed.length === 1 && 'Evaluated on 1 Test'}
                        {synthesis.assessments_completed.length === 2 && 'Evaluated on 2 Tests'}
                        {synthesis.assessments_completed.length === 3 && 'Evaluated on 3 Tests (Complete)'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                      {synthesis.summary_notes || `Strengths and development areas are evaluated dynamically on the basis of your ${synthesis.assessments_completed.length} completed test(s).`}
                    </p>
                  </div>
                </div>
                {synthesis.assessments_completed.length < 3 && (
                  <button
                    onClick={() => setSelectedTab('take')}
                    className="shrink-0 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md flex items-center gap-2 cursor-pointer self-start md:self-auto"
                  >
                    <span>Take Next Assessment</span>
                    <Play className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Latest Completed Test Badges */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* MBTI Card */}
                <div className="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold tracking-wider uppercase text-indigo-400">
                        MBTI Framework
                      </span>
                      {synthesis?.latest_results.MBTI ? (
                        <div className="flex items-center gap-1.5">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            synthesis.latest_results.MBTI.is_public ?? true
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-slate-800 text-slate-400 border border-slate-700'
                          }`}>
                            {synthesis.latest_results.MBTI.is_public ?? true ? 'Public' : 'Private'}
                          </span>
                        </div>
                      ) : (
                        <span className="text-[10px] text-slate-500">Not taken</span>
                      )}
                    </div>
                    {synthesis?.latest_results.MBTI ? (
                      <>
                        <h3 className="text-2xl font-black text-white tracking-tight mb-1 font-mono">
                          {synthesis.latest_results.MBTI.result_code}
                        </h3>
                        <p className="text-xs font-medium text-slate-300 mb-3">
                          {synthesis.latest_results.MBTI.result_title}
                        </p>
                        <p className="text-[11px] text-slate-400 line-clamp-3 mb-4">
                          {synthesis.latest_results.MBTI.summary}
                        </p>
                      </>
                    ) : (
                      <div className="py-4 text-xs text-slate-500 italic">
                        Cognitive preferences not established.
                      </div>
                    )}
                  </div>
                  <div className="space-y-2 pt-4 border-t border-slate-800/80">
                    {synthesis?.latest_results.MBTI && (
                      <button
                        onClick={() => setDetailResult(synthesis.latest_results.MBTI)}
                        className="w-full py-2 rounded-xl text-xs font-semibold bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-all cursor-pointer flex items-center justify-center gap-1"
                      >
                        <BarChart3 className="w-3.5 h-3.5" />
                        <span>View MBTI Analysis</span>
                      </button>
                    )}
                    <button
                      onClick={() => handleStartTest('MBTI')}
                      className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-all cursor-pointer"
                    >
                      <Play className="w-3.5 h-3.5" />
                      <span>{synthesis?.latest_results.MBTI ? 'Retake MBTI' : 'Start MBTI'}</span>
                    </button>
                  </div>
                </div>

                {/* DISC Card */}
                <div className="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold tracking-wider uppercase text-purple-400">
                        DISC Behavioral
                      </span>
                      {synthesis?.latest_results.DISC ? (
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          synthesis.latest_results.DISC.is_public ?? true
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-slate-800 text-slate-400 border border-slate-700'
                        }`}>
                          {synthesis.latest_results.DISC.is_public ?? true ? 'Public' : 'Private'}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-500">Not taken</span>
                      )}
                    </div>
                    {synthesis?.latest_results.DISC ? (
                      <>
                        <h3 className="text-2xl font-black text-white tracking-tight mb-1 font-mono">
                          {synthesis.latest_results.DISC.result_code}
                        </h3>
                        <p className="text-xs font-medium text-slate-300 mb-3">
                          {synthesis.latest_results.DISC.result_title}
                        </p>
                        <p className="text-[11px] text-slate-400 line-clamp-3 mb-4">
                          {synthesis.latest_results.DISC.summary}
                        </p>
                      </>
                    ) : (
                      <div className="py-4 text-xs text-slate-500 italic">
                        Workplace behavior profile not taken.
                      </div>
                    )}
                  </div>
                  <div className="space-y-2 pt-4 border-t border-slate-800/80">
                    {synthesis?.latest_results.DISC && (
                      <button
                        onClick={() => setDetailResult(synthesis.latest_results.DISC)}
                        className="w-full py-2 rounded-xl text-xs font-semibold bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 transition-all cursor-pointer flex items-center justify-center gap-1"
                      >
                        <BarChart3 className="w-3.5 h-3.5" />
                        <span>View DISC Analysis</span>
                      </button>
                    )}
                    <button
                      onClick={() => handleStartTest('DISC')}
                      className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-all cursor-pointer"
                    >
                      <Play className="w-3.5 h-3.5" />
                      <span>{synthesis?.latest_results.DISC ? 'Retake DISC' : 'Start DISC'}</span>
                    </button>
                  </div>
                </div>

                {/* Big Five Card */}
                <div className="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold tracking-wider uppercase text-amber-400">
                        Big Five / OCEAN
                      </span>
                      {synthesis?.latest_results.BIG_FIVE ? (
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          synthesis.latest_results.BIG_FIVE.is_public ?? true
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-slate-800 text-slate-400 border border-slate-700'
                        }`}>
                          {synthesis.latest_results.BIG_FIVE.is_public ?? true ? 'Public' : 'Private'}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-500">Not taken</span>
                      )}
                    </div>
                    {synthesis?.latest_results.BIG_FIVE ? (
                      <>
                        <h3 className="text-lg font-bold text-white tracking-tight mb-1 font-mono">
                          {synthesis.latest_results.BIG_FIVE.result_title}
                        </h3>
                        <div className="grid grid-cols-5 gap-1 my-3 text-center">
                          {['O', 'C', 'E', 'A', 'N'].map((trait) => (
                            <div key={trait} className="p-1 rounded bg-slate-900 border border-slate-800">
                              <span className="block text-[9px] text-slate-500">{trait}</span>
                              <span className="text-[11px] font-bold text-amber-300 font-mono">
                                {synthesis?.latest_results.BIG_FIVE?.scores[trait] ?? 0}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </>
                    ) : (
                      <div className="py-4 text-xs text-slate-500 italic">
                        Five-factor trait index not yet scored.
                      </div>
                    )}
                  </div>
                  <div className="space-y-2 pt-4 border-t border-slate-800/80">
                    {synthesis?.latest_results.BIG_FIVE && (
                      <button
                        onClick={() => setDetailResult(synthesis.latest_results.BIG_FIVE)}
                        className="w-full py-2 rounded-xl text-xs font-semibold bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 transition-all cursor-pointer flex items-center justify-center gap-1"
                      >
                        <BarChart3 className="w-3.5 h-3.5" />
                        <span>View Big Five Analysis</span>
                      </button>
                    )}
                    <button
                      onClick={() => handleStartTest('BIG_FIVE')}
                      className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-all cursor-pointer"
                    >
                      <Play className="w-3.5 h-3.5" />
                      <span>{synthesis?.latest_results.BIG_FIVE ? 'Retake Big Five' : 'Start Big Five'}</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Synthesized Strengths & Weaknesses Layer (Evaluated per Completed Tests) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                {/* Assessment-Derived Strengths */}
                <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4" />
                        11 Core Strengths
                      </h3>
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        Evaluated on {synthesis.assessments_completed.length} completed test{synthesis.assessments_completed.length !== 1 ? 's' : ''} ({synthesis.assessments_completed.join(', ')})
                      </p>
                    </div>
                    <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-lg shrink-0">
                      {synthesis.key_strengths.length} Core Strengths
                    </span>
                  </div>

                  <ul className="space-y-2.5">
                    {synthesis.key_strengths.map((st, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-3 text-xs rounded-xl p-2.5 border bg-slate-900/60 border-slate-800/80 text-slate-300 transition-all hover:border-slate-700/80"
                      >
                        <span className="font-mono text-[10px] font-bold text-emerald-400 shrink-0 mt-0.5">
                          #{i + 1}
                        </span>
                        <span className="flex-1 leading-relaxed">{st}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Potential Development Areas / Growth Blindspots */}
                <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Potential Development Areas
                      </h3>
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        Evaluated on {synthesis.assessments_completed.length} completed test{synthesis.assessments_completed.length !== 1 ? 's' : ''} ({synthesis.assessments_completed.join(', ')})
                      </p>
                    </div>
                    <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-lg shrink-0">
                      {synthesis.key_weaknesses.length} Growth Areas
                    </span>
                  </div>

                  <ul className="space-y-2.5">
                    {synthesis.key_weaknesses.map((wk, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-3 text-xs rounded-xl p-2.5 border bg-slate-900/60 border-slate-800/80 text-slate-300"
                      >
                        <span className="font-mono text-[10px] font-bold text-amber-500 shrink-0 mt-0.5">
                          #{i + 1}
                        </span>
                        <span className="flex-1 leading-relaxed">{wk}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Psychometric Architecture Disclaimer */}
              <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/50 flex items-start gap-3 text-xs text-slate-400">
                <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <p className="leading-relaxed">
                  <strong className="text-slate-200">Domain Separation Architecture: </strong>
                  Personality traits are psychometric preferences measured from structured test responses.
                  They are strictly independent from the 1–7 Skill Engine proficiency ratings and should be understood as
                  indicated preferences rather than absolute factual capabilities.
                </p>
              </div>
            </>
          )}
        </div>
      )}

      {/* VIEW: TAKE ASSESSMENTS */}
      {selectedTab === 'take' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {registry.map((test) => (
            <div
              key={test.type}
              className="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between shadow-xl hover:border-slate-700 transition-all"
            >
              <div>
                <span className="px-3 py-1 rounded-lg text-[10px] font-bold tracking-wider uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-3 inline-block">
                  {test.type} v1.0
                </span>
                <h3 className="text-lg font-bold text-white tracking-tight mb-1">
                  {test.name}
                </h3>
                <p className="text-xs font-medium text-slate-400 mb-3">{test.tagline}</p>
                <p className="text-xs text-slate-300 leading-relaxed mb-4">{test.description}</p>

                <div className="space-y-1.5 mb-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 font-mono">
                  <div className="flex justify-between">
                    <span>Dimensions:</span>
                    <span className="text-indigo-300 font-bold">{test.dimensions.join(' · ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Questions:</span>
                    <span className="text-slate-200">{test.question_count} items</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Estimated Duration:</span>
                    <span className="text-slate-200">{test.estimated_minutes} min</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleStartTest(test.type)}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
              >
                <Play className="w-4 h-4" />
                <span>Launch Assessment Session</span>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* VIEW: HISTORY */}
      {selectedTab === 'history' && (
        <div className="space-y-6">
          {/* Header Action: Compare */}
          {history.length >= 2 && (
            <div className="flex justify-end">
              <button
                onClick={() => {
                  setShowCompareModal(true);
                  setComparisonResult(null);
                  setCompareBaselineId(history[1]?.session_id || '');
                  setCompareTargetId(history[0]?.session_id || '');
                }}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
              >
                <GitCompare className="w-4 h-4" />
                <span>Compare Assessment Attempts</span>
              </button>
            </div>
          )}

          {history.length === 0 ? (
            <EmptyState
              icon={Brain}
              title="No assessment history"
              description="Historical assessment records will appear here as you complete tests."
            />
          ) : (
            <div className="space-y-4">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="glass-card p-5 sm:p-6 rounded-2xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-slate-700 transition-all"
                >
                  <div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {item.assessment_type} v{item.result_version || '1.0'}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        item.is_public ?? true
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {item.is_public ?? true ? 'Public' : 'Private'}
                      </span>
                      <span className="text-xs font-mono text-slate-500">
                        {new Date(item.completed_at).toLocaleDateString()} at{' '}
                        {new Date(item.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-white">
                      {item.result_code} — {item.result_title}
                    </h4>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2 max-w-2xl">{item.summary}</p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
                    <button
                      type="button"
                      onClick={() => handleDownloadDossier(item)}
                      className="p-2 rounded-xl border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-indigo-300 transition-all cursor-pointer"
                      title="Download Dossier (.txt)"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleToggleVisibility(item)}
                      className="p-2 rounded-xl border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white transition-all cursor-pointer"
                      title={item.is_public ?? true ? 'Make Private' : 'Make Public'}
                    >
                      {item.is_public ?? true ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4 text-amber-400" />}
                    </button>
                    <button
                      onClick={() => setDetailResult(item)}
                      className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-indigo-300 hover:text-white text-xs font-semibold transition-all cursor-pointer flex items-center gap-1"
                    >
                      <BarChart3 className="w-3.5 h-3.5" />
                      <span>View Breakdown</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =====================================================================
          MODAL: STRUCTURED RESULT DETAIL & VISUALIZATION
         ===================================================================== */}
      {detailResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="glass-panel w-full max-w-3xl rounded-3xl border border-slate-800 shadow-2xl p-6 sm:p-8 space-y-6 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 rounded-lg text-xs font-bold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {detailResult.assessment_type} v{detailResult.result_version || '1.0'}
                </span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                  detailResult.is_public ?? true
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                }`}>
                  {detailResult.is_public ?? true ? 'Public Visibility' : 'Private'}
                </span>
              </div>
              <button
                onClick={() => setDetailResult(null)}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 transition-all cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Title & Code */}
            <div>
              <span className="text-3xl font-black text-white font-mono tracking-tight block">
                {detailResult.result_code}
              </span>
              <h2 className="text-lg font-bold text-slate-200 mt-0.5">
                {detailResult.result_title}
              </h2>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                {detailResult.summary}
              </p>
            </div>

            {/* VISUALIZATION BY FRAMEWORK */}
            {detailResult.assessment_type === 'MBTI' && detailResult.scores?.dimensions && (
              <div className="space-y-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  MBTI Bipolar Preference Dimensions
                </h4>
                <div className="space-y-3.5">
                  {[
                    { left: 'Extraversion', right: 'Introversion', leftCode: 'E', rightCode: 'I' },
                    { left: 'Sensing', right: 'Intuition', leftCode: 'S', rightCode: 'N' },
                    { left: 'Thinking', right: 'Feeling', leftCode: 'T', rightCode: 'F' },
                    { left: 'Judging', right: 'Perceiving', leftCode: 'J', rightCode: 'P' }
                  ].map((dim) => {
                    const leftPct = detailResult.scores.dimensions[dim.left] ?? 50;
                    const rightPct = detailResult.scores.dimensions[dim.right] ?? 50;
                    const isLeftDominant = leftPct >= rightPct;

                    return (
                      <div key={dim.left} className="space-y-1 text-xs">
                        <div className="flex justify-between font-mono">
                          <span className={`${isLeftDominant ? 'font-bold text-indigo-400' : 'text-slate-400'}`}>
                            {dim.left} ({leftPct}%)
                          </span>
                          <span className={`${!isLeftDominant ? 'font-bold text-indigo-400' : 'text-slate-400'}`}>
                            {dim.right} ({rightPct}%)
                          </span>
                        </div>
                        {/* Bipolar Dual Bar */}
                        <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden flex border border-slate-800">
                          <div
                            className={`h-full transition-all duration-300 ${
                              isLeftDominant ? 'bg-indigo-500' : 'bg-slate-800'
                            }`}
                            style={{ width: `${leftPct}%` }}
                          />
                          <div
                            className={`h-full transition-all duration-300 ${
                              !isLeftDominant ? 'bg-indigo-500' : 'bg-slate-800'
                            }`}
                            style={{ width: `${rightPct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {detailResult.assessment_type === 'DISC' && detailResult.scores?.percentages && (
              <div className="space-y-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-purple-400">
                  DISC Dimension Distribution
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    { key: 'D', label: 'Dominance', color: 'from-rose-500 to-red-500' },
                    { key: 'I', label: 'Influence', color: 'from-amber-500 to-yellow-500' },
                    { key: 'S', label: 'Steadiness', color: 'from-emerald-500 to-teal-500' },
                    { key: 'C', label: 'Conscientiousness', color: 'from-blue-500 to-cyan-500' }
                  ].map((dim) => {
                    const score = detailResult.scores.percentages[dim.key] ?? 0;
                    return (
                      <div key={dim.key} className="space-y-1 p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                        <div className="flex justify-between text-xs">
                          <span className="font-bold text-slate-300">{dim.label}</span>
                          <span className="font-mono font-bold text-white">{score}%</span>
                        </div>
                        <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                          <div className={`h-full bg-gradient-to-r ${dim.color}`} style={{ width: `${score}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {detailResult.assessment_type === 'BIG_FIVE' && detailResult.scores && (
              <div className="space-y-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  Five-Factor Percentile Ratings
                </h4>
                <div className="space-y-3">
                  {[
                    { key: 'O', label: 'Openness to Experience' },
                    { key: 'C', label: 'Conscientiousness' },
                    { key: 'E', label: 'Extraversion' },
                    { key: 'A', label: 'Agreeableness' },
                    { key: 'N', label: 'Neuroticism' }
                  ].map((dim) => {
                    const score = detailResult.scores[dim.key] ?? 50;
                    return (
                      <div key={dim.key} className="space-y-1 text-xs">
                        <div className="flex justify-between font-mono">
                          <span className="font-bold text-slate-300">{dim.label}</span>
                          <span className="font-bold text-amber-300">{score}%</span>
                        </div>
                        <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800/80">
                          <div
                            className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
                            style={{ width: `${score}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Strengths & Development Areas */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-2">
                <h5 className="text-[11px] font-bold uppercase text-emerald-400 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Assessment-Based Strengths</span>
                </h5>
                <ul className="space-y-1 text-xs text-slate-300">
                  {(detailResult.strengths || []).map((s, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-emerald-500">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-2">
                <h5 className="text-[11px] font-bold uppercase text-amber-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Potential Development Areas</span>
                </h5>
                <ul className="space-y-1 text-xs text-slate-300">
                  {(detailResult.weaknesses || []).map((w, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-amber-500">•</span>
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Footer Actions: Take Out Results & Visibility */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-800">
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleToggleVisibility(detailResult)}
                  className="px-3 py-1.5 rounded-xl border border-slate-800 hover:border-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5"
                >
                  {detailResult.is_public ?? true ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  <span>{detailResult.is_public ?? true ? 'Make Private' : 'Make Public'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleCopyDossier(detailResult)}
                  className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5"
                  title="Copy formatted result dossier to clipboard"
                >
                  {copiedDossier ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedDossier ? 'Copied Dossier!' : 'Copy Dossier'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleDownloadDossier(detailResult)}
                  className="px-3 py-1.5 rounded-xl bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-500/30 text-xs font-semibold text-indigo-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5"
                  title="Download complete psychological result dossier (.txt)"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Dossier</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleDownloadJson(detailResult)}
                  className="px-3 py-1.5 rounded-xl bg-purple-600/10 hover:bg-purple-600/20 border border-purple-500/30 text-xs font-semibold text-purple-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5"
                  title="Export raw structured psychometric result data (.json)"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Export JSON</span>
                </button>

                <button
                  type="button"
                  onClick={handlePrintResult}
                  className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5"
                  title="Print result report or save as PDF"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print / PDF</span>
                </button>
              </div>

              <button
                type="button"
                onClick={() => setDetailResult(null)}
                className="w-full sm:w-auto px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold transition-all cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL: ASSESSMENT ATTEMPTS COMPARISON
         ===================================================================== */}
      {showCompareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="glass-panel w-full max-w-3xl rounded-3xl border border-slate-800 shadow-2xl p-6 sm:p-8 space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <GitCompare className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-white">Compare Assessment Attempts</h3>
              </div>
              <button
                onClick={() => setShowCompareModal(false)}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 transition-all cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Attempt Selectors */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">
                  Baseline Attempt (Earlier):
                </label>
                <select
                  value={compareBaselineId}
                  onChange={(e) => setCompareBaselineId(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="">Select Baseline</option>
                  {history.map((h) => (
                    <option key={h.session_id} value={h.session_id}>
                      {h.assessment_type} — {h.result_code} ({new Date(h.completed_at).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">
                  Target Attempt (Later):
                </label>
                <select
                  value={compareTargetId}
                  onChange={(e) => setCompareTargetId(e.target.value)}
                  className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="">Select Target</option>
                  {history.map((h) => (
                    <option key={h.session_id} value={h.session_id}>
                      {h.assessment_type} — {h.result_code} ({new Date(h.completed_at).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={handleRunComparison}
              disabled={comparing || !compareBaselineId || !compareTargetId}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold disabled:opacity-50 transition-all cursor-pointer flex items-center justify-center gap-1.5"
            >
              <GitCompare className="w-4 h-4" />
              <span>{comparing ? 'Analyzing Differences...' : 'Run Comparative Analysis'}</span>
            </button>

            {/* Comparison Results */}
            {comparisonResult && (
              <div className="space-y-4 pt-4 border-t border-slate-800 animate-fadeIn">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white font-mono">
                    Baseline: {comparisonResult.baseline_result_code} → Target: {comparisonResult.target_result_code}
                  </span>
                  <span className="text-[10px] text-slate-500 uppercase font-bold">
                    {comparisonResult.assessment_type}
                  </span>
                </div>

                <div className="space-y-2">
                  {comparisonResult.dimensions_comparison.map((dim, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                    >
                      <div className="space-y-0.5">
                        <span className="font-bold text-slate-200">{dim.dimension}</span>
                        <p className="text-[11px] text-slate-400">{dim.interpretation}</p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <span className="font-mono text-slate-400 text-[11px]">
                          {dim.baseline_score}% → {dim.target_score}%
                        </span>
                        <span
                          className={`font-mono font-bold text-xs px-2 py-0.5 rounded ${
                            dim.delta > 0
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : dim.delta < 0
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {dim.delta > 0 ? `+${dim.delta}%` : `${dim.delta}%`}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <p className="text-[11px] text-slate-500 italic leading-relaxed pt-2">
                  {comparisonResult.summary}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
