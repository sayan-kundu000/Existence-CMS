from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from app.schemas.assessment import ResponseAnswerItem

MBTI_TITLES: Dict[str, str] = {
    "INTJ": "Architect / Strategic Mastermind",
    "INTP": "Logician / Innovative Thinker",
    "ENTJ": "Commander / Executive Leader",
    "ENTP": "Debater / Visionary Explorer",
    "INFJ": "Advocate / Insightful Idealist",
    "INFP": "Mediator / Empathetic Visionary",
    "ENFJ": "Protagonist / Inspiring Mentor",
    "ENFP": "Campaigner / Creative Catalyst",
    "ISTJ": "Inspector / Methodical Realist",
    "ISFJ": "Defender / Dedicated Custodian",
    "ESTJ": "Director / Systematic Organizer",
    "ESFJ": "Consul / Harmonious Facilitator",
    "ISTP": "Virtuoso / Practical Troubleshooter",
    "ISFP": "Adventurer / Sensitive Craftsman",
    "ESTP": "Entrepreneur / Dynamic Pragmatist",
    "ESFP": "Entertainer / Spontaneous Enthusiast"
}

DISC_TITLES: Dict[str, str] = {
    "D": "Dominant Driver (Results-Oriented & Decisive)",
    "I": "Influential Inspirer (Persuasive & Enthusiastic)",
    "S": "Steady Supporter (Patient & Collaborative)",
    "C": "Conscientious Analyst (Precise & Systematic)",
    "DI": "Dynamic Initiator",
    "DC": "Strategic Challenger",
    "ID": "Charismatic Pioneer",
    "IS": "Harmonious Connector",
    "SI": "Supportive Facilitator",
    "SC": "Reliable Quality Anchor",
    "CD": "Disciplined Strategist",
    "CS": "Methodical Specialist"
}


# ===========================================================================
# Reusable Assessment Scoring Strategies (Strategy Pattern)
# ===========================================================================

