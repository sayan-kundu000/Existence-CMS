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


def score_mbti(answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
    """Score MBTI responses and derive type, dimensions, soft skills, strengths, and weaknesses."""
    dim_sums = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}
    dim_counts = {"EI": 0, "SN": 0, "TF": 0, "JP": 0}

    for ans in answers:
        if ans.dimension in dim_sums:
            dim_sums[ans.dimension] += ans.selected_value
            dim_counts[ans.dimension] += 1

    # Calculations (Likert 1-5, where 3 is neutral mid-point)
    # EI: 1=I, 5=E
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

    # Dynamic derivation of strengths and weaknesses (no soft skills)
    strengths = []
    weaknesses = []

    if e_or_i == "E":
        strengths.append("High sociability and energizing team momentum")
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
        f"Demonstrates a clear {mbti_code} ({title}) cognitive preference: "
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


def score_disc(answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
    """Score DISC assessment and derive behavioral archetype, strengths and blindspots (no soft skills)."""
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
    secondary_code = sorted_traits[1][0] if sorted_traits[1][1] >= 45 else ""

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

    comp_str = f"complemented by secondary trait {secondary_code} ({pcts[secondary_code]}%). " if secondary_code else ""
    summary = (
        f"Primary behavioral emphasis on {primary_code} ({pcts[primary_code]}%) "
        f"{comp_str}Displays high operational impact "
        f"when working in environments that reward {title.lower()}."
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


def score_big_five(answers: List[ResponseAnswerItem]) -> Dict[str, Any]:
    """Score Big Five / OCEAN framework and derive percentile indices (no soft skills)."""
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
    
    # Archetype narrative based on dominant traits
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
    else:
        strengths.append("Pragmatic implementation focus rooted in proven conventions")

    if scores["C"] >= 60:
        strengths.append("Uncompromising follow-through on commitments and high personal accountability")
    else:
        weaknesses.append("Benefits from structured checklists to maintain task consistency")

    if scores["E"] >= 60:
        strengths.append("Comfortable initiating high-visibility outreach and community building")

    if scores["A"] >= 60:
        strengths.append("Fosters high-trust psychological safety in group settings")

    if scores["N"] <= 40:
        strengths.append("Maintains emotional composure and clear head under intense operational volatility")
    else:
        weaknesses.append("Heightened sensitivity to environmental ambiguity requires explicit clarity")

    summary = (
        f"Five-Factor breakdown: Openness {scores['O']}%, Conscientiousness {scores['C']}%, "
        f"Extraversion {scores['E']}%, Agreeableness {scores['A']}%, Neuroticism {scores['N']}%."
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


# Calibrated pool of psychological strengths to guarantee exactly 14 total (with Communication mandatory)
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
    Synthesizes personality intelligence strictly from assessment outputs:
    - Communication is the mandatory strength.
    - Exactly 14 key strengths (13 derived + mandatory Communication).
    - Exactly 7 weaknesses / growth areas.
    - Types of personalities clearly stated.
    - No soft skills (empty list).
    """
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

    # 1. Strengths: Mandatory 'Communication' + exactly 13 derived strengths = 14 total
    MANDATORY_STRENGTH = "Communication"
    derived_strengths = []
    for s in raw_strengths:
        clean = s.strip()
        if clean.lower() != MANDATORY_STRENGTH.lower() and clean not in derived_strengths:
            derived_strengths.append(clean)

    # Fill from calibrated pool if fewer than 13 derived from available tests
    for pool_st in PSYCHOLOGICAL_STRENGTHS_POOL:
        if len(derived_strengths) >= 13:
            break
        if pool_st not in derived_strengths and pool_st.lower() != MANDATORY_STRENGTH.lower():
            derived_strengths.append(pool_st)

    # Trim to exactly 13
    derived_strengths = derived_strengths[:13]

    # Exactly 14 total strengths with Communication guaranteed
    final_strengths = [MANDATORY_STRENGTH] + derived_strengths

    # 2. Weaknesses: Exactly 7 derived weaknesses
    derived_weaknesses = []
    for w in raw_weaknesses:
        clean = w.strip()
        if clean not in derived_weaknesses:
            derived_weaknesses.append(clean)

    # Fill from calibrated pool if fewer than 7
    for pool_wk in PSYCHOLOGICAL_WEAKNESSES_POOL:
        if len(derived_weaknesses) >= 7:
            break
        if pool_wk not in derived_weaknesses:
            derived_weaknesses.append(pool_wk)

    # Trim to exactly 7
    final_weaknesses = derived_weaknesses[:7]

    # 3. No soft skills
    final_soft_skills: List[str] = []

    # 4. Summary narrative stating personality types
    summary = " | ".join(types_narrative) if types_narrative else "Personality assessments not yet completed."

    return final_soft_skills, final_strengths, final_weaknesses, summary
