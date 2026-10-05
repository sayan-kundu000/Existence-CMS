from typing import Dict, List, Any

# Meta definitions for the assessments
ASSESSMENT_REGISTRY: Dict[str, Dict[str, Any]] = {
    "MBTI": {
        "name": "Myers-Briggs Type Indicator (MBTI)",
        "tagline": "Cognitive Style & Psychological Preferences",
        "description": "Explores how you perceive the world, process information, make decisions, and orient your life across 4 core dichotomies.",
        "dimensions": [
            "Extraversion (E) vs Introversion (I)",
            "Sensing (S) vs Intuition (N)",
            "Thinking (T) vs Feeling (F)",
            "Judging (J) vs Perceiving (P)"
        ],
        "question_count": 75,
        "estimated_minutes": 15
    },
    "DISC": {
        "name": "DISC Behavioral Assessment",
        "tagline": "Workplace Communication & Action Tendencies",
        "description": "Measures your observable behavioral patterns in team, leadership, and high-pressure operational environments.",
        "dimensions": [
            "Dominance (D) — Direct, Results-Driven, Decisive",
            "Influence (I) — Outgoing, Persuasive, Enthusiastic",
            "Steadiness (S) — Patient, Team-Oriented, Consistent",
            "Conscientiousness (C) — Analytical, Precise, Systematic"
        ],
        "question_count": 75,
        "estimated_minutes": 15
    },
    "BIG_FIVE": {
        "name": "Big Five / OCEAN Model",
        "tagline": "The Five-Factor Trait Personality Framework",
        "description": "The gold-standard empirical model evaluating five fundamental trait dimensions governing human temperament.",
        "dimensions": [
            "Openness (O) — Intellectual Curiosity & Creative Breadth",
            "Conscientiousness (C) — Organization, Diligence & Discipline",
            "Extraversion (E) — Social Vitality, Energy & Assertiveness",
            "Agreeableness (A) — Empathy, Altruism & Cooperative Spirit",
            "Neuroticism (N) — Emotional Sensitivity & Stress Reactivity"
        ],
        "question_count": 75,
        "estimated_minutes": 15
    }
}