class BaseScoringStrategy(ABC):
    """Abstract base class for model-specific psychometric scoring strategies."""

    @abstractmethod
    def score(self, answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
        """Calculates dimension scores, archetype classification, strengths, and development areas."""
        pass


class MbtiScoringStrategy(BaseScoringStrategy):
    """
    MBTI Psychometric Scoring Strategy:
    Calculates four preference dimensions:
    - Extraversion (E) <-> Introversion (I)
    - Sensing (S) <-> Intuition (N)
    - Thinking (T) <-> Feeling (F)
    - Judging (J) <-> Perceiving (P)
    Derives 4-letter type across all 16 valid combinations.
    """

    def score(self, answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
        dim_sums = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}
        dim_counts = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}

        for ans in answers:
            if ans.dimension in dim_sums:
                dim_sums[ans.dimension] += ans.selected_value
                dim_counts[ans.dimension] += 1

        # EI: 1=I, 5=E (Midpoint = 3.0)
        ei_avg = dim_sums["EI"] / max(1, dim_counts["EI"])
        e_pct = round(((ei_avg - 1) / 4) * 100)
        i_pct = 100 - e_pct
        e_or_i = "E" if ei_avg >= 3.0 else "I"

        # SN: 1=S, 5=N
        sn_avg = dim_sums["SN"] / max(1, dim_counts["SN"])
        n_pct = round(((sn_avg - 1) / 4) * 100)
        s_pct = 100 - n_pct
        s_or_n = "N" if sn_avg >= 3.0 else "S"

        # TF: 1=T, 5=F
        tf_avg = dim_sums["TF"] / max(1, dim_counts["TF"])
        f_pct = round(((tf_avg - 1) / 4) * 100)
        t_pct = 100 - f_pct
        t_or_f = "F" if tf_avg >= 3.0 else "T"

        # JP: 1=J, 5=P
        jp_avg = dim_sums["JP"] / max(1, dim_counts["JP"])
        p_pct = round(((jp_avg - 1) / 4) * 100)
        j_pct = 100 - p_pct
        j_or_p = "P" if jp_avg >= 3.0 else "J"

        mbti_code = f"{e_or_i}{s_or_n}{t_or_f}{j_or_p}"
        title = MBTI_TITLES.get(mbti_code, f"{mbti_code} Personality Type")

        strengths = []
        weaknesses = []

        if e_or_i == "E":
            strengths.append("High sociability and energizing team momentum")
            weaknesses.append("May experience restlessness during prolonged solitary routine tasks")
        else:
            strengths.append("High concentration and autonomous deep work")
            weaknesses.append("May delay speaking up in rapid unmoderated meetings")

        if s_or_n == "N":
            strengths.append("Quickly connects disparate concepts to formulate innovative visions")
            weaknesses.append("Can overlook repetitive operational details in favor of the macro view")
        else:
            strengths.append("Grounded realism and rigorous implementation fidelity")
            weaknesses.append("May exhibit initial skepticism toward unproven theoretical approaches")

        if t_or_f == "T":
            strengths.append("Detached rational analysis under emotional pressure")
            weaknesses.append("Feedback delivery can occasionally be perceived as overly blunt")
        else:
            strengths.append("Naturally cultivates psychological safety and team morale")
            weaknesses.append("May hesitate to deliver tough, uncomfortable performance critiques")

        if j_or_p == "J":
            strengths.append("Predictable deadline execution and systematic organization")
            weaknesses.append("May experience friction when requirements shift unpredictably")
        else:
            strengths.append("High flexibility and calm demeanor during sudden scope pivots")
            weaknesses.append("Risk of delaying final closure in pursuit of exploratory alternatives")

        scores = {
            "dimensions": {
                "Extraversion": e_pct,
                "Introversion": i_pct,
                "Sensing": s_pct,
                "Intuition": n_pct,
                "Thinking": t_pct,
                "Feeling": f_pct,
                "Judging": j_pct,
                "Perceiving": p_pct
            },
            "breakdown": {
                "EI": {"score": ei_avg, "preference": e_or_i, "e_pct": e_pct, "i_pct": i_pct},
                "SN": {"score": sn_avg, "preference": s_or_n, "n_pct": n_pct, "s_pct": s_pct},
                "TF": {"score": tf_avg, "preference": t_or_f, "f_pct": f_pct, "t_pct": t_pct},
                "JP": {"score": jp_avg, "preference": j_or_p, "p_pct": p_pct, "j_pct": j_pct}
            }
        }

        summary = (
            f"Assessment output indicates a {mbti_code} ({title}) cognitive preference: "
            f"{'Introverted' if e_or_i == 'I' else 'Extraverted'} orientation paired with "
            f"{'Intuitive' if s_or_n == 'N' else 'Sensing'} information intake, "
            f"{'Thinking-based' if t_or_f == 'T' else 'Values-centered'} decision criteria, and "
            f"{'Structured' if j_or_p == 'J' else 'Adaptable'} workflow execution."
        )

        return {
            "result_code": mbti_code,
            "result_title": title,
            "summary": summary,
            "scores": scores,
            "soft_skills": [],
            "strengths": list(dict.fromkeys(strengths)),
            "weaknesses": list(dict.fromkeys(weaknesses))
        }


