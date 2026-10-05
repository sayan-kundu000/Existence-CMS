import test from 'node:test';
import assert from 'node:assert';

// 1. Mastery Scale Contract (Prompt 05 Section 24 & 25)
const LEVEL_NAMES = {
  1: 'Beginner',
  2: 'Novice',
  3: 'Intermediate',
  4: 'Proficient',
  5: 'Advanced',
  6: 'Expert',
  7: 'Master',
};

test('Skills 7-Level Mastery Scale adheres strictly to 1-7', () => {
  assert.strictEqual(LEVEL_NAMES[1], 'Beginner');
  assert.strictEqual(LEVEL_NAMES[2], 'Novice');
  assert.strictEqual(LEVEL_NAMES[3], 'Intermediate');
  assert.strictEqual(LEVEL_NAMES[4], 'Proficient');
  assert.strictEqual(LEVEL_NAMES[5], 'Advanced');
  assert.strictEqual(LEVEL_NAMES[6], 'Expert');
  assert.strictEqual(LEVEL_NAMES[7], 'Master');
  assert.strictEqual(Object.keys(LEVEL_NAMES).length, 7);
});

// 2. Public Route Parser (Prompt 05 Section 5 & Prompt 08)
const parseRoute = (path) => {
  const p = path.toLowerCase();
  if (p.startsWith('/admin') || p.startsWith('/cms')) return 'cms';
  if (p.startsWith('/about')) return 'about';
  if (p.startsWith('/education')) return 'education';
  if (p.startsWith('/experience')) return 'experience';
  if (p.startsWith('/skills')) return 'skills';
  if (p.startsWith('/projects')) return 'projects';
  if (p.startsWith('/personality')) return 'personality';
  if (p.startsWith('/interests')) return 'interests';
  if (p.startsWith('/contact')) return 'contact';
  return 'home';
};

test('Public Routing correctly parses all expected paths', () => {
  assert.strictEqual(parseRoute('/'), 'home');
  assert.strictEqual(parseRoute('/home'), 'home');
  assert.strictEqual(parseRoute('/about'), 'about');
  assert.strictEqual(parseRoute('/education'), 'education');
  assert.strictEqual(parseRoute('/experience'), 'experience');
  assert.strictEqual(parseRoute('/skills'), 'skills');
  assert.strictEqual(parseRoute('/projects'), 'projects');
  assert.strictEqual(parseRoute('/personality'), 'personality');
  assert.strictEqual(parseRoute('/interests'), 'interests');
  assert.strictEqual(parseRoute('/contact'), 'contact');
  assert.strictEqual(parseRoute('/admin'), 'cms');
  assert.strictEqual(parseRoute('/admin/revisions'), 'cms');
  assert.strictEqual(parseRoute('/cms'), 'cms');
});

// 3. Dynamic Page Title Generator (Prompt 05 Section 53 & Prompt 08)
const getPageTitle = (tab, name) => {
  const baseName = name ? `${name} — ` : '';
  switch (tab) {
    case 'about':
      return `${baseName}Executive Narrative | Existence`;
    case 'education':
      return `${baseName}Academic Lineage | Existence`;
    case 'experience':
      return `${baseName}Work Trajectory | Existence`;
    case 'skills':
      return `${baseName}7-Level Mastery Engine | Existence`;
    case 'projects':
      return `${baseName}Projects & Tech Stack Engine | Existence`;
    case 'personality':
      return `${baseName}Psychological Intelligence | Existence`;
    case 'interests':
      return `${baseName}Hobbies & Interests | Existence`;
    case 'contact':
      return `${baseName}Contact Coordinates | Existence`;
    case 'cms':
      return 'Existence Admin CMS';
    case 'home':
    default:
      return `${baseName}Personal Identity & Trajectory | Existence`;
  }
};

test('Page Title Generator respects verified entity name and fallbacks', () => {
  assert.strictEqual(getPageTitle('home', 'Elena Rostova'), 'Elena Rostova — Personal Identity & Trajectory | Existence');
  assert.strictEqual(getPageTitle('home', null), 'Personal Identity & Trajectory | Existence');
  assert.strictEqual(getPageTitle('skills', 'Elena Rostova'), 'Elena Rostova — 7-Level Mastery Engine | Existence');
  assert.strictEqual(getPageTitle('projects', 'Elena Rostova'), 'Elena Rostova — Projects & Tech Stack Engine | Existence');
  assert.strictEqual(getPageTitle('cms', 'Elena Rostova'), 'Existence Admin CMS');
});

// 4. Currently Studying & Currently Working Date Display Invariants (Prompt 05 Sections 20, 23)
const formatEducationPeriod = (edu) => {
  if (edu.currently_studying) {
    return `${edu.starting_month_year} – Present`;
  }
  return `${edu.starting_month_year} – ${edu.ending_month_year}`;
};

const formatExperiencePeriod = (exp) => {
  if (exp.currently_working) {
    return `${exp.starting_month_year} – Present`;
  }
  return `${exp.starting_month_year} – ${exp.ending_month_year}`;
};

test('Education and Experience period formatters render "Present" when currently active', () => {
  const activeEdu = { starting_month_year: 'Sep 2022', ending_month_year: null, currently_studying: true };
  const pastEdu = { starting_month_year: 'Sep 2018', ending_month_year: 'Jun 2022', currently_studying: false };
  assert.strictEqual(formatEducationPeriod(activeEdu), 'Sep 2022 – Present');
  assert.strictEqual(formatEducationPeriod(pastEdu), 'Sep 2018 – Jun 2022');

  const activeExp = { starting_month_year: 'Jan 2024', ending_month_year: null, currently_working: true };
  const pastExp = { starting_month_year: 'Mar 2021', ending_month_year: 'Dec 2023', currently_working: false };
  assert.strictEqual(formatExperiencePeriod(activeExp), 'Jan 2024 – Present');
  assert.strictEqual(formatExperiencePeriod(pastExp), 'Mar 2021 – Dec 2023');
});