# Standardized Question Banks (Exactly 75 questions per assessment = 225 unique items)
QUESTION_BANKS: Dict[str, List[Dict[str, Any]]] = {
    "MBTI": [
        # --- Dimension: EI (Extraversion vs Introversion) — 19 Items ---
        {
            "id": "mbti_ei_1",
            "dimension": "EI",
            "text": "At networking events or crowded conferences, you feel energized by meeting many new people rather than socially drained.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_2",
            "dimension": "EI",
            "text": "When tackling a complex puzzle, you prefer discussing your thinking out loud with peers rather than working through it in solitary contemplation.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_3",
            "dimension": "EI",
            "text": "You naturally enjoy being at the center of group attention and feel comfortable speaking off the cuff in unfamiliar assemblies.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_4",
            "dimension": "EI",
            "text": "Your ideal work environment involves frequent lively interactions throughout the day rather than sustained quiet solitude.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_5",
            "dimension": "EI",
            "text": "After an exhausting work week, your favorite way to recharge is celebrating with an energetic gathering of friends rather than spending quiet time at home.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_6",
            "dimension": "EI",
            "text": "You tend to introduce yourself first to newcomers in a room without waiting for an intermediary to connect you.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_7",
            "dimension": "EI",
            "text": "You find extended periods of isolation mentally sluggish and feel motivated when there is constant ambient activity around you.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_8",
            "dimension": "EI",
            "text": "In team meetings, you contribute ideas spontaneously as they come to mind rather than rehearsing your statements privately first.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_9",
            "dimension": "EI",
            "text": "You maintain an expansive, broad circle of diverse acquaintances rather than a small, tightly guarded cluster of confidants.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_10",
            "dimension": "EI",
            "text": "You feel comfortable sharing personal insights, anecdotes, and opinions openly even with people you have only recently met.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_11",
            "dimension": "EI",
            "text": "Group brainstorming sessions stimulate your best creativity much more effectively than individual quiet journaling.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_12",
            "dimension": "EI",
            "text": "When entering an unfamiliar gathering, you effortlessly strike up conversations with strangers rather than hanging back near the perimeter.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_13",
            "dimension": "EI",
            "text": "You find that processing complex concepts by speaking through them with a colleague clarifies your thinking faster than internal deliberation.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_14",
            "dimension": "EI",
            "text": "You actively seek opportunities to facilitate group brainstorming sessions rather than working through ideation on your own.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_15",
            "dimension": "EI",
            "text": "A bustling, dynamic office environment stimulates your productivity more than an empty, silent workspace.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_16",
            "dimension": "EI",
            "text": "You naturally take on the role of social catalyst or connector when bringing different teams together for collaborative initiatives.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_17",
            "dimension": "EI",
            "text": "You tend to share your immediate thoughts and impressions freely without prolonged internal deliberation or filtering.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_18",
            "dimension": "EI",
            "text": "You feel invigorated and energized after delivering a presentation or leading a lively question-and-answer session.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_ei_19",
            "dimension": "EI",
            "text": "You prefer taking action in public environments where spontaneous team interaction and banter are part of the daily workflow.",
            "positive_pole": "Extraversion (E)",
            "negative_pole": "Introversion (I)",
            "scale_type": "likert_5"
        },
        # --- Dimension: SN (Sensing vs Intuition) — 19 Items ---
        {
            "id": "mbti_sn_1",
            "dimension": "SN",
            "text": "You are more drawn to speculative theories and long-range future possibilities than to immediate, concrete operational facts.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_2",
            "dimension": "SN",
            "text": "You instinctively focus on hidden patterns, metaphors, and underlying meanings rather than physical step-by-step instructions.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_3",
            "dimension": "SN",
            "text": "You find designing ambitious conceptual roadmaps far more thrilling than managing the day-to-day administrative details.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_4",
            "dimension": "SN",
            "text": "You place greater trust in your instinctive gut impressions than in historically documented track records.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_5",
            "dimension": "SN",
            "text": "You often think about what could be decades from now rather than accepting how things currently exist in reality.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_6",
            "dimension": "SN",
            "text": "When learning a new subject, you want to grasp the overarching philosophy first before memorizing specific mechanics or data.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_7",
            "dimension": "SN",
            "text": "You are fascinated by unconventional, untested hypotheses even when they lack immediate practical application.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_8",
            "dimension": "SN",
            "text": "You find routine, repetitive maintenance tasks tedious and constantly seek novel ways to reinvent the existing system.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_9",
            "dimension": "SN",
            "text": "In literature or conversation, you appreciate allegories, symbolism, and open-ended interpretations more than plain literal statements.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_10",
            "dimension": "SN",
            "text": "You often connect two seemingly unrelated disciplines to synthesize a completely unexpected new concept.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_11",
            "dimension": "SN",
            "text": "You prefer working with visionary prototypes and concepts rather than fine-tuning pre-existing physical tools.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_12",
            "dimension": "SN",
            "text": "You prefer exploring theoretical models and speculative futures over refining existing, proven practical procedures.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_13",
            "dimension": "SN",
            "text": "When reading technical literature, you focus on underlying architectural philosophy rather than granular implementation syntax.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_14",
            "dimension": "SN",
            "text": "You are motivated by conceptual novelty and inventive paradigms rather than predictable, established operational standards.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_15",
            "dimension": "SN",
            "text": "You frequently synthesize insights from seemingly unrelated disciplines to propose groundbreaking strategic directions.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_16",
            "dimension": "SN",
            "text": "You are more fascinated by what could conceivably exist in tomorrow's landscape than what currently functions reliably today.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_17",
            "dimension": "SN",
            "text": "You enjoy reading between the lines and uncovering latent symbolism or hidden intentions in human communications.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_18",
            "dimension": "SN",
            "text": "You find detailed, repetitive administrative compliance tasks tedious compared to speculative product roadmapping.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_sn_19",
            "dimension": "SN",
            "text": "You trust your intuitive hunches about emerging technology trends even when immediate statistical evidence is sparse.",
            "positive_pole": "Intuition (N)",
            "negative_pole": "Sensing (S)",
            "scale_type": "likert_5"
        },
        # --- Dimension: TF (Thinking vs Feeling) — 19 Items ---
        {
            "id": "mbti_tf_1",
            "dimension": "TF",
            "text": "When resolving a difficult dilemma, personal relationships and empathetic impact carry greater weight for you than cold, impersonal logic.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_2",
            "dimension": "TF",
            "text": "You prioritize compassion, individual circumstances, and mercy above strict rule enforcement and uniform justice.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_3",
            "dimension": "TF",
            "text": "You are exceptionally sensitive to the emotional climate of a team and instinctively soften your feedback to avoid hurt feelings.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_4",
            "dimension": "TF",
            "text": "Being regarded as caring, understanding, and kind matters more to you than being perceived as intellectually formidable.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_5",
            "dimension": "TF",
            "text": "You make crucial life choices primarily based on what aligns with your core human values rather than financial or algorithmic optimization.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_6",
            "dimension": "TF",
            "text": "When a friend confides a problem in you, your first impulse is to offer emotional comfort and validation rather than analytical troubleshooting.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_7",
            "dimension": "TF",
            "text": "You believe maintaining team morale and harmonious consensus is more critical to success than proving who is technically correct.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_8",
            "dimension": "TF",
            "text": "You take interpersonal criticism to heart and feel distressed when someone in your circle harbors unresolved resentment.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_9",
            "dimension": "TF",
            "text": "In workplace disputes, you seek solutions where all parties feel heard and validated rather than deciding purely by legal precedent.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_10",
            "dimension": "TF",
            "text": "You find it distressing to terminate an underperforming colleague, even when economic efficiency strictly demands it.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_11",
            "dimension": "TF",
            "text": "You value heartfelt authenticity and vulnerability in leaders more than polished technical brilliance.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_12",
            "dimension": "TF",
            "text": "In contentious discussions, preserving relational harmony and mutual trust takes precedence over winning purely logical debates.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_13",
            "dimension": "TF",
            "text": "You evaluate the success of an organizational decision primarily by its positive impact on human well-being and team dignity.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_14",
            "dimension": "TF",
            "text": "When a teammate experiences personal distress, you instinctively provide emotional empathy before analyzing practical remedies.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_15",
            "dimension": "TF",
            "text": "You naturally prioritize interpersonal consensus and mutual understanding over uncompromising mechanical efficiency.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_16",
            "dimension": "TF",
            "text": "You feel deeply unsettled when an organization treats individuals as interchangeable resources rather than unique human beings.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_17",
            "dimension": "TF",
            "text": "You rely heavily on personal empathy and shared team values when formulating policies or resolving operational disagreements.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_18",
            "dimension": "TF",
            "text": "You are motivated by praise that recognizes your human kindness and supportive spirit rather than purely clinical metrics.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_tf_19",
            "dimension": "TF",
            "text": "You seek to inspire and elevate colleagues through encouragement and psychological safety rather than tough-love critique.",
            "positive_pole": "Feeling (F)",
            "negative_pole": "Thinking (T)",
            "scale_type": "likert_5"
        },
        # --- Dimension: JP (Judging vs Perceiving) — 18 Items ---
        {
            "id": "mbti_jp_1",
            "dimension": "JP",
            "text": "You prefer keeping your schedule fluid and spontaneous rather than committing to rigid calendar appointments.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_2",
            "dimension": "JP",
            "text": "You produce your most inspired work during last-minute bursts of creative urgency rather than steady incremental daily sessions.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_3",
            "dimension": "JP",
            "text": "Sudden, unplanned shifts in travel or project itineraries feel like exciting adventures rather than stressful disruptions.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_4",
            "dimension": "JP",
            "text": "You enjoy continuing to gather information and exploring alternative options instead of locking down early final closure.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_5",
            "dimension": "JP",
            "text": "You feel constrained and restless when forced to follow strict standard operating procedures with no room for improvisation.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_6",
            "dimension": "JP",
            "text": "Your workspace and digital files tend to reflect an evolving, organic creative chaos rather than categorized filing folders.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_7",
            "dimension": "JP",
            "text": "You often begin several intriguing side projects simultaneously before finishing previous ones.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_8",
            "dimension": "JP",
            "text": "When embarking on a vacation, you prefer wandering freely and discovering local spots on a whim rather than booking an hourly itinerary.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_9",
            "dimension": "JP",
            "text": "You view formal deadlines as flexible targets subject to re-negotiation if a better approach emerges.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_10",
            "dimension": "JP",
            "text": "You are energized by ambiguous, evolving problem spaces where the ultimate destination remains to be determined.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_11",
            "dimension": "JP",
            "text": "You prefer remaining open to emergent opportunities and late-breaking changes rather than prematurely committing to rigid blueprints.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_12",
            "dimension": "JP",
            "text": "You find rigid operational constraints stifle your ingenuity and prefer defining workflows organically as situations develop.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_13",
            "dimension": "JP",
            "text": "You enjoy exploring serendipitous tangents and exploratory experiments even when they deviate from predetermined milestone paths.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_14",
            "dimension": "JP",
            "text": "You view project deadlines as helpful directional targets rather than non-negotiable absolute constraints.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_15",
            "dimension": "JP",
            "text": "You feel most creative and agile when navigating loose guidelines that encourage real-time troubleshooting and improvisation.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_16",
            "dimension": "JP",
            "text": "You hesitate to lock down finalized system specifications early, preferring to keep design possibilities open as long as viable.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_17",
            "dimension": "JP",
            "text": "You thrive in high-velocity startup environments where daily priorities pivot dynamically based on customer discoveries.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        },
        {
            "id": "mbti_jp_18",
            "dimension": "JP",
            "text": "You prefer celebrating spontaneous breakthroughs over executing meticulous, step-by-step checklist protocols.",
            "positive_pole": "Perceiving (P)",
            "negative_pole": "Judging (J)",
            "scale_type": "likert_5"
        }
    ],

    "DISC": [
        # --- Dominance (D) — 19 Items ---
        {
            "id": "disc_d_1",
            "dimension": "D",
            "text": "You proactively seize the initiative in stagnant situations, set aggressive targets, and focus relentlessly on bottom-line outcomes.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_2",
            "dimension": "D",
            "text": "You are candid, direct, and completely comfortable challenging consensus when project momentum is at stake.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_3",
            "dimension": "D",
            "text": "You thrive in competitive arenas and prefer rapid, decisive action over extended deliberation.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_4",
            "dimension": "D",
            "text": "You view difficult operational obstacles and organizational resistance as energizing challenges to overcome.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_5",
            "dimension": "D",
            "text": "When a project encounters an unexpected crisis, you naturally step forward to assume leadership and issue clear directives.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_6",
            "dimension": "D",
            "text": "You become impatient with excessive bureaucracy and seek immediate workarounds to bypass red tape.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_7",
            "dimension": "D",
            "text": "You hold yourself and team members to demanding performance benchmarks and address poor output without hesitation.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_8",
            "dimension": "D",
            "text": "You are willing to accept calculated risks and potential blowback if it offers a significant strategic advantage.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_9",
            "dimension": "D",
            "text": "You prefer negotiating from a position of authority and influence rather than yielding ground to appease counterparts.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_10",
            "dimension": "D",
            "text": "You measure personal and professional satisfaction by tangible achievements and market victories rather than mere participation.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_11",
            "dimension": "D",
            "text": "You push continuously for faster turnaround times and dislike resting on past accomplishments.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_12",
            "dimension": "D",
            "text": "You assertively drive challenging initiatives forward and insist on measurable, high-impact results from every team member.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_13",
            "dimension": "D",
            "text": "You are completely comfortable making hard executive calls under extreme time pressure with imperfect data.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_14",
            "dimension": "D",
            "text": "You actively seek leadership opportunities where you possess the autonomous authority to command strategic outcomes.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_15",
            "dimension": "D",
            "text": "You challenge traditional assumptions boldly when you believe a more aggressive tactic will capture greater market share.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_16",
            "dimension": "D",
            "text": "You readily confront project bottlenecks head-on without softening the urgency or seriousness of the issue.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_17",
            "dimension": "D",
            "text": "You expect rapid progress reports focused strictly on quantifiable key performance indicators and bottom-line impact.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_18",
            "dimension": "D",
            "text": "You possess a powerful competitive instinct that drives you to outperform rival organizations and set new benchmarks.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_d_19",
            "dimension": "D",
            "text": "You refuse to let operational complacency slow down momentum and will personally push through institutional resistance.",
            "scale_type": "likert_5"
        },
        # --- Influence (I) — 19 Items ---
        {
            "id": "disc_i_1",
            "dimension": "I",
            "text": "You naturally motivate and rally colleagues around a shared vision through contagious enthusiasm and persuasive rhetoric.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_2",
            "dimension": "I",
            "text": "You excel at building immediate rapport with strangers and expanding social capital across organizational boundaries.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_3",
            "dimension": "I",
            "text": "You prefer interactive collaborative workshops and spontaneous group brainstorming over solitary analytical tasks.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_4",
            "dimension": "I",
            "text": "You maintain an upbeat, optimistic disposition that elevates team morale during difficult periods.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_5",
            "dimension": "I",
            "text": "You enjoy giving public presentations, pitching bold initiatives, and capturing an audience's imagination.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_6",
            "dimension": "I",
            "text": "You use humor, personal storytelling, and charm to disarm tension and win people over to your viewpoint.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_7",
            "dimension": "I",
            "text": "You thrive on external praise, public recognition, and positive reinforcement for your creative contributions.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_8",
            "dimension": "I",
            "text": "You instinctively introduce colleagues to one another to spark collaborative opportunities and creative partnerships.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_9",
            "dimension": "I",
            "text": "You easily generate excitement for brand-new concepts even before practical implementation details are fully ironed out.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_10",
            "dimension": "I",
            "text": "You feel most fulfilled in client-facing, community-building, or promotional roles with high interpersonal visibility.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_11",
            "dimension": "I",
            "text": "You encourage team members to express themselves freely and cultivate an energetic, expressive group culture.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_12",
            "dimension": "I",
            "text": "You inspire enthusiasm in others by articulating an exciting, optimistic vision of what the team can achieve together.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_13",
            "dimension": "I",
            "text": "You excel at building rapport quickly and generating authentic goodwill with prospective clients and cross-functional allies.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_14",
            "dimension": "I",
            "text": "You use humor, charisma, and storytelling to disarm skepticism and bring skeptical stakeholders into enthusiastic alignment.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_15",
            "dimension": "I",
            "text": "You thrive in environments where creative self-expression, public speaking, and spontaneous social interaction are celebrated.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_16",
            "dimension": "I",
            "text": "You naturally celebrate team achievements with celebratory fanfare to sustain high morale and collective vitality.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_17",
            "dimension": "I",
            "text": "You prefer collaborative brainstorming retreats and high-energy workshops over quiet solo spreadsheet audits.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_18",
            "dimension": "I",
            "text": "You persuade colleagues by appealing to shared aspirations and creating a compelling emotional narrative around your ideas.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_i_19",
            "dimension": "I",
            "text": "You are energized by public networking and expand your social influence effortlessly across different professional circles.",
            "scale_type": "likert_5"
        },
        # --- Steadiness (S) — 19 Items ---
        {
            "id": "disc_s_1",
            "dimension": "S",
            "text": "You place high value on organizational predictability, steady cadence, and a calm, dependable work rhythm.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_2",
            "dimension": "S",
            "text": "You are widely recognized as a patient, attentive listener who consistently supports teammates without demanding the spotlight.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_3",
            "dimension": "S",
            "text": "You excel at soothing interpersonal friction, reconciling divergent opinions, and maintaining a stable working coalition.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_4",
            "dimension": "S",
            "text": "You prefer well-planned, deliberate implementations and resist abrupt, disruptive operational overhauls.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_5",
            "dimension": "S",
            "text": "You demonstrate remarkable organizational loyalty and commit to seeing long-term programs through to multi-year completion.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_6",
            "dimension": "S",
            "text": "You work methodically and maintain an unhurried, reassuring presence even when surrounding environments become chaotic.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_7",
            "dimension": "S",
            "text": "You prefer mastering a stable domain of expertise rather than constantly jumping into unfamiliar operational roles.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_8",
            "dimension": "S",
            "text": "You go out of your way to assist a colleague who is overwhelmed by quietly absorbing part of their workload.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_9",
            "dimension": "S",
            "text": "You value deep, long-standing workplace relationships built on mutual trust and confidentiality over superficial networking.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_10",
            "dimension": "S",
            "text": "You prefer working within established team consensus rather than making unilateral decisions that could alienate peers.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_11",
            "dimension": "S",
            "text": "You prioritize safety, dependable follow-through, and reliable service over experimental, high-variance gambles.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_12",
            "dimension": "S",
            "text": "You provide calm, steady emotional grounding and dependable support when organizational turbulence destabilizes your team.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_13",
            "dimension": "S",
            "text": "You place high value on team loyalty, steady predictability, and preserving established working relationships over time.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_14",
            "dimension": "S",
            "text": "You patiently listen to colleagues' concerns without interrupting, ensuring everyone feels heard and valued in group settings.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_15",
            "dimension": "S",
            "text": "You prefer working within established, well-tested team rhythms rather than enduring constant unannounced corporate reorganizations.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_16",
            "dimension": "S",
            "text": "You are known as a dependable anchor who quietly and faithfully finishes critical support tasks without demanding the spotlight.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_17",
            "dimension": "S",
            "text": "You build enduring, trustworthy professional partnerships founded on mutual respect, patience, and unwavering consistency.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_18",
            "dimension": "S",
            "text": "You take deliberate care to ensure transitions and changes are introduced gently to prevent unnecessary team stress.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_s_19",
            "dimension": "S",
            "text": "You are deeply committed to harmony in the workplace and actively defuse tensions through steady, peaceful mediation.",
            "scale_type": "likert_5"
        },
        # --- Conscientiousness (C) — 18 Items ---
        {
            "id": "disc_c_1",
            "dimension": "C",
            "text": "You insist on rigorous analytical precision, high quality benchmarks, and meticulous attention to detail.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_2",
            "dimension": "C",
            "text": "You systematically audit assumptions, verify raw data, and identify latent edge cases before declaring a deliverable ready.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_3",
            "dimension": "C",
            "text": "You prefer structured frameworks, codified guidelines, and verifiable criteria over subjective impressions.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_4",
            "dimension": "C",
            "text": "You invest significant effort into crafting clear, comprehensive documentation and operational audit trails.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_5",
            "dimension": "C",
            "text": "You feel uncomfortable submitting work that contains even minor formatting errors or statistical inconsistencies.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_6",
            "dimension": "C",
            "text": "You evaluate proposals with dispassionate skepticism until empirical proof or historical data is presented.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_7",
            "dimension": "C",
            "text": "You believe adhering to proven engineering or operational standards is the best guarantee of sustainable excellence.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_8",
            "dimension": "C",
            "text": "You prefer having adequate time to conduct thorough research rather than being rushed into superficial conclusions.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_9",
            "dimension": "C",
            "text": "You take pride in creating elegant, well-ordered systems that minimize ambiguity and eliminate operational waste.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_10",
            "dimension": "C",
            "text": "You routinely perform stress testing and risk assessments to ensure critical workflows cannot fail unexpectedly.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_11",
            "dimension": "C",
            "text": "You rigorously audit data, formulas, and technical artifacts to verify absolute factual correctness before sign-off.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_12",
            "dimension": "C",
            "text": "You adhere strictly to engineering best practices, compliance guidelines, and systematic quality assurance standards.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_13",
            "dimension": "C",
            "text": "You insist on clear empirical evidence and verified validation benchmarks before endorsing novel strategic claims.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_14",
            "dimension": "C",
            "text": "You design detailed systems, checklists, and standardized documentation to prevent human error and operational regressions.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_15",
            "dimension": "C",
            "text": "You enjoy deep analytical troubleshooting where finding the root cause of an anomaly requires methodical persistence.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_16",
            "dimension": "C",
            "text": "You prefer working in environments with well-defined standards of excellence where precision is recognized and rewarded.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_17",
            "dimension": "C",
            "text": "You carefully weigh every potential variable and risk factor before committing to an architectural or financial strategy.",
            "scale_type": "likert_5"
        },
        {
            "id": "disc_c_18",
            "dimension": "C",
            "text": "You maintain an orderly, disciplined approach to problem solving and reject sloppy, hasty compromises in craftsmanship.",
            "scale_type": "likert_5"
        }
    ],

    "BIG_FIVE": [
        # --- Openness (O) — 15 Items ---
        {
            "id": "b5_o_1",
            "dimension": "O",
            "text": "You possess an active, vivid imagination and love exploring art, music, or philosophical questions.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_2",
            "dimension": "O",
            "text": "You actively seek out unfamiliar cultural viewpoints, foreign cuisines, and perspectives different from your own.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_3",
            "dimension": "O",
            "text": "You are deeply moved by aesthetic beauty in nature, architecture, poetry, or sophisticated design.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_4",
            "dimension": "O",
            "text": "You enjoy dissecting complex, abstract riddles purely for the joy of intellectual discovery.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_5",
            "dimension": "O",
            "text": "You are eager to question age-old customs and experiment with unorthodox solutions in your daily life.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_6",
            "dimension": "O",
            "text": "You enjoy reading across multiple diverse subjects such as history, technology, psychology, and cosmology.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_7",
            "dimension": "O",
            "text": "You find modern art, avant-garde cinema, and experimental music intriguing rather than baffling.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_8",
            "dimension": "O",
            "text": "You often reflect on metaphysical topics, the nature of consciousness, or the future of humanity.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_9",
            "dimension": "O",
            "text": "You readily adjust your core mental models when presented with a compelling new paradigm.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_10",
            "dimension": "O",
            "text": "You are intensely curious about avant-garde philosophical questions and novel schools of contemporary thought.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_11",
            "dimension": "O",
            "text": "You love immersing yourself in diverse artistic traditions, architectural innovations, and world cultural heritage.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_12",
            "dimension": "O",
            "text": "You are constantly experimenting with new intellectual tools, mental frameworks, and interdisciplinary methodologies.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_13",
            "dimension": "O",
            "text": "You find unconventional theories and speculative possibilities intellectually exhilarating rather than impractical.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_14",
            "dimension": "O",
            "text": "You actively seek out complex cinematic, literary, or musical works that challenge conventional narrative structures.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_o_15",
            "dimension": "O",
            "text": "You delight in re-examining your fundamental assumptions whenever you encounter persuasive, unorthodox perspectives.",
            "scale_type": "likert_5"
        },
        # --- Conscientiousness (C) — 15 Items ---
        {
            "id": "b5_c_1",
            "dimension": "C",
            "text": "You maintain an organized daily routine and keep your personal belongings and digital workspaces neatly arranged.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_2",
            "dimension": "C",
            "text": "When you commit to a deadline or promise, you follow through faithfully regardless of personal inconvenience.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_3",
            "dimension": "C",
            "text": "You systematically break down long-term objectives into concrete milestones and track your progress diligently.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_4",
            "dimension": "C",
            "text": "You demonstrate strong willpower and resist immediate distractions in order to complete demanding responsibilities.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_5",
            "dimension": "C",
            "text": "You review your work carefully multiple times to ensure nothing has been overlooked before sending it out.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_6",
            "dimension": "C",
            "text": "You pay bills, fulfill obligations, and arrive at scheduled appointments well ahead of the expected time.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_7",
            "dimension": "C",
            "text": "You plan your financial expenditures prudently and practice consistent saving for future contingencies.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_8",
            "dimension": "C",
            "text": "You avoid leaving tasks half-finished and persist through mundane chores until everything is properly settled.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_9",
            "dimension": "C",
            "text": "You hold yourself personally accountable for your mistakes rather than blaming external circumstances.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_10",
            "dimension": "C",
            "text": "You consistently organize your workload with meticulous precision, tracking tasks, milestones, and dependencies methodically.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_11",
            "dimension": "C",
            "text": "You maintain exceptional self-discipline and persist through grueling, repetitive tasks without losing focus or quality.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_12",
            "dimension": "C",
            "text": "You take personal pride in being impeccably prepared for every meeting, review, and operational commitment.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_13",
            "dimension": "C",
            "text": "You follow through on commitments with uncompromising rigor, even when unforeseen obstacles demand long hours.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_14",
            "dimension": "C",
            "text": "You systematically eliminate inefficiencies from your daily schedule through structured planning and prioritization.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_c_15",
            "dimension": "C",
            "text": "You double-check calculations, configurations, and deliverable specifications to guarantee flawless precision.",
            "scale_type": "likert_5"
        },
        # --- Extraversion (E) — 15 Items ---
        {
            "id": "b5_e_1",
            "dimension": "E",
            "text": "You have an exuberant, cheerful disposition and express your emotions with warmth and animated energy.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_2",
            "dimension": "E",
            "text": "You readily strike up engaging conversations with cab drivers, baristas, or strangers standing in line.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_3",
            "dimension": "E",
            "text": "You thrive in bustling environments characterized by lively sounds, physical movement, and continuous social activity.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_4",
            "dimension": "E",
            "text": "You speak in a vibrant, confident tone and naturally draw listeners into your conversations.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_5",
            "dimension": "E",
            "text": "You actively seek leadership opportunities and enjoy organizing group outings, clubs, or social events.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_6",
            "dimension": "E",
            "text": "You feel restless, understimulated, and bored when spending an entire weekend completely isolated from people.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_7",
            "dimension": "E",
            "text": "You are known among friends as someone who brings life and enthusiastic vitality into any room you enter.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_8",
            "dimension": "E",
            "text": "You prefer fast-paced, action-packed hobbies over quiet, sedentary solitary pastimes.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_9",
            "dimension": "E",
            "text": "You express your opinions with bold self-assurance without worrying excessively about how others might judge you.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_10",
            "dimension": "E",
            "text": "You are consistently energetic, talkative, and vivacious in social settings, bringing positive momentum to conversations.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_11",
            "dimension": "E",
            "text": "You naturally take the spotlight in group discussions and communicate your perspectives with assertiveness and passion.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_12",
            "dimension": "E",
            "text": "You thrive in high-stimulation environments filled with vibrant music, lively conversations, and rapid social exchanges.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_13",
            "dimension": "E",
            "text": "You actively initiate social gatherings and enjoy bringing diverse groups of people together for shared celebrations.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_14",
            "dimension": "E",
            "text": "You express your feelings and enthusiasm outwardly and openly, radiating warmth and excitement to those around you.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_e_15",
            "dimension": "E",
            "text": "You prefer engaging in fast-paced collaborative group projects over long periods of solitary, uninterrupted execution.",
            "scale_type": "likert_5"
        },
        # --- Agreeableness (A) — 15 Items ---
        {
            "id": "b5_a_1",
            "dimension": "A",
            "text": "You instinctively assume the best in people and believe that human nature is fundamentally benevolent.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_2",
            "dimension": "A",
            "text": "You readily lend a helping hand or offer emotional solace to someone in distress without expecting reciprocity.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_3",
            "dimension": "A",
            "text": "You are genuinely modest about your talents and feel uncomfortable boasting about your accomplishments.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_4",
            "dimension": "A",
            "text": "You treat people from every walk of life with sincere respect, dignity, and polite attentiveness.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_5",
            "dimension": "A",
            "text": "You find it easy to forgive someone who wronged you and rarely harbor lingering grudges or vengeful thoughts.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_6",
            "dimension": "A",
            "text": "You go out of your way to accommodate the preferences and comfort of your companions when planning activities.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_7",
            "dimension": "A",
            "text": "You are deeply touched by the hardships of vulnerable communities and feel compelled to support charitable causes.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_8",
            "dimension": "A",
            "text": "You avoid sarcastic or condescending remarks and strive to make everyone around you feel valued and accepted.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_9",
            "dimension": "A",
            "text": "You naturally assume that people have good intentions and prefer extending trust rather than cultivating cynical skepticism.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_10",
            "dimension": "A",
            "text": "You go out of your way to assist coworkers or neighbors in distress, giving generously of your time and resources.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_11",
            "dimension": "A",
            "text": "You are gentle, courteous, and polite in your interactions, treating everyone you meet with unconditional dignity.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_12",
            "dimension": "A",
            "text": "You seek compromise and common ground in arguments, prioritizing peaceful reconciliation over asserting dominance.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_13",
            "dimension": "A",
            "text": "You are deeply sensitive to the feelings of others and feel genuine sorrow when someone around you is suffering.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_14",
            "dimension": "A",
            "text": "You cooperate willingly with group decisions, prioritizing collective team harmony over individual personal preferences.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_a_15",
            "dimension": "A",
            "text": "You forgive transgressions readily and hold no grudges against colleagues who make honest, unintentional mistakes.",
            "scale_type": "likert_5"
        },
        # --- Neuroticism (N) — 15 Items ---
        {
            "id": "b5_n_1",
            "dimension": "N",
            "text": "You frequently experience waves of tension, unease, or worry even when things are running reasonably well.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_2",
            "dimension": "N",
            "text": "An unexpected criticism or minor social awkwardness can loop in your mind for hours afterward.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_3",
            "dimension": "N",
            "text": "You find it difficult to soothe your nerves and sleep peacefully when facing an upcoming evaluation or test.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_4",
            "dimension": "N",
            "text": "Your emotional mood can fluctuate sharply throughout the day in response to minor environmental triggers.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_5",
            "dimension": "N",
            "text": "When confronting significant uncertainty, your mind quickly jumps to the worst-case scenario.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_6",
            "dimension": "N",
            "text": "You often feel overwhelmed or emotionally drained when unexpected obstacles disrupt your plans.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_7",
            "dimension": "N",
            "text": "You occasionally struggle with self-doubt and question whether your abilities measure up to those of your peers.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_8",
            "dimension": "N",
            "text": "You are prone to physical manifestations of stress, such as a racing heart or tense muscles, during conflicts.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_9",
            "dimension": "N",
            "text": "You frequently experience feelings of apprehension or self-consciousness when entering unfamiliar social gatherings.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_10",
            "dimension": "N",
            "text": "Small everyday irritations or administrative delays can trigger noticeable feelings of anxiety and impatience.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_11",
            "dimension": "N",
            "text": "You often replay past awkward interactions in your head, analyzing what you should have said differently.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_12",
            "dimension": "N",
            "text": "You feel deeply unsettled when facing ambiguous deadlines or unpredictable changes in project requirements.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_13",
            "dimension": "N",
            "text": "You find it challenging to shake off persistent feelings of dread or impending difficulty during stressful seasons.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_14",
            "dimension": "N",
            "text": "Your self-confidence can waver significantly when you encounter unexpected criticism or cold indifference from peers.",
            "scale_type": "likert_5"
        },
        {
            "id": "b5_n_15",
            "dimension": "N",
            "text": "You are easily startled by sudden loud noises or abrupt environmental disruptions when concentrating on work.",
            "scale_type": "likert_5"
        }
    ]
}
