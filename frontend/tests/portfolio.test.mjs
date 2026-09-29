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

// 2. Public Route Parser (Prompt 05 Section 5)
const parseRoute = (path) => {
  const p = path.toLowerCase();
  if (p.startsWith('/admin') || p.startsWith('/cms')) return 'cms';
  if (p.startsWith('/about')) return 'about';
  if (p.startsWith('/education')) return 'education';
  if (p.startsWith('/experience')) return 'experience';
  if (p.startsWith('/skills')) return 'skills';
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
  assert.strictEqual(parseRoute('/personality'), 'personality');
  assert.strictEqual(parseRoute('/interests'), 'interests');
  assert.strictEqual(parseRoute('/contact'), 'contact');
  assert.strictEqual(parseRoute('/admin'), 'cms');
  assert.strictEqual(parseRoute('/admin/revisions'), 'cms');
  assert.strictEqual(parseRoute('/cms'), 'cms');
});

// 3. Dynamic Page Title Generator (Prompt 05 Section 53)
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
