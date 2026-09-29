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
  ArrowRight
} from 'lucide-react';
import {
  AssessmentMeta,
  AssessmentResult,
  PersonalitySynthesis,
  QuestionItem,
  AnswerItem,
  PublicTabType
} from '../../types';
import { api } from '../../services/api';
import { EmptyState } from '../common/EmptyState';

interface PersonalityViewProps {
  synthesis: PersonalitySynthesis | null;
  onRefreshSynthesis: () => void;
  onNavigate?: (tab: PublicTabType) => void;
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
  const [submitting, setSubmitting] = useState(false);
  const [activeResult, setActiveResult] = useState<AssessmentResult | null>(null);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'take' | 'history'>('overview');

  const [showQuestionGrid, setShowQuestionGrid] = useState<boolean>(false);

  useEffect(() => {
    loadRegistryAndHistory();
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
      setActiveResult(null);
      setShowQuestionGrid(false);
    } catch (err: any) {
      alert(`Could not start assessment: ${err.message}`);
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
    setSubmitting(true);
    try {
      const formattedAnswers: AnswerItem[] = activeSession.questions.map((q) => ({
        question_id: q.id,
        dimension: q.dimension,
        selected_value: activeSession.answers[q.id] || 3 // Default neutral if unanswered
      }));

      const res = await api.submitAssessment(activeSession.sessionId, formattedAnswers);
      setActiveResult(res);
      setActiveSession(null);
      setSelectedTab('overview');
      setShowQuestionGrid(false);
      await loadRegistryAndHistory();
      onRefreshSynthesis();
    } catch (err: any) {
      alert(`Submission error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  // --- RENDER ASSESSMENT RUNNER ---
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
                {activeSession.type}
              </span>
              <span className="text-white text-sm font-bold">Standardized Psychometric Assessment</span>
              <span className="text-slate-500 font-mono">({totalQ} Questions)</span>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setShowQuestionGrid(!showQuestionGrid)}
                className="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-750 text-indigo-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5 font-medium"
              >
                <span>Question Matrix ({answeredCount}/{totalQ})</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  if (confirm('Cancel this assessment session and return to the portfolio overview?')) {
                    setActiveSession(null);
                    setSelectedTab('overview');
                  }
                }}
                className="px-3 py-1.5 rounded-xl border border-rose-900/60 bg-rose-950/30 hover:bg-rose-900/50 text-rose-300 transition-all cursor-pointer"
              >
                Exit
              </button>
            </div>
          </div>

          {/* Dual Progress Bars: Current Item & Total Completed */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span className="font-mono text-indigo-400">
                Current: Question {activeSession.currentIdx + 1} of {totalQ} ({progress}%)
              </span>
              <span className="font-mono text-emerald-400">
                Completed: {answeredCount} of {totalQ} items answered ({answeredPct}%)
              </span>
            </div>
            <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800/80">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-full transition-all duration-300"
                style={{ width: `${Math.max(progress, answeredPct)}%` }}
              />
            </div>
          </div>

          {/* Quick Jump Question Matrix (1 to 43) */}
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
                      title={`Item ${idx + 1}: Dimension ${item.dimension} (${isAnswered ? 'Answered: ' + activeSession.answers[item.id] : 'Unanswered'})`}
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
                Item {activeSession.currentIdx + 1} of {totalQ} · Dimension {q.dimension}
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

          {/* 5-point Likert Scale options */}
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
                  <span className="block text-lg sm:text-xl font-bold font-mono mb-1">{opt.val}</span>
                  <span className="text-[10px] sm:text-xs font-medium line-clamp-1">{opt.label}</span>
                </button>
              ))}
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 px-1 font-medium">
              <span>{q.negative_pole || '← Disagree'}</span>
              <span>{q.positive_pole || 'Agree →'}</span>
            </div>
          </div>

          {/* Navigation Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-6 border-t border-slate-800/80">
            <button
              type="button"
              disabled={activeSession.currentIdx === 0}
              onClick={() =>
                setActiveSession({
                  ...activeSession,
                  currentIdx: activeSession.currentIdx - 1
                })
              }
              className="px-4 py-2.5 rounded-xl text-xs font-medium border border-slate-800 hover:bg-slate-800 disabled:opacity-30 text-slate-300 transition-all cursor-pointer text-center"
            >
              Previous Question
            </button>

            {activeSession.currentIdx < totalQ - 1 ? (
              <button
                type="button"
                onClick={() =>
                  setActiveSession({
                    ...activeSession,
                    currentIdx: activeSession.currentIdx + 1
                  })
                }
                className="px-6 py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all cursor-pointer flex items-center justify-center gap-1.5"
              >
                <span>Next Question ({activeSession.currentIdx + 2}/{totalQ})</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <div className="flex flex-col sm:items-end gap-1">
                <button
                  type="button"
                  disabled={submitting}
                  onClick={handleSubmitAnswers}
                  className="px-8 py-3 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/30 transition-all cursor-pointer text-center"
                >
                  {submitting ? 'Computing Psychological Archetype...' : `Submit Assessment (${answeredCount}/${totalQ} items)`}
                </button>
                {answeredCount < totalQ && (
                  <span className="text-[10px] text-amber-400/90 font-medium">
                    Note: {totalQ - answeredCount} unanswered items will be scored as Neutral (3).
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 sm:py-12 px-4 sm:px-6 space-y-10 animate-fadeIn">
      {/* Header and Sub-tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <span className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl">
              <Brain className="w-6 h-6" />
            </span>
            Personality Intelligence & Psychology Engine
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Empirical personality assessment models: MBTI (Cognitive Style), DISC (Operational Drive), and Big Five (OCEAN).
          </p>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-2xl border border-slate-800">
          <button
            onClick={() => setSelectedTab('overview')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              selectedTab === 'overview'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Synthesis Overview
          </button>
          <button
            onClick={() => setSelectedTab('take')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              selectedTab === 'take'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Take Tests ({registry.length})
          </button>
          <button
            onClick={() => setSelectedTab('history')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              selectedTab === 'history'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Test History ({history.length})
          </button>
        </div>
      </div>

      {/* VIEW: OVERVIEW */}
      {selectedTab === 'overview' && (
        <div className="space-y-8">
          {(!synthesis || !synthesis.has_assessments) && history.length === 0 ? (
            <EmptyState
              icon={Brain}
              title="Personality assessment not completed"
              description="No assessment results have been recorded yet. Complete the MBTI, DISC, or Big Five assessments to generate synthesized behavioral profiles, soft skills, and strengths."
              actionText="Take Your First Assessment"
              onAction={() => setSelectedTab('take')}
            />
          ) : (
            <>
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
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Active
                        </span>
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
                        <p className="text-[11px] text-slate-400 line-clamp-3">
                          {synthesis.latest_results.MBTI.summary}
                        </p>
                      </>
                    ) : (
                      <div className="py-4 text-xs text-slate-500 italic">
                        Cognitive preferences not established.
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleStartTest('MBTI')}
                    className="mt-5 w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-800 text-indigo-300 transition-all cursor-pointer"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>{synthesis?.latest_results.MBTI ? 'Retake MBTI' : 'Start MBTI'}</span>
                  </button>
                </div>

                {/* DISC Card */}
                <div className="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold tracking-wider uppercase text-purple-400">
                        DISC Behavioral
                      </span>
                      {synthesis?.latest_results.DISC ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Active
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
                        <p className="text-[11px] text-slate-400 line-clamp-3">
                          {synthesis.latest_results.DISC.summary}
                        </p>
                      </>
                    ) : (
                      <div className="py-4 text-xs text-slate-500 italic">
                        Workplace behavior profile not taken.
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleStartTest('DISC')}
                    className="mt-5 w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-800 text-purple-300 transition-all cursor-pointer"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>{synthesis?.latest_results.DISC ? 'Retake DISC' : 'Start DISC'}</span>
                  </button>
                </div>

                {/* Big Five Card */}
                <div className="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold tracking-wider uppercase text-amber-400">
                        Big Five / OCEAN
                      </span>
                      {synthesis?.latest_results.BIG_FIVE ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Active
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
                  <button
                    onClick={() => handleStartTest('BIG_FIVE')}
                    className="mt-5 w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-800 text-amber-300 transition-all cursor-pointer"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>{synthesis?.latest_results.BIG_FIVE ? 'Retake Big Five' : 'Start Big Five'}</span>
                  </button>
                </div>
              </div>

              {/* Synthesized 14 Strengths & 7 Weaknesses Layer (No soft skills) */}
              {synthesis && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                  {/* 14 Key Strengths (Communication Mandatory) */}
                  <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4" />
                        14 Key Strengths
                      </h3>
                      <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-lg">
                        {synthesis.key_strengths.length} Core Strengths
                      </span>
                    </div>

                    <ul className="space-y-2.5">
                      {synthesis.key_strengths.map((st, i) => {
                        const isMandatory = st.toLowerCase() === 'communication';
                        return (
                          <li
                            key={i}
                            className={`flex items-start gap-3 text-xs rounded-xl p-2.5 border transition-all ${
                              isMandatory
                                ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
                                : 'bg-slate-900/60 border-slate-800/80 text-slate-300'
                            }`}
                          >
                            <span className="font-mono text-[10px] font-bold text-slate-500 shrink-0 mt-0.5">
                              #{i + 1}
                            </span>
                            <div className="flex-1 leading-relaxed">
                              <span>{st}</span>
                              {isMandatory && (
                                <span className="ml-2 inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-emerald-500 text-slate-950 tracking-wider">
                                  Mandatory Core Strength
                                </span>
                              )}
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  </div>

                  {/* 7 Weaknesses / Growth Areas */}
                  <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        7 Growth Blindspots / Weaknesses
                      </h3>
                      <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-lg">
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
              )}
            </>
          )}
        </div>
      )}

      {/* VIEW: TAKE TESTS LIST */}
      {selectedTab === 'take' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {registry.map((test) => (
            <div
              key={test.type}
              className="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between shadow-xl hover:border-slate-700 transition-all"
            >
              <div>
                <span className="px-3 py-1 rounded-lg text-[10px] font-bold tracking-wider uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-3 inline-block">
                  {test.type} Assessment
                </span>
                <h3 className="text-lg font-bold text-white tracking-tight mb-1">
                  {test.name}
                </h3>
                <p className="text-xs font-medium text-slate-400 mb-4">{test.tagline}</p>
                <p className="text-xs text-slate-300 leading-relaxed mb-4">{test.description}</p>

                <div className="space-y-1 mb-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400">
                  <div className="flex justify-between">
                    <span>Questions:</span>
                    <span className="font-mono text-slate-200">{test.question_count} items</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Estimated Duration:</span>
                    <span className="font-mono text-slate-200">{test.estimated_minutes} min</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleStartTest(test.type)}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
              >
                <Play className="w-4 h-4" />
                <span>Launch Assessment</span>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* VIEW: HISTORY */}
      {selectedTab === 'history' && (
        <div className="space-y-4">
          {history.length === 0 ? (
            <EmptyState
              icon={Brain}
              title="No assessment history"
              description="Historical assessment records will appear here as you take tests."
            />
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                className="glass-card p-5 sm:p-6 rounded-2xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {item.assessment_type}
                    </span>
                    <span className="text-xs font-mono text-slate-500">
                      {new Date(item.completed_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h4 className="text-base font-bold text-white">
                    {item.result_code} — {item.result_title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 max-w-2xl">{item.summary}</p>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                    Scored
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