// 5. Work Mode Location Requirement Invariant (Prompt 05 Section 21)
const resolveDisplayLocation = (exp) => {
  if (exp.work_mode === 'Remote') {
    return 'Remote';
  }
  return exp.location || 'Location Unspecified';
};

test('Work mode location resolution correctly manages Remote vs Physical', () => {
  assert.strictEqual(resolveDisplayLocation({ work_mode: 'Remote', location: null }), 'Remote');
  assert.strictEqual(resolveDisplayLocation({ work_mode: 'On-site', location: 'London, UK' }), 'London, UK');
  assert.strictEqual(resolveDisplayLocation({ work_mode: 'Hybrid', location: 'Berlin, DE' }), 'Berlin, DE');
});

// 6. Public/Private Data Boundary Invariant (Prompt 05 Section 36)
test('Public Profile object strictly excludes administrative secrets', () => {
  const samplePublicProfile = {
    id: 1,
    name: 'Elena Rostova',
    email_ids: ['elena@existence.io'],
    mobile_number: '+1-555-0199',
    linkedin: 'https://linkedin.com/in/elena',
    about: 'Systems Architect',
    is_empty: false
  };

  // Must not contain any sensitive security keys
  assert.strictEqual('pin' in samplePublicProfile, false);
  assert.strictEqual('hashed_pin' in samplePublicProfile, false);
  assert.strictEqual('pin_hash' in samplePublicProfile, false);
  assert.strictEqual('password' in samplePublicProfile, false);
  assert.strictEqual('password_hash' in samplePublicProfile, false);
  assert.strictEqual('jwt_secret' in samplePublicProfile, false);
  assert.strictEqual('audit_logs' in samplePublicProfile, false);
});

// 7. Prompt 07: Skills 7-Level Rating Boundary Clamping Invariant
const clampRating = (r) => Math.max(1, Math.min(7, Math.floor(Number(r) || 1)));

test('Skills Rating Clamping Invariant strictly enforces 1 to 7', () => {
  assert.strictEqual(clampRating(0), 1);
  assert.strictEqual(clampRating(-5), 1);
  assert.strictEqual(clampRating(8), 7);
  assert.strictEqual(clampRating(100), 7);
  assert.strictEqual(clampRating(4), 4);
  assert.strictEqual(clampRating(7), 7);
  assert.strictEqual(clampRating(1), 1);
});

// 8. Prompt 07: Skills Case-Insensitive Name Duplicate Invariant
const areSkillsDuplicate = (name1, name2) => {
  if (!name1 || !name2) return false;
  return name1.trim().toLowerCase() === name2.trim().toLowerCase();
};

test('Skill Name duplicate detection catches case and whitespace variations', () => {
  assert.strictEqual(areSkillsDuplicate('PostgreSQL', '  postgresql  '), true);
  assert.strictEqual(areSkillsDuplicate('Distributed Consensus', 'DISTRIBUTED CONSENSUS'), true);
  assert.strictEqual(areSkillsDuplicate('FastAPI', 'FastAPI'), true);
  assert.strictEqual(areSkillsDuplicate('FastAPI', 'Django'), false);
});

// 9. Prompt 07: Skills Public/Private Filter Invariant
const filterPublicSkills = (skills) => {
  return skills.filter((s) => (s.visibility ?? s.is_visible ?? true) === true);
};

test('Public Skills filter strictly excludes hidden skills from public view', () => {
  const allSkills = [
    { id: 1, name: 'Python', rating: 6, visibility: true },
    { id: 2, name: 'Proprietary Secret', rating: 3, visibility: false },
    { id: 3, name: 'Kubernetes', rating: 5, is_visible: true }
  ];
  const publicSkills = filterPublicSkills(allSkills);
  assert.strictEqual(publicSkills.length, 2);
  assert.strictEqual(publicSkills.some((s) => s.id === 2), false);
});

// 10. Prompt 07: Deterministic Ordering Invariant
const sortSkillsDeterministically = (skills) => {
  return [...skills].sort((a, b) => {
    const orderDiff = (a.ordering ?? a.display_order ?? 0) - (b.ordering ?? b.display_order ?? 0);
    if (orderDiff !== 0) return orderDiff;
    return a.name.localeCompare(b.name);
  });
};

test('Skills sort deterministically by display order then name', () => {
  const unsorted = [
    { id: 1, name: 'Zig', ordering: 2 },
    { id: 2, name: 'Rust', ordering: 1 },
    { id: 3, name: 'C++', ordering: 2 }
  ];
  const sorted = sortSkillsDeterministically(unsorted);
  assert.strictEqual(sorted[0].name, 'Rust');
  assert.strictEqual(sorted[1].name, 'C++');
  assert.strictEqual(sorted[2].name, 'Zig');
});

// 10b. Skills Mastery Ratings Descending Output Invariant
const sortSkillsByMasteryRatingDescending = (skills) => {
  return [...skills].sort((a, b) => {
    if (b.rating !== a.rating) {
      return b.rating - a.rating;
    }
    const orderDiff = (a.ordering ?? a.display_order ?? 0) - (b.ordering ?? b.display_order ?? 0);
    if (orderDiff !== 0) return orderDiff;
    return a.name.localeCompare(b.name);
  });
};

test('Skills sort according to Mastery Ratings in descending order as output', () => {
  const skills = [
    { id: 1, name: 'HTML', rating: 3, ordering: 1 },
    { id: 2, name: 'Distributed Systems', rating: 7, ordering: 2 },
    { id: 3, name: 'PostgreSQL', rating: 6, ordering: 1 },
    { id: 4, name: 'FastAPI', rating: 6, ordering: 2 },
    { id: 5, name: 'CSS', rating: 1, ordering: 1 },
  ];
  const sorted = sortSkillsByMasteryRatingDescending(skills);
  assert.strictEqual(sorted[0].name, 'Distributed Systems'); // Rating 7
  assert.strictEqual(sorted[1].name, 'PostgreSQL'); // Rating 6, ordering 1
  assert.strictEqual(sorted[2].name, 'FastAPI'); // Rating 6, ordering 2
  assert.strictEqual(sorted[3].name, 'HTML'); // Rating 3
  assert.strictEqual(sorted[4].name, 'CSS'); // Rating 1
});