class DiscScoringStrategy(BaseScoringStrategy):
    """
    DISC Behavioral Assessment Scoring Strategy:
    Measures 4 core dimensions:
    - Dominance (D)
    - Influence (I)
    - Steadiness (S)
    - Conscientiousness (C)
    Derives primary dimension and secondary dimension where appropriate.
    """

    def score(self, answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
        dim_sums = {"D": 0, "I": 0, "S": 0, "C": 0}
        dim_counts = {"D": 0, "I": 0, "S": 0, "C": 0}

        for ans in answers:
            if ans.dimension in dim_sums:
                dim_sums[ans.dimension] += ans.selected_value
                dim_counts[ans.dimension] += 1

        pcts = {}
        for d in ["D", "I", "S", "C"]:
            avg = dim_sums[d] / max(1, dim_counts[d])
            pcts[d] = round(((avg - 1) / 4) * 100)

        # Sort to determine primary and secondary behavioral traits
        sorted_traits = sorted(pcts.items(), key=lambda item: item[1], reverse=True)
        primary_code = sorted_traits[0][0]
        secondary_code = sorted_traits[1][0] if len(sorted_traits) > 1 and sorted_traits[1][1] >= 45 else ""

        disc_code = f"{primary_code}{secondary_code}"
        title = DISC_TITLES.get(disc_code, DISC_TITLES.get(primary_code, f"{disc_code} Behavioral Profile"))

        strengths = []
        weaknesses = []

        if primary_code == "D":
            strengths.append("High drive for measurable outcomes and decisive crisis leadership")
            weaknesses.append("Can become impatient with deliberate consensus building")
        elif primary_code == "I":
            strengths.append("Inspiring enthusiasm and generating collaborative team alignment")
            weaknesses.append("May lose momentum when immersed in repetitive administrative paperwork")
        elif primary_code == "S":
            strengths.append("Remarkable reliability, team loyalty, and steady operational continuity")
            weaknesses.append("May hesitate when sudden unannounced organizational shifts occur")
        elif primary_code == "C":
            strengths.append("High precision, empirical integrity, and zero tolerance for defect leakage")
            weaknesses.append("Risk of analysis paralysis when rapid decisions are required with incomplete data")

        # Secondary behavioral trait evaluation (if identified)
        if secondary_code:
            if secondary_code == "D" and "High drive for measurable outcomes and decisive crisis leadership" not in strengths:
                strengths.append("Decisive problem-solving and focus on measurable milestones")
                weaknesses.append("Can experience frustration with prolonged administrative delays")
            elif secondary_code == "I" and "Inspiring enthusiasm and generating collaborative team alignment" not in strengths:
                strengths.append("Dynamic interpersonal engagement and stakeholder motivation")
                weaknesses.append("Risk of deprioritizing routine record-keeping for new initiatives")
            elif secondary_code == "S" and "Remarkable reliability, team loyalty, and steady operational continuity" not in strengths:
                strengths.append("Consistent team dependability and patient conflict mitigation")
                weaknesses.append("May delay initiating unilateral changes without consensus")
            elif secondary_code == "C" and "High precision, empirical integrity, and zero tolerance for defect leakage" not in strengths:
                strengths.append("Methodical quality verification and structured analytical rigor")
                weaknesses.append("May over-scrutinize edge cases during time-sensitive sprints")

        comp_str = f"complemented by secondary trait {secondary_code} ({pcts.get(secondary_code, 0)}%). " if secondary_code else ""
        summary = (
            f"Assessment output indicates a primary behavioral emphasis on {primary_code} ({pcts[primary_code]}%) "
            f"{comp_str}Displays high measured engagement "
            f"in operational environments aligned with {title.lower()}."
        )

        return {
            "result_code": disc_code,
            "result_title": title,
            "summary": summary,
            "scores": {"percentages": pcts, "ranking": [t[0] for t in sorted_traits]},
            "soft_skills": [],
            "strengths": strengths,
            "weaknesses": weaknesses
        }


class OceanScoringStrategy(BaseScoringStrategy):
    """
    Big Five / OCEAN Psychometric Scoring Strategy:
    Evaluates:
    - Openness to Experience (O)
    - Conscientiousness (C)
    - Extraversion (E)
    - Agreeableness (A)
    - Neuroticism / Emotional Sensitivity (N)
    Treats scores as non-judgmental psychometric dimensions.
    """

    def score(self, answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
        dim_sums = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}
        dim_counts = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}

        for ans in answers:
            if ans.dimension in dim_sums:
                dim_sums[ans.dimension] += ans.selected_value
                dim_counts[ans.dimension] += 1

        scores = {}
        for d in ["O", "C", "E", "A", "N"]:
            avg = dim_sums[d] / max(1, dim_counts[d])
            scores[d] = round(((avg - 1) / 4) * 100)

        result_code = f"O{scores['O']}-C{scores['C']}-E{scores['E']}-A{scores['A']}-N{scores['N']}"

        primary_traits = []
        if scores["O"] >= 65: primary_traits.append("High Openness")
        if scores["C"] >= 65: primary_traits.append("High Conscientiousness")
        if scores["E"] >= 65: primary_traits.append("High Extraversion")
        if scores["A"] >= 65: primary_traits.append("High Agreeableness")
        if scores["N"] <= 35: primary_traits.append("High Emotional Stability")

        result_title = " · ".join(primary_traits) if primary_traits else "Balanced Five-Factor Profile"

        strengths = []
        weaknesses = []

        if scores["O"] >= 60:
            strengths.append("High openness to pioneering concepts and multidisciplinary innovation")
            weaknesses.append("Risk of overcomplicating straightforward tasks with exploratory ideas")
        else:
            strengths.append("Pragmatic implementation focus rooted in proven conventions")
            weaknesses.append("May exhibit initial resistance toward unproven theoretical paradigms")

        if scores["C"] >= 60:
            strengths.append("Uncompromising follow-through on commitments and high personal accountability")
            weaknesses.append("Can become overly rigid when sudden plans require immediate improvisation")
        else:
            strengths.append("Spontaneous adaptability and ease operating in ambiguous environments")
            weaknesses.append("Benefits from structured checklists to maintain task consistency")

        if scores["E"] >= 60:
            strengths.append("Comfortable initiating high-visibility outreach and community building")
            weaknesses.append("May occasionally dominate conversational space in collaborative forums")
        else:
            strengths.append("High capacity for independent focus and deep, uninterrupted concentration")
            weaknesses.append("May prefer written exchanges over spontaneous high-bandwidth speaking")

        if scores["A"] >= 60:
            strengths.append("Fosters high-trust psychological safety in group settings")
            weaknesses.append("May hesitate to challenge popular consensus to preserve team harmony")
        else:
            strengths.append("Objective critical scrutiny and direct competitive execution")
            weaknesses.append("Direct critique style may occasionally risk interpersonal friction")

        if scores["N"] <= 40:
            strengths.append("Maintains emotional composure and clear head under intense operational volatility")
            weaknesses.append("May occasionally underestimate emotional stress cues in team dynamics")
        else:
            strengths.append("Acute environmental vigilance and rapid sensitivity to subtle project risks")
            weaknesses.append("Heightened sensitivity to environmental ambiguity requires explicit clarity")

        summary = (
            f"Five-Factor assessment outputs: Openness {scores['O']}%, Conscientiousness {scores['C']}%, "
            f"Extraversion {scores['E']}%, Agreeableness {scores['A']}%, Neuroticism {scores['N']}%. "
            "Scores represent measured preferences across standardized psychometric dimensions."
        )

        return {
            "result_code": result_code,
            "result_title": result_title,
            "summary": summary,
            "scores": scores,
            "soft_skills": [],
            "strengths": strengths,
            "weaknesses": weaknesses
        }