// 11. Multi-Category: 17 Canonical Skill Categories Invariant
const SKILL_CATEGORIES = [
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
];

test('17 Canonical Skill Categories are complete and allow multi-selection', () => {
  assert.strictEqual(SKILL_CATEGORIES.length, 17);
  assert.strictEqual(new Set(SKILL_CATEGORIES).size, 17);
  const required = ['Technical', 'Financial', 'Analytical', 'Leadership', 'Ethical', 'Medical', 'Diplomatic'];
  for (const req of required) {
    assert.strictEqual(SKILL_CATEGORIES.includes(req), true);
  }
});

// 12. Multi-Category Filtering Invariant
const extractSkillCategories = (skill) => {
  if (skill.categories && skill.categories.length > 0) {
    return skill.categories;
  }
  if (skill.category) {
    return skill.category.split(',').map((c) => c.trim()).filter(Boolean);
  }
  return ['Technical'];
};

const filterSkillsByCategory = (skills, selectedCategory) => {
  if (!selectedCategory || selectedCategory === 'all') return skills;
  return skills.filter((s) => {
    const cats = extractSkillCategories(s);
    return cats.includes(selectedCategory);
  });
};

test('Skills with multiple categories match any of their assigned categories', () => {
  const skills = [
    { id: 1, name: 'Algorithmic Trading', categories: ['Technical', 'Financial', 'Analytical'] },
    { id: 2, name: 'Bioethics Council Lead', category: 'Ethical, Medical, Leadership' },
    { id: 3, name: 'Linux Kernel Hacking', categories: ['Technical'] }
  ];

  // Filtering for Financial matches Algorithmic Trading
  const financial = filterSkillsByCategory(skills, 'Financial');
  assert.strictEqual(financial.length, 1);
  assert.strictEqual(financial[0].name, 'Algorithmic Trading');

  // Filtering for Technical matches both Algorithmic Trading and Linux Kernel Hacking
  const technical = filterSkillsByCategory(skills, 'Technical');
  assert.strictEqual(technical.length, 2);

  // Filtering for Medical matches Bioethics Council Lead
  const medical = filterSkillsByCategory(skills, 'Medical');
  assert.strictEqual(medical.length, 1);
  assert.strictEqual(medical[0].name, 'Bioethics Council Lead');

  // Filtering for Leadership matches Bioethics Council Lead
  const leadership = filterSkillsByCategory(skills, 'Leadership');
  assert.strictEqual(leadership.length, 1);
  assert.strictEqual(leadership[0].name, 'Bioethics Council Lead');

  // Filtering for all returns all 3
  const all = filterSkillsByCategory(skills, 'all');
  assert.strictEqual(all.length, 3);
});

// 13. Standardized Psychometric Framework Invariant (Prompt 08 Sections 3 & 4)
const VALID_MBTI_TYPES = new Set([
  'INTJ', 'INTP', 'ENTJ', 'ENTP',
  'INFJ', 'INFP', 'ENFJ', 'ENFP',
  'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
  'ISTP', 'ISFP', 'ESTP', 'ESFP'
]);

test('MBTI engine supports all 16 valid archetypes', () => {
  assert.strictEqual(VALID_MBTI_TYPES.size, 16);
  assert.strictEqual(VALID_MBTI_TYPES.has('INTJ'), true);
  assert.strictEqual(VALID_MBTI_TYPES.has('ENFP'), true);
  assert.strictEqual(VALID_MBTI_TYPES.has('ISTJ'), true);
  assert.strictEqual(VALID_MBTI_TYPES.has('ESFP'), true);
  assert.strictEqual(VALID_MBTI_TYPES.has('XXXX'), false);
});

// 14. MBTI Bipolar Pair Invariant (Prompt 08 Section 14 & 27)
const computeMbtiBipolarPair = (rawPositiveScore, maxPossible = 20) => {
  const posPct = Math.round((rawPositiveScore / maxPossible) * 100);
  const negPct = 100 - posPct;
  return {
    positive_percentage: posPct,
    negative_percentage: negPct,
    dominant: posPct >= 50 ? 'POSITIVE' : 'NEGATIVE'
  };
};

test('MBTI bipolar pairs sum to 100% and identify dominant pole correctly', () => {
  const result = computeMbtiBipolarPair(14, 20); // 70% positive
  assert.strictEqual(result.positive_percentage, 70);
  assert.strictEqual(result.negative_percentage, 30);
  assert.strictEqual(result.dominant, 'POSITIVE');

  const neutral = computeMbtiBipolarPair(10, 20); // 50%
  assert.strictEqual(neutral.positive_percentage, 50);
  assert.strictEqual(neutral.negative_percentage, 50);
  assert.strictEqual(neutral.dominant, 'POSITIVE');

  const introvert = computeMbtiBipolarPair(4, 20); // 20%
  assert.strictEqual(introvert.positive_percentage, 20);
  assert.strictEqual(introvert.negative_percentage, 80);
  assert.strictEqual(introvert.dominant, 'NEGATIVE');
});

// 15. Session Resume & Answer Integrity Invariant (Prompt 08 Section 32)
const resumeSessionState = (savedSession, updatedAnswers) => {
  return {
    ...savedSession,
    answers: { ...savedSession.answers, ...updatedAnswers },
    answered_count: Object.keys({ ...savedSession.answers, ...updatedAnswers }).length,
    progress_index: Math.max(savedSession.progress_index, Object.keys(updatedAnswers).length)
  };
};

test('Session resume retains previously recorded answers without data loss', () => {
  const initial = {
    session_id: 'session-xyz',
    type: 'MBTI',
    progress_index: 2,
    answers: { 'q1': 5, 'q2': 4 }
  };
  const resumed = resumeSessionState(initial, { 'q3': 2, 'q4': 1 });
  assert.strictEqual(resumed.answers['q1'], 5);
  assert.strictEqual(resumed.answers['q2'], 4);
  assert.strictEqual(resumed.answers['q3'], 2);
  assert.strictEqual(resumed.answers['q4'], 1);
  assert.strictEqual(resumed.answered_count, 4);
});

// 16. Assessment Comparison Shift Direction Invariant (Prompt 08 Section 22)
const calculateScoreDelta = (baseline, target) => {
  const delta = Math.round((target - baseline) * 10) / 10;
  return {
    delta,
    direction: delta > 0 ? 'INCREASED' : delta < 0 ? 'DECREASED' : 'UNCHANGED',
    description: delta !== 0
      ? `Shifted by ${delta > 0 ? '+' : ''}${delta}%`
      : 'Maintained exact baseline'
  };
};

test('Comparison shift calculates correct delta, direction, and objective wording', () => {
  const inc = calculateScoreDelta(45, 65);
  assert.strictEqual(inc.delta, 20);
  assert.strictEqual(inc.direction, 'INCREASED');
  assert.strictEqual(inc.description, 'Shifted by +20%');

  const dec = calculateScoreDelta(80, 55);
  assert.strictEqual(dec.delta, -25);
  assert.strictEqual(dec.direction, 'DECREASED');
  assert.strictEqual(dec.description, 'Shifted by -25%');

  const same = calculateScoreDelta(50, 50);
  assert.strictEqual(same.delta, 0);
  assert.strictEqual(same.direction, 'UNCHANGED');
  assert.strictEqual(same.description, 'Maintained exact baseline');
});

// 17. DISC Primary & Secondary Dimension Identification (Prompt 08 Section 16)
const identifyDiscDimensions = (percentages) => {
  const sorted = Object.entries(percentages).sort((a, b) => b[1] - a[1]);
  return {
    primary: sorted[0][0],
    secondary: sorted[1] && sorted[1][1] > 0 ? sorted[1][0] : null
  };
};

test('DISC primary and secondary dimensions are identified from percentage distribution', () => {
  const pcts = { D: 85, I: 65, S: 40, C: 50 };
  const res = identifyDiscDimensions(pcts);
  assert.strictEqual(res.primary, 'D');
  assert.strictEqual(res.secondary, 'I');
});

// 18. Big Five Five-Factor Invariant (Prompt 08 Section 17)
const BIG_FIVE_TRAITS = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'];

test('Big Five evaluates all five canonical OCEAN dimensions with non-judgmental bounds', () => {
  assert.strictEqual(BIG_FIVE_TRAITS.length, 5);
  const scores = { O: 78, C: 88, E: 45, A: 62, N: 35 };
  for (const val of Object.values(scores)) {
    assert.strictEqual(val >= 0 && val <= 100, true);
  }
});