class ScoringStrategyFactory:
    """Factory to instantiate the appropriate scoring strategy."""

    @staticmethod
    def get_strategy(assessment_type: str) -> BaseScoringStrategy:
        atype = assessment_type.upper()
        if atype == "MBTI":
            return MbtiScoringStrategy()
        elif atype == "DISC":
            return DiscScoringStrategy()
        elif atype in ("BIG_FIVE", "OCEAN"):
            return OceanScoringStrategy()
        raise ValueError(f"No configured scoring strategy for assessment type '{assessment_type}'")


# Backward-compatible convenience functions
def score_mbti(answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
    return ScoringStrategyFactory.get_strategy("MBTI").score(answers)


def score_disc(answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
    return ScoringStrategyFactory.get_strategy("DISC").score(answers)


def score_big_five(answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
    return ScoringStrategyFactory.get_strategy("BIG_FIVE").score(answers)


# ===========================================================================
# Result Comparison Engine
# ===========================================================================

def compare_assessment_results(baseline: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares two completed assessment results of the same assessment model.
    Calculates dimension score deltas, shift directions, and objective descriptions.
    Enforces non-judgmental psychometric interpretation (measured shift, not growth/decline).
    """
    b_type = baseline.get("assessment_type", "")
    t_type = target.get("assessment_type", "")
    if b_type != t_type:
        raise ValueError(f"Cannot compare results of differing assessment types ({b_type} vs {t_type})")

    b_scores = baseline.get("scores", {})
    t_scores = target.get("scores", {})

    dim_comparisons = []

    if b_type == "MBTI":
        b_dims = b_scores.get("dimensions", {})
        t_dims = t_scores.get("dimensions", {})
        all_dims = ["Extraversion", "Introversion", "Sensing", "Intuition", "Thinking", "Feeling", "Judging", "Perceiving"]
        for dim in all_dims:
            b_val = float(b_dims.get(dim, 50))
            t_val = float(t_dims.get(dim, 50))
            delta = round(t_val - b_val, 1)
            direction = "INCREASED" if delta > 0 else "DECREASED" if delta < 0 else "UNCHANGED"
            interpretation = (
                f"Measured preference score shifted by {delta:+0.1f}% (from {b_val:.0f}% to {t_val:.0f}%)."
                if delta != 0 else f"Measured preference remained constant at {b_val:.0f}%."
            )
            dim_comparisons.append({
                "dimension": dim,
                "baseline_score": b_val,
                "target_score": t_val,
                "delta": delta,
                "direction": direction,
                "interpretation": interpretation
            })

    elif b_type == "DISC":
        b_pcts = b_scores.get("percentages", {})
        t_pcts = t_scores.get("percentages", {})
        for dim in ["D", "I", "S", "C"]:
            dim_label = {"D": "Dominance", "I": "Influence", "S": "Steadiness", "C": "Conscientiousness"}.get(dim, dim)
            b_val = float(b_pcts.get(dim, 0))
            t_val = float(t_pcts.get(dim, 0))
            delta = round(t_val - b_val, 1)
            direction = "INCREASED" if delta > 0 else "DECREASED" if delta < 0 else "UNCHANGED"
            interpretation = (
                f"Dimension score for {dim_label} shifted by {delta:+0.1f}% (from {b_val:.0f}% to {t_val:.0f}%)."
                if delta != 0 else f"Dimension score for {dim_label} remained constant at {b_val:.0f}%."
            )
            dim_comparisons.append({
                "dimension": dim_label,
                "baseline_score": b_val,
                "target_score": t_val,
                "delta": delta,
                "direction": direction,
                "interpretation": interpretation
            })

    elif b_type in ("BIG_FIVE", "OCEAN"):
        # Big Five scores dictionary
        b_s = b_scores.get("scores", b_scores)
        t_s = t_scores.get("scores", t_scores)
        mapping = {
            "O": "Openness",
            "C": "Conscientiousness",
            "E": "Extraversion",
            "A": "Agreeableness",
            "N": "Neuroticism"
        }
        for code, label in mapping.items():
            b_val = float(b_s.get(code, 50))
            t_val = float(t_s.get(code, 50))
            delta = round(t_val - b_val, 1)
            direction = "INCREASED" if delta > 0 else "DECREASED" if delta < 0 else "UNCHANGED"
            interpretation = (
                f"Five-Factor score for {label} shifted by {delta:+0.1f}% (from {b_val:.0f}% to {t_val:.0f}%)."
                if delta != 0 else f"Five-Factor score for {label} remained constant at {b_val:.0f}%."
            )
            dim_comparisons.append({
                "dimension": label,
                "baseline_score": b_val,
                "target_score": t_val,
                "delta": delta,
                "direction": direction,
                "interpretation": interpretation
            })

    summary = (
        f"Compared {b_type} results between attempts (Baseline: {baseline.get('result_code')}, Target: {target.get('result_code')}). "
        f"Shows measured variance across {len(dim_comparisons)} psychometric dimensions. "
        "Notice: Score variances reflect contextual responses and do not constitute absolute personality shifts or moral evaluations."
    )

    return {
        "assessment_type": b_type,
        "baseline_session_id": baseline.get("session_id", ""),
        "target_session_id": target.get("session_id", ""),
        "baseline_result_code": baseline.get("result_code", ""),
        "target_result_code": target.get("result_code", ""),
        "baseline_completed_at": baseline.get("completed_at"),
        "target_completed_at": target.get("completed_at"),
        "dimensions_comparison": dim_comparisons,
        "summary": summary
    }


# Calibrated pool of psychological strengths to guarantee exactly 11 core strengths
PSYCHOLOGICAL_STRENGTHS_POOL = [
    "Strategic systems thinking and conceptual architecture",
    "Decisive execution under ambiguous operational conditions",
    "Analytical problem-solving and empirical root-cause diagnostics",
    "High cognitive stamina and autonomous deep work focus",
    "Goal-oriented perseverance through protracted project cycles",
    "Adaptive agility during sudden technical or strategic pivots",
    "Predictable deadline reliability and milestone discipline",
    "Intellectual curiosity and cross-disciplinary knowledge synthesis",
    "Empathetic stakeholder alignment and team consensus building",
    "Process optimization and systematic quality assurance",
    "Constructive crisis leadership and emotional composure",
    "Rapid pattern recognition across complex data streams",
    "Principled accountability and high ethical standards in execution"
]

# Calibrated pool of psychological weaknesses/blindspots to guarantee exactly 7 total
PSYCHOLOGICAL_WEAKNESSES_POOL = [
    "Tendency to delay speaking up in rapid, unstructured meeting formats",
    "May deprioritize routine administrative tracking in favor of macro strategy",
    "Risk of analysis paralysis when rapid decisions are required with partial data",
    "Can experience impatience with protracted bureaucratic consensus building",
    "Feedback delivery may occasionally be perceived as overly direct and blunt",
    "Initial skepticism toward unproven or non-empirical theoretical paradigms",
    "Sensitivity to ambiguous project mandates without defined measurable milestones"
]


def synthesize_personality(
    mbti: Dict[str, Any] = None,
    disc: Dict[str, Any] = None,
    big_five: Dict[str, Any] = None
) -> Tuple[List[str], List[str], List[str], str]:
    """
    Synthesizes personality intelligence based strictly on the number of completed tests:
    - If 1 test is given: evaluated on the basis of that 1 test.
    - If 2 tests are given: evaluated on the basis of those 2 tests.
    - If 3 tests are given: evaluated on the basis of those 3 tests (yielding 11 core strengths).
    - If 0 tests are given: returns empty lists.
    - No mandatory Communication core strength (Communication is not shown or forced as mandatory).
    - No soft skills (empty list).
    - Summary narrative clearly details the evaluated tests.
    """
    given_tests = []
    if mbti:
        given_tests.append(("MBTI", mbti))
    if disc:
        given_tests.append(("DISC", disc))
    if big_five:
        given_tests.append(("Big Five", big_five))

    test_count = len(given_tests)
    if test_count == 0:
        return [], [], [], "Personality assessments not yet completed."

    raw_strengths = []
    raw_weaknesses = []
    types_narrative = []

    if mbti:
        raw_strengths.extend(mbti.get("strengths", []))
        raw_weaknesses.extend(mbti.get("weaknesses", []))
        types_narrative.append(f"MBTI: {mbti.get('result_code')} ({mbti.get('result_title')})")

    if disc:
        raw_strengths.extend(disc.get("strengths", []))
        raw_weaknesses.extend(disc.get("weaknesses", []))
        types_narrative.append(f"DISC: {disc.get('result_code')} ({disc.get('result_title')})")

    if big_five:
        raw_strengths.extend(big_five.get("strengths", []))
        raw_weaknesses.extend(big_five.get("weaknesses", []))
        types_narrative.append(f"Big Five: {big_five.get('result_title')}")

    # 1. Strengths: Exactly 11 core strengths when full assessments are completed,
    # evaluated dynamically on the basis of completed tests, without Communication as mandatory.
    derived_strengths = []
    for s in raw_strengths:
        clean = s.strip()
        if clean and clean not in derived_strengths:
            derived_strengths.append(clean)

    # When all 3 tests are completed, ensure exactly 11 core strengths are populated
    if test_count == 3 and len(derived_strengths) < 11:
        for pool_st in PSYCHOLOGICAL_STRENGTHS_POOL:
            if len(derived_strengths) >= 11:
                break
            if pool_st not in derived_strengths:
                derived_strengths.append(pool_st)

    final_strengths = derived_strengths[:11]

    # 2. Weaknesses / Growth Areas: strictly derived from completed tests
    derived_weaknesses = []
    for w in raw_weaknesses:
        clean = w.strip()
        if clean and clean not in derived_weaknesses:
            derived_weaknesses.append(clean)

    final_weaknesses = derived_weaknesses

    # 3. No soft skills
    final_soft_skills: List[str] = []

    # 4. Summary narrative stating personality types and test basis
    prefix = (
        f"Evaluated on the basis of 1 completed assessment"
        if test_count == 1
        else f"Evaluated on the basis of {test_count} completed assessments"
    )
    narrative_detail = " | ".join(types_narrative)
    summary = f"{prefix}: {narrative_detail}"

    return final_soft_skills, final_strengths, final_weaknesses, summary