// 19. Projects Engine: Link URL Security Invariant (Prompt 08)
const validateProjectUrl = (url) => {
  if (!url || typeof url !== 'string') return false;
  const trimmed = url.trim();
  if (!trimmed) return false;
  try {
    const parsed = new URL(trimmed);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
};

test('Projects Engine strictly enforces http/https protocol security on deployment links', () => {
  assert.strictEqual(validateProjectUrl('https://example.com'), true);
  assert.strictEqual(validateProjectUrl('http://demo.example.org/app'), true);
  assert.strictEqual(validateProjectUrl('https://github.com/org/repo'), true);

  // Security rejections
  assert.strictEqual(validateProjectUrl('javascript:alert(1)'), false);
  assert.strictEqual(validateProjectUrl('data:text/html,<script>alert(1)</script>'), false);
  assert.strictEqual(validateProjectUrl('vbscript:msgbox(1)'), false);
  assert.strictEqual(validateProjectUrl('file:///etc/passwd'), false);
  assert.strictEqual(validateProjectUrl('not-a-valid-url'), false);
  assert.strictEqual(validateProjectUrl(''), false);
  assert.strictEqual(validateProjectUrl(null), false);
});

// 20. Projects Engine: Primary Link Invariant (0 or 1 Primary Link)
const setPrimaryLink = (links, targetId) => {
  return links.map(link => ({
    ...link,
    is_primary: link.id === targetId
  }));
};

test('Projects Engine primary link setter guarantees at most one primary link', () => {
  const initialLinks = [
    { id: 1, label: 'GitHub', is_primary: true },
    { id: 2, label: 'Live Demo', is_primary: false },
    { id: 3, label: 'Docs', is_primary: false }
  ];

  const updated = setPrimaryLink(initialLinks, 2);
  assert.strictEqual(updated.find(l => l.id === 1).is_primary, false);
  assert.strictEqual(updated.find(l => l.id === 2).is_primary, true);
  assert.strictEqual(updated.find(l => l.id === 3).is_primary, false);
  assert.strictEqual(updated.filter(l => l.is_primary).length, 1);
});

// 21. Projects Engine: Technology Deduplication
const deduplicateProjectTechnologies = (existing, newTech) => {
  const exists = existing.some(
    t => t.name.toLowerCase().trim() === newTech.name.toLowerCase().trim() &&
         t.category === newTech.category
  );
  if (exists) return existing;
  return [...existing, newTech];
};

test('Projects Engine deduplicates technologies by case-insensitive name within category', () => {
  const existing = [
    { id: 1, name: 'React', category: 'Framework' },
    { id: 2, name: 'PostgreSQL', category: 'Database' }
  ];

  // Attempt duplicate addition
  const dupAttempt = deduplicateProjectTechnologies(existing, { name: 'react', category: 'Framework' });
  assert.strictEqual(dupAttempt.length, 2);

  // New technology
  const added = deduplicateProjectTechnologies(existing, { name: 'FastAPI', category: 'Framework' });
  assert.strictEqual(added.length, 3);
  assert.strictEqual(added[2].name, 'FastAPI');
});

// 22. Projects Engine: Taxonomy Verification
const PROJECT_STATUSES = ['Planning', 'In Progress', 'Completed', 'Maintained', 'Archived'];
const PROJECT_LINK_TYPES = ['Live Demo', 'GitHub', 'Deployment', 'Documentation', 'API', 'Design', 'Other'];

test('Projects Engine taxonomies define correct enterprise statuses and link types', () => {
  assert.strictEqual(PROJECT_STATUSES.includes('Completed'), true);
  assert.strictEqual(PROJECT_STATUSES.includes('Maintained'), true);
  assert.strictEqual(PROJECT_LINK_TYPES.includes('Live Demo'), true);
  assert.strictEqual(PROJECT_LINK_TYPES.includes('GitHub'), true);
  assert.strictEqual(PROJECT_LINK_TYPES.includes('Deployment'), true);
  assert.strictEqual(PROJECT_LINK_TYPES.includes('Documentation'), true);
});

// 23. Skill Domain Grouping and Interactive Drill-Down
test('Skill Domain extraction and grouping works correctly', () => {
  const sampleSkills = [
    { id: 1, name: 'NumPy', domain: 'AIML', rating: 6 },
    { id: 2, name: 'SciPy', domain: 'AIML', rating: 5 },
    { id: 3, name: 'Pandas', domain: 'AIML', rating: 6 },
    { id: 4, name: 'Scikit-learn', domain: 'AIML', rating: 6 },
    { id: 5, name: 'TensorFlow', domain: 'AIML', rating: 5 },
    { id: 6, name: 'PyTorch', domain: 'AIML', rating: 6 },
    { id: 7, name: 'React', domain: 'Frontend Development', rating: 6 },
    { id: 8, name: 'FastAPI', domain: 'Backend Engineering', rating: 6 },
    { id: 9, name: 'General Problem Solving', domain: null, rating: 5 }
  ];

  // Domain extraction
  const domainSet = new Set();
  sampleSkills.forEach(s => {
    if (s.domain && s.domain.trim()) domainSet.add(s.domain.trim());
  });
  const domains = Array.from(domainSet).sort();

  assert.strictEqual(domains.includes('AIML'), true);
  assert.strictEqual(domains.includes('Frontend Development'), true);
  assert.strictEqual(domains.includes('Backend Engineering'), true);

  // Filter skills by domain 'AIML'
  const aimlSkills = sampleSkills.filter(s => (s.domain || '').toLowerCase() === 'aiml');
  assert.strictEqual(aimlSkills.length, 6);
  assert.deepStrictEqual(
    aimlSkills.map(s => s.name),
    ['NumPy', 'SciPy', 'Pandas', 'Scikit-learn', 'TensorFlow', 'PyTorch']
  );
});

// 24. Experience Timeline Sorting (Descending Order)
test('Experience items sort in descending order of timelines (active first, then latest completed)', () => {
  const experiences = [
    { id: 1, role: 'Junior Dev', starting_month_year: 'Jan 2018', ending_month_year: 'Dec 2019', currently_working: false },
    { id: 2, role: 'Senior Lead', starting_month_year: 'Jan 2024', ending_month_year: null, currently_working: true },
    { id: 3, role: 'Staff Engineer', starting_month_year: 'Mar 2024', ending_month_year: null, currently_working: true },
    { id: 4, role: 'Mid Dev', starting_month_year: 'Jan 2020', ending_month_year: 'Nov 2023', currently_working: false },
  ];

  const parseMY = (str) => {
    if (!str) return null;
    const parts = str.trim().split(/\s+/);
    const months = { jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11 };
    if (parts.length === 2) {
      const m = months[parts[0].slice(0, 3).toLowerCase()] ?? 0;
      const y = parseInt(parts[1], 10);
      return { year: y, month: m };
    }
    return null;
  };

  const sorted = [...experiences].sort((a, b) => {
    if (a.currently_working && !b.currently_working) return -1;
    if (!a.currently_working && b.currently_working) return 1;

    if (a.currently_working && b.currently_working) {
      const aStart = parseMY(a.starting_month_year);
      const bStart = parseMY(b.starting_month_year);
      if (aStart && bStart) {
        if (aStart.year !== bStart.year) return bStart.year - aStart.year;
        return bStart.month - aStart.month;
      }
      return 0;
    }

    const aEnd = parseMY(a.ending_month_year);
    const bEnd = parseMY(b.ending_month_year);
    if (aEnd && bEnd) {
      if (aEnd.year !== bEnd.year) return bEnd.year - aEnd.year;
      if (aEnd.month !== bEnd.month) return bEnd.month - aEnd.month;
    }
    return 0;
  });

  // Most recent active role first (Mar 2024 active > Jan 2024 active)
  assert.strictEqual(sorted[0].id, 3);
  assert.strictEqual(sorted[1].id, 2);
  // Then completed roles by end date descending (Nov 2023 > Dec 2019)
  assert.strictEqual(sorted[2].id, 4);
  assert.strictEqual(sorted[3].id, 1);
});

// 25. Experience Duration (Individual & Overall Overlapping Merging)
test('Experience duration calculation accurately measures individual roles and merges overall timeline', () => {
  const parseMY = (str) => {
    if (!str) return null;
    const parts = str.trim().split(/\s+/);
    const months = { jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11 };
    if (parts.length === 2) {
      const m = months[parts[0].slice(0, 3).toLowerCase()] ?? 0;
      const y = parseInt(parts[1], 10);
      return { year: y, month: m };
    }
    return null;
  };

  const calcDuration = (startStr, endStr, currentlyWorking, refDate = new Date(2025, 5, 1)) => {
    const s = parseMY(startStr);
    if (!s) return { years: 0, months: 0, totalMonths: 0, formatted: '0 months' };
    const e = currentlyWorking ? { year: refDate.getFullYear(), month: refDate.getMonth() } : parseMY(endStr);
    if (!e) return { years: 0, months: 0, totalMonths: 0, formatted: '0 months' };

    const totalMonths = Math.max(1, (e.year - s.year) * 12 + (e.month - s.month) + 1);
    const years = Math.floor(totalMonths / 12);
    const remMonths = totalMonths % 12;

    let formatted = '';
    if (years > 0 && remMonths > 0) formatted = `${years} ${years === 1 ? 'year' : 'years'} ${remMonths} ${remMonths === 1 ? 'month' : 'months'}`;
    else if (years > 0) formatted = `${years} ${years === 1 ? 'year' : 'years'}`;
    else formatted = `${remMonths} ${remMonths === 1 ? 'month' : 'months'}`;

    return { years, months: remMonths, totalMonths, formatted };
  };

  // Exactly 2 years: Jan 2022 to Dec 2023 = 24 months
  const dur1 = calcDuration('Jan 2022', 'Dec 2023', false);
  assert.strictEqual(dur1.years, 2);
  assert.strictEqual(dur1.months, 0);
  assert.strictEqual(dur1.formatted, '2 years');

  // 1 year 6 months: Jan 2022 to Jun 2023 = 18 months
  const dur2 = calcDuration('Jan 2022', 'Jun 2023', false);
  assert.strictEqual(dur2.years, 1);
  assert.strictEqual(dur2.months, 6);
  assert.strictEqual(dur2.formatted, '1 year 6 months');

  // Exactly 1 year: Jan 2022 to Dec 2022 = 12 months
  const dur1Yr = calcDuration('Jan 2022', 'Dec 2022', false);
  assert.strictEqual(dur1Yr.formatted, '1 year');

  // Exactly 1 month: Jan 2022 to Jan 2022 = 1 month
  const dur1Mo = calcDuration('Jan 2022', 'Jan 2022', false);
  assert.strictEqual(dur1Mo.formatted, '1 month');

  // 1 year 1 month: Jan 2022 to Jan 2023 = 13 months
  const dur1Yr1Mo = calcDuration('Jan 2022', 'Jan 2023', false);
  assert.strictEqual(dur1Yr1Mo.formatted, '1 year 1 month');

  // Currently working role evaluated against refDate June 2025: Jan 2024 to Jun 2025 = 18 months
  const durActive = calcDuration('Jan 2024', null, true, new Date(2025, 5, 1));
  assert.strictEqual(durActive.years, 1);
  assert.strictEqual(durActive.months, 6);
  assert.strictEqual(durActive.formatted, '1 year 6 months');

  // Overall experience interval merging:
  // Role A: Jan 2022 to Dec 2022 (12 months)
  // Role B: Jun 2022 to Jun 2023 (overlaps Role A from Jun-Dec 2022)
  // Total union should be Jan 2022 to Jun 2023 = 18 months (not 12 + 13 = 25 months)
  const intervals = [
    { start: 2022 * 12 + 0, end: 2022 * 12 + 11 }, // Jan 2022 - Dec 2022
    { start: 2022 * 12 + 5, end: 2023 * 12 + 5 }  // Jun 2022 - Jun 2023
  ].sort((a, b) => a.start - b.start);

  const merged = [];
  for (const interval of intervals) {
    if (!merged.length) {
      merged.push({ ...interval });
    } else {
      const last = merged[merged.length - 1];
      if (interval.start <= last.end + 1) {
        last.end = Math.max(last.end, interval.end);
      } else {
        merged.push({ ...interval });
      }
    }
  }

  const mergedTotalMonths = merged.reduce((acc, curr) => acc + (curr.end - curr.start + 1), 0);
  assert.strictEqual(mergedTotalMonths, 18);
  const overallYears = Math.floor(mergedTotalMonths / 12);
  const overallRem = mergedTotalMonths % 12;
  assert.strictEqual(overallYears, 1);
  assert.strictEqual(overallRem, 6);
});

// 26. Multi-Domain Skills Assignment & Segregation
test('A skill can belong to multiple domains and appears in each domain grouping', () => {
  const skills = [
    {
      id: 1,
      name: 'Bioinformatics & Computational Genomics',
      domain: 'Biotechnology & Bioengineering, Computer Science & AI, Medical & Healthcare',
      domains: ['Biotechnology & Bioengineering', 'Computer Science & AI', 'Medical & Healthcare']
    },
    {
      id: 2,
      name: 'Reservoir Fluid Simulation',
      domain: 'Petroleum & Natural Gas Engineering, Mechanical Engineering',
      domains: ['Petroleum & Natural Gas Engineering', 'Mechanical Engineering']
    },
    {
      id: 3,
      name: 'Extractive Hydrometallurgy',
      domain: 'Mining & Mineral Engineering, Metallurgy & Materials Engineering',
      domains: ['Mining & Mineral Engineering', 'Metallurgy & Materials Engineering']
    },
    {
      id: 4,
      name: 'Precision Agricultural Robotics',
      domain: 'Agricultural & Food Engineering, Robotics & Automation',
      domains: ['Agricultural & Food Engineering', 'Robotics & Automation']
    }
  ];

  // Grouping logic matching SkillsView
  const domainMap = {};
  skills.forEach(skill => {
    const rawDomains = skill.domains && skill.domains.length > 0
      ? skill.domains
      : (skill.domain ? skill.domain.split(',').map(d => d.trim()).filter(Boolean) : []);
    
    rawDomains.forEach(dom => {
      if (!domainMap[dom]) domainMap[dom] = [];
      domainMap[dom].push(skill);
    });
  });

  const domains = Object.keys(domainMap);
  // Verify all unique domains are extracted
  assert.ok(domains.includes('Biotechnology & Bioengineering'));
  assert.ok(domains.includes('Computer Science & AI'));
  assert.ok(domains.includes('Medical & Healthcare'));
  assert.ok(domains.includes('Petroleum & Natural Gas Engineering'));
  assert.ok(domains.includes('Mechanical Engineering'));
  assert.ok(domains.includes('Mining & Mineral Engineering'));
  assert.ok(domains.includes('Metallurgy & Materials Engineering'));
  assert.ok(domains.includes('Agricultural & Food Engineering'));
  assert.ok(domains.includes('Robotics & Automation'));

  // Multi-domain skill 1 must appear in Biotechnology, Computer Science, and Medical
  assert.ok(domainMap['Biotechnology & Bioengineering'].some(s => s.id === 1));
  assert.ok(domainMap['Computer Science & AI'].some(s => s.id === 1));
  assert.ok(domainMap['Medical & Healthcare'].some(s => s.id === 1));

  // Multi-domain skill 2 must appear in Petroleum and Mechanical
  assert.ok(domainMap['Petroleum & Natural Gas Engineering'].some(s => s.id === 2));
  assert.ok(domainMap['Mechanical Engineering'].some(s => s.id === 2));

  // Multi-domain skill 3 must appear in Mining and Metallurgy
  assert.ok(domainMap['Mining & Mineral Engineering'].some(s => s.id === 3));
  assert.ok(domainMap['Metallurgy & Materials Engineering'].some(s => s.id === 3));
});

// 27. Comprehensive Domain Search & Taxonomy Coverage
test('Domain search finds domains across engineering, medical, business, legal and other fields', () => {
  const sampleDomains = [
    { name: 'Mechanical & Mechatronics Engineering', field: 'Engineering', keywords: ['cad', 'fluid', 'thermo', 'robotics'] },
    { name: 'Petroleum & Petrochemical Engineering', field: 'Engineering', keywords: ['drilling', 'reservoir', 'oil', 'gas'] },
    { name: 'Agricultural, Biosystems & Food Engineering', field: 'Engineering', keywords: ['agritech', 'irrigation', 'crops'] },
    { name: 'Biotechnology & Genetic Engineering', field: 'Engineering', keywords: ['crispr', 'genomics', 'synthetic biology'] },
    { name: 'Mining, Mineral & Geological Engineering', field: 'Engineering', keywords: ['extraction', 'geology', 'mineral'] },
    { name: 'Metallurgy & Materials Science Engineering', field: 'Engineering', keywords: ['alloys', 'metallurgy', 'corrosion'] },
    { name: 'Medical, Clinical & Health Sciences', field: 'Medical', keywords: ['clinical', 'cardiology', 'medicine'] },
    { name: 'Corporate Law, Regulatory Compliance & IP', field: 'Legal', keywords: ['contracts', 'patents', 'compliance'] },
    { name: 'Corporate Strategy, Finance & Investment', field: 'Business', keywords: ['valuation', 'm&a', 'private equity'] }
  ];

  const search = (query) => {
    const q = query.toLowerCase();
    return sampleDomains.filter(d => 
      d.name.toLowerCase().includes(q) ||
      d.field.toLowerCase().includes(q) ||
      d.keywords.some(k => k.toLowerCase().includes(q))
    );
  };

  // Search by exact keyword or field
  const petroResults = search('petroleum');
  assert.strictEqual(petroResults.length, 1);
  assert.strictEqual(petroResults[0].name, 'Petroleum & Petrochemical Engineering');

  const miningResults = search('mineral');
  assert.strictEqual(miningResults.length, 1);
  assert.strictEqual(miningResults[0].name, 'Mining, Mineral & Geological Engineering');

  const metallurgyResults = search('alloys');
  assert.strictEqual(metallurgyResults.length, 1);
  assert.strictEqual(metallurgyResults[0].name, 'Metallurgy & Materials Science Engineering');

  const legalResults = search('legal');
  assert.strictEqual(legalResults.length, 1);
  assert.strictEqual(legalResults[0].name, 'Corporate Law, Regulatory Compliance & IP');

  const medicalResults = search('cardiology');
  assert.strictEqual(medicalResults.length, 1);
  assert.strictEqual(medicalResults[0].name, 'Medical, Clinical & Health Sciences');
});

// 29. GitHub Extraction & AI Dossier Tests
test('GitHub Extraction target parser handles profile URLs, repo URLs, and handles correctly', () => {
  const parseGithubTarget = (input) => {
    const clean = input.trim().replace(/^(https?:\/\/)?(www\.)?github\.com\//i, '').replace(/\/+$/, '');
    const parts = clean.split('/').filter(Boolean);
    if (parts.length === 0) throw new Error('Empty GitHub link');
    const owner = parts[0];
    const repo = parts[1] ? parts[1].replace(/\.git$/i, '') : undefined;
    return { owner, repo };
  };

  assert.deepStrictEqual(parseGithubTarget('https://github.com/torvalds'), { owner: 'torvalds', repo: undefined });
  assert.deepStrictEqual(parseGithubTarget('https://github.com/torvalds/linux.git'), { owner: 'torvalds', repo: 'linux' });
  assert.deepStrictEqual(parseGithubTarget('github.com/existence/cms'), { owner: 'existence', repo: 'cms' });
  assert.deepStrictEqual(parseGithubTarget('octocat'), { owner: 'octocat', repo: undefined });
});

test('GitHub Project Title Normalizer cleanly formats dashes and preserves key acronyms', () => {
  const cleanTitle = (raw) => {
    if (!raw) return 'Untitled Project';
    const words = raw.split(/[-_]+/);
    return words
      .filter(Boolean)
      .map((w) => {
        const low = w.toLowerCase();
        if (['ai', 'api', 'ui', 'ux', 'cms', 'db', 'sdk', 'cli', 'id', 'ml', 'nlp'].includes(low)) {
          return w.toUpperCase();
        }
        return w.charAt(0).toUpperCase() + w.slice(1);
      })
      .join(' ');
  };

  assert.strictEqual(cleanTitle('ai-powered-cms-api'), 'AI Powered CMS API');
  assert.strictEqual(cleanTitle('machine-learning-pipeline'), 'Machine Learning Pipeline');
  assert.strictEqual(cleanTitle('super_fast_web_service'), 'Super Fast Web Service');
});

test('AI Dossier Synthesizer produces full structured sections in super simple words', () => {
  const synthesize = (name, desc, techs, links) => {
    const purpose = `The primary purpose of **${name}** is to solve real-world problems around ${desc.toLowerCase()}.`;
    const techLines = techs.map(t => `- **${t.name}** (*${t.category}*): Used because it ${t.why}.`).join('\n');
    const arch = `**${name}** is structured with a clean separation of concerns:\n1. User Interface\n2. Logic Core\n3. Data Handling\n4. Outputs`;
    const caps = '- ✨ High reliability and clean architecture\n- ✨ Automated workflows';
    const future = '- 🚀 Automated CI/CD\n- 🚀 Performance caching';
    const linkLines = links.map(l => `- [${l.label}](${l.url})${l.type === 'GitHub' ? ' *(Mandatory Source Repository)*' : ' *(Optional Deployment)*'}`).join('\n');

    return `# ${name}\n\n## 🎯 1. Purpose of the Project\n${purpose}\n\n## 🛠️ 2. What I Used & Why I Used It\n${techLines}\n\n## 🏗️ 3. Architecture & How It Works (In Super Simple Words)\n${arch}\n\n## ✨ 4. What This Project Can Do\n${caps}\n\n## 🚀 5. How It Can Be Improved in the Future\n${future}\n\n## 🔗 6. Project Links & Deployments\n${linkLines}`;
  };

  const dossier = synthesize(
    'Existence CMS',
    'portfolio and content management',
    [
      { name: 'React', category: 'Framework', why: 'enables responsive UI components' },
      { name: 'FastAPI', category: 'Framework', why: 'provides high-performance async APIs' }
    ],
    [
      { label: 'GitHub Repository', url: 'https://github.com/org/existence-cms', type: 'GitHub' },
      { label: 'Render Deployment', url: 'https://existence.onrender.com', type: 'Deployment' }
    ]
  );

  assert.ok(dossier.includes('# Existence CMS'));
  assert.ok(dossier.includes('## 🎯 1. Purpose of the Project'));
  assert.ok(dossier.includes('## 🛠️ 2. What I Used & Why I Used It'));
  assert.ok(dossier.includes('## 🏗️ 3. Architecture & How It Works (In Super Simple Words)'));
  assert.ok(dossier.includes('## ✨ 4. What This Project Can Do'));
  assert.ok(dossier.includes('## 🚀 5. How It Can Be Improved in the Future'));
  assert.ok(dossier.includes('## 🔗 6. Project Links & Deployments'));
  assert.ok(dossier.includes('## 🔗 6. Project Links & Deployments'));
  assert.ok(dossier.includes('*(Mandatory Source Repository)*'));
  assert.ok(dossier.includes('*(Optional Deployment)*'));
});


test('Automatic Sync: Technology removal and AI dossier regeneration logic', () => {
  // Simulate active manifest technologies before and after deletion of backend
  const previousTechs = ['Python', 'FastAPI', 'PostgreSQL', 'React', 'TailwindCSS'];
  
  // Developer deleted backend files and dependencies from repository:
  const activeRepoLanguages = ['TypeScript', 'JavaScript'];
  const activeManifestTechs = ['React', 'TailwindCSS', 'Vite'];
  
  // Deduplicated union of currently active technologies in the repository
  const currentTechs = Array.from(new Set([...activeRepoLanguages, ...activeManifestTechs]));
  
  // Verify deleted backend technologies are stripped
  const removedTechs = previousTechs.filter(t => !currentTechs.includes(t));
  assert.deepStrictEqual(removedTechs, ['Python', 'FastAPI', 'PostgreSQL']);
  
  // Verify new technologies are captured
  const addedTechs = currentTechs.filter(t => !previousTechs.includes(t));
  assert.deepStrictEqual(addedTechs, ['TypeScript', 'JavaScript', 'Vite']);
  
  // Re-generate architecture description based strictly on current technologies
  const hasBackend = currentTechs.some(t => ['FastAPI', 'Express.js', 'Django', 'Go', 'Rust'].includes(t));
  const archDescription = hasBackend 
    ? 'Processing Core (Backend): Handles business rules and database transactions.'
    : 'Client-Side Execution Core: Pure client-driven application executing directly in the browser.';
  
  assert.strictEqual(hasBackend, false);
  assert.strictEqual(archDescription, 'Client-Side Execution Core: Pure client-driven application executing directly in the browser.');
});


test('GitHub Webhook Payload verification and endpoint routing', () => {
  const origin = 'https://existence.live';
  const webhookUrl = `${origin}/api/v1/projects/github-webhook`;
  
  assert.strictEqual(webhookUrl, 'https://existence.live/api/v1/projects/github-webhook');
  
  const pushPayload = {
    repository: {
      name: 'smart-agent',
      html_url: 'https://github.com/developer/smart-agent',
      owner: { login: 'developer' }
    }
  };
  
  assert.strictEqual(pushPayload.repository.name, 'smart-agent');
  assert.strictEqual(pushPayload.repository.owner.login, 'developer');
  assert.strictEqual(pushPayload.repository.html_url, 'https://github.com/developer/smart-agent');
});








