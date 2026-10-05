import { ExtractedProject, ExtractedProjectLink, ExtractedTechnology, GitHubExtractionResponse, Project, ProjectLinkType } from '../types';

// Super-Simple plain English tech knowledge base using everyday physical analogies
const TECH_KNOWLEDGE: Record<string, { name: string; category: string; role: string; why: string }> = {
  python: {
    name: 'Python',
    category: 'Programming Language',
    role: 'The Master Recipe Chef',
    why: 'acts like a brilliant, patient master chef who reads every recipe instruction with absolute precision, handles heavy calculations effortlessly, and follows every instruction reliably without ever skipping a step'
  },
  javascript: {
    name: 'JavaScript',
    category: 'Programming Language',
    role: 'The Spark of Motion',
    why: 'brings buttons, menus, and cards to life with fluid movement, making elements expand, slide, and react smoothly the split-second you touch them'
  },
  typescript: {
    name: 'TypeScript',
    category: 'Programming Language',
    role: 'The Strict Safety Inspector',
    why: 'acts like a careful proofreader who inspects every single sentence and bolt before anything leaves the workshop floor, catching typos and mistakes early so the software never breaks down unexpectedly'
  },
  react: {
    name: 'React',
    category: 'Framework',
    role: 'The Interactive Storefront Window',
    why: 'acts like an interactive storefront window with bright, instant buttons. Whenever you touch or click something, it refreshes only that tiny piece on your screen in a split-second without making the whole page reload or flicker'
  },
  fastapi: {
    name: 'FastAPI',
    category: 'Framework',
    role: 'The High-Speed Dispatch Hub',
    why: 'works like a super-fast postal dispatch center with organized express mailboxes. When an order or message arrives, it inspects the package instantly to ensure everything is correct, stamps it approved, and rushes it directly to where it needs to go without delay'
  },
  nextjs: {
    name: 'Next.js',
    category: 'Framework',
    role: 'The Complete Publishing House',
    why: 'pre-prints beautiful pages ahead of time so they appear on your screen the exact millisecond you tap a link, giving visitors an effortless, instantaneous reading experience'
  },
  'next.js': {
    name: 'Next.js',
    category: 'Framework',
    role: 'The Complete Publishing House',
    why: 'pre-prints beautiful pages ahead of time so they appear on your screen the exact millisecond you tap a link, giving visitors an effortless, instantaneous reading experience'
  },
  express: {
    name: 'Express.js',
    category: 'Framework',
    role: 'The Nimble City Courier',
    why: 'acts as a swift, lightweight messenger that routes digital letters through city streets, directing each package to the right desk without taking up unnecessary space'
  },
  django: {
    name: 'Django',
    category: 'Framework',
    role: 'The All-In-One Grand Manor',
    why: 'provides a fully furnished mansion with built-in security guards, an organized library, and administrative desks ready to handle large, complex operations securely'
  },
  flask: {
    name: 'Flask',
    category: 'Framework',
    role: 'The Handy Pocket Toolkit',
    why: 'offers a clean, flexible set of essential tools that lets creators craft custom solutions without carrying unnecessary weight'
  },
  vue: {
    name: 'Vue.js',
    category: 'Framework',
    role: 'The Friendly Guidebook',
    why: 'provides clean, approachable building blocks that make screens pleasant to design and wonderful to look at'
  },
  tailwind: {
    name: 'TailwindCSS',
    category: 'Frontend',
    role: 'The Master Styling Palette',
    why: "works like an artist's precision styling kit, ensuring every button, card, font size, and color looks polished, elegant, and comfortable to read on small phone screens and big monitors alike"
  },
  tailwindcss: {
    name: 'TailwindCSS',
    category: 'Frontend',
    role: 'The Master Styling Palette',
    why: "works like an artist's precision styling kit, ensuring every button, card, font size, and color looks polished, elegant, and comfortable to read on small phone screens and big monitors alike"
  },
  html: {
    name: 'HTML5',
    category: 'Frontend',
    role: 'The Architectural Frame',
    why: 'builds the solid walls, rooms, doors, and signposts of the application, ensuring every headline, button, and paragraph is standing in its rightful place'
  },
  css: {
    name: 'CSS3',
    category: 'Frontend',
    role: 'The Interior Designer',
    why: 'paints the walls, chooses harmonious lighting, softens sharp corners, and adds gentle hover transitions that make using the tool a visual pleasure'
  },
  postgresql: {
    name: 'PostgreSQL',
    category: 'Database',
    role: 'The Heavy-Duty Bank Vault',
    why: 'acts like a massive steel bank vault with thousands of labeled deposit boxes. Every piece of information placed inside is permanently protected, locked tight, and can be retrieved in a millisecond whenever asked for'
  },
  postgres: {
    name: 'PostgreSQL',
    category: 'Database',
    role: 'The Heavy-Duty Bank Vault',
    why: 'acts like a massive steel bank vault with thousands of labeled deposit boxes. Every piece of information placed inside is permanently protected, locked tight, and can be retrieved in a millisecond whenever asked for'
  },
  sqlite: {
    name: 'SQLite',
    category: 'Database',
    role: 'The Fireproof Desk Drawer Safe',
    why: 'operates as a self-contained, lockable strongbox that sits right on your desk, keeping all your records safe and tidy without needing a whole team of caretakers to run it'
  },
  mongodb: {
    name: 'MongoDB',
    category: 'Database',
    role: 'The Flexible Folder Archive',
    why: 'stores records inside neat digital folders that can easily expand, stretch, or adapt whenever you need to tuck in new details or notes'
  },
  redis: {
    name: 'Redis',
    category: 'Database',
    role: 'The Quick-Access Memory Desk',
    why: 'acts like a handy notepad placed right at the front desk for questions people ask all day long, delivering answers in a millisecond without needing to unlock the big storage room every time'
  },
  docker: {
    name: 'Docker',
    category: 'Cloud/Deployment',
    role: 'The Sturdy Shipping Container',
    why: 'packs the entire software along with everything it needs inside a sturdy, sealed shipping crate so it runs identically on any computer in the world without missing parts'
  },
  render: {
    name: 'Render',
    category: 'Cloud/Deployment',
    role: 'The Automated Cloud Workshop',
    why: 'keeps the application running continuously on the internet, automatically updating whenever new work is finished'
  },
  vercel: {
    name: 'Vercel',
    category: 'Cloud/Deployment',
    role: 'The Global Lightning Relay',
    why: 'distributes visual pages to speedy delivery outposts stationed across the entire globe, so visitors see pages load instantly no matter where they live'
  },
  railway: {
    name: 'Railway',
    category: 'Cloud/Deployment',
    role: 'The Rapid Infrastructure Track',
    why: 'lays down fast, isolated tracks in the cloud so services can start up and communicate without roadblocks'
  },
  pytorch: {
    name: 'PyTorch',
    category: 'Data/AI',
    role: 'The Pattern Learning Laboratory',
    why: 'learns from thousands of examples to recognize subtle patterns in pictures, text, or numbers, just like an apprentice practicing a craft until they master it'
  },
  tensorflow: {
    name: 'TensorFlow',
    category: 'Data/AI',
    role: 'The Industrial Machine Learning Factory',
    why: 'trains intelligent models and prepares them to run reliably on phones, laptops, and large data centers'
  },
  openai: {
    name: 'OpenAI API',
    category: 'Data/AI',
    role: 'The Observant Intelligent Assistant',
    why: 'acts like a wise assistant with an encyclopedic memory who reads text, spots helpful connections, and answers complex questions in everyday language'
  },
  gemini: {
    name: 'Google Gemini',
    category: 'Data/AI',
    role: 'The Multi-Talented Intelligent Partner',
    why: 'understands text, pictures, spoken words, and code simultaneously, providing lightning-fast reasoning and helpful suggestions'
  },
  vite: {
    name: 'Vite',
    category: 'Frontend',
    role: 'The Instant Workshop Motor',
    why: 'powers up the workspace in a fraction of a second, reflecting changes the very instant they are typed without waiting around'
  }
};

const CATEGORY_FALLBACK_ROLES: Record<string, string> = {
  Frontend: 'The User-Friendly Display Window',
  Backend: 'The Central Thinking Engine',
  Framework: 'The Organized Building Blueprint',
  Database: 'The Permanent Record Vault',
  'Programming Language': 'The Clear Instruction Set',
  'Cloud/Deployment': 'The 24/7 Global Host',
  DevOps: 'The Automation & Protection Station',
  'Data/AI': 'The Smart Pattern Assistant',
  Testing: 'The Quality Assurance Inspector',
  Other: 'The Specialized Helper Tool'
};

export const cleanProjectTitle = (rawName: string): string => {
  if (!rawName) return 'Untitled Project';
  const words = rawName.split(/[-_]+/);
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

export const parseGithubInput = (input: string): { owner: string; repo?: string } => {
  let clean = input.trim();
  if (!clean) {
    throw new Error('Please enter a valid GitHub username or repository link.');
  }

  // Strip leading @
  if (clean.startsWith('@')) {
    clean = clean.slice(1).trim();
  }

  // Strip query parameters (?...) and hash fragments (#...)
  clean = clean.split('?')[0].split('#')[0].trim();

  // Strip domain prefix and trailing slashes
  clean = clean.replace(/^(https?:\/\/)?(www\.)?github\.com\//i, '').replace(/\/+$/, '');
  const parts = clean.split('/').filter(Boolean);
  if (parts.length === 0) {
    throw new Error('Please enter a valid GitHub username or repository link.');
  }

  const owner = parts[0].replace(/[^a-zA-Z0-9\-_]/g, '');
  if (!owner) {
    throw new Error('Invalid GitHub username format. Please use a valid GitHub handle.');
  }

  const NON_REPO_SLUGS = new Set([
    'repositories', 'projects', 'packages', 'stars', 'followers',
    'following', 'tab', 'orgs', 'overview'
  ]);

  let repo: string | undefined = undefined;
  if (parts.length > 1) {
    let candidate = parts[1].replace(/\.git$/i, '');
    if (!NON_REPO_SLUGS.has(candidate.toLowerCase())) {
      repo = candidate;
    }
  }

  return { owner, repo };
};

export const synthesizeAiDossier = (
  name: string,
  rawDesc: string,
  language: string | null,
  topics: string[],
  techs: ExtractedTechnology[],
  links: ExtractedProjectLink[],
  stars: number
): { shortDesc: string; fullDossier: string } => {
  const cleanDesc = (rawDesc || '').trim();
  const techNames = techs.map((t) => t.name);
  const primaryLang = language || techNames[0] || 'Modern Software';

  // 1. Short Description (Crisp, approachable preview)
  const shortDesc = cleanDesc
    ? `${cleanDesc.replace(/\.$/, '')}. Built with ${techNames.slice(0, 3).join(', ') || primaryLang} to keep everyday workflows fast, organized, and reliable.`
    : `An intuitive, dependable solution built with ${techNames.slice(0, 3).join(', ') || primaryLang} that turns complicated tasks into smooth, effortless steps.`;

  // 2. Section 1: Purpose & Big Picture
  const painPoint = cleanDesc
    ? `Before **${name}** was created, people dealing with this task had to manage slow, repetitive, and often confusing manual work around ${cleanDesc.toLowerCase().replace(/\.$/, '')}. Without an organized tool, essential details easily get scattered across messy notes, lost in buried folders, or forgotten in endless email threads. A single innocent mistake could mean starting all over again from scratch, causing wasted hours and unnecessary stress.`
    : `Before **${name}** was created, accomplishing this work required juggling multiple disjointed steps, manual checklists, and constant double-checking. Important information was vulnerable to misplacement, and even small oversights could lead to delays or lost progress.`;

  const solution = cleanDesc
    ? `**${name}** steps in as a calm, dependable digital helper. It brings all the necessary controls and information into one clean, welcoming space. Instead of memorizing complicated rules or worrying about making an error, users can simply open this tool, follow clear cues, and finish what they set out to do with total peace of mind. It takes care of the tricky behind-the-scenes checks automatically so you never have to second-guess yourself.`
    : `**${name}** was engineered to turn that complex workflow into a straightforward, predictable, and delightful experience. It organizes every moving part into intuitive steps, handling all the heavy thinking and verification in the background so users achieve dependable results every single time.`;

  // 3. Section 2: Real-World Analogy
  const analogyText = `To understand exactly how **${name}** works, imagine a welcoming neighborhood bakery or master artisan workshop:

- **The Front Display Counter (What You See & Touch)**: Bright, clean display shelves showing everything clearly. You simply point at what you want or hand over a note. It responds immediately with a smile.
- **The Friendly Attendant (The Quick Messenger)**: Takes your order ticket, double-checks that nothing was missed, and carries it briskly into the kitchen.
- **The Master Kitchen & Chef (The Thinking Engine)**: Follows the recipe with absolute precision, mixes the ingredients, cooks everything to perfection, and ensures every rule is honored.
- **The Fireproof Pantry & Safe (The Permanent Storage Vault)**: Every single recipe, order history, and ingredient count is neatly placed inside labeled, locked drawers so nothing is ever spoiled, lost, or forgotten.`;

  // 4. Section 3: Tech Stack Breakdown
  const techLines = techs.length > 0
    ? techs.map((t) => {
        const match = TECH_KNOWLEDGE[t.name.toLowerCase()];
        const role = match?.role || CATEGORY_FALLBACK_ROLES[t.category || 'Other'] || 'The Specialized Helper Tool';
        const why = match ? match.why : `provides specialized capabilities to keep the application running smoothly, safely, and efficiently`;
        return `- **${t.name}** (*${role}*): ${why}.`;
      }).join('\n')
    : `- **${primaryLang}** (*The Clear Instruction Set*): provides the clear set of instructions that tells the computer exactly what to do step by step.`;

  // 5. Section 4: Architecture
  const frontendTechs = techs.filter((t) => t.category === 'Frontend' || ['React', 'Vue.js', 'Angular', 'Svelte', 'Next.js', 'HTML5', 'CSS3', 'TailwindCSS'].includes(t.name)).map((t) => t.name);
  const backendTechs = techs.filter((t) => (['Backend', 'Framework'].includes(t.category || '') && !['React', 'Vue.js', 'Angular', 'Svelte', 'TailwindCSS', 'Bootstrap'].includes(t.name)) || ['FastAPI', 'Express.js', 'Django', 'Flask', 'Spring Boot', 'NestJS', 'Go', 'Rust', 'Node.js'].includes(t.name)).map((t) => t.name);
  const dbTechs = techs.filter((t) => t.category === 'Database' || ['PostgreSQL', 'SQLite', 'MongoDB', 'Redis', 'MySQL', 'Prisma', 'SQLAlchemy', 'Supabase', 'Firebase'].includes(t.name)).map((t) => t.name);
  const aiTechs = techs.filter((t) => t.category === 'Data/AI').map((t) => t.name);
  const cloudTechs = techs.filter((t) => ['Cloud/Deployment', 'DevOps'].includes(t.category || '')).map((t) => t.name);

  const archSteps: string[] = [];
  if (frontendTechs.length > 0) {
    archSteps.push(`1. **User Interface (Frontend)**: Styled and guided by ${frontendTechs.slice(0, 3).join(', ')}. Think of this as the welcoming storefront counter. It presents clean screens, helpful buttons, and clear text that anyone can navigate comfortably.`);
  } else {
    archSteps.push(`1. **Input & Entry Points**: Structured with clear, friendly entry points and straightforward prompts that guide users naturally.`);
  }

  if (backendTechs.length > 0) {
    archSteps.push(`2. **Processing Core (Backend)**: Powered by ${backendTechs.slice(0, 3).join(', ')}. Think of this as the bustling kitchen behind the counter. It takes in requests, double-checks the rules, calculates the answers, and prepares everything safely and securely.`);
  } else if (['JavaScript', 'TypeScript', 'HTML5', 'CSS3'].includes(primaryLang)) {
    archSteps.push(`2. **Processing Core (Client-Side Logic)**: Driven directly by ${primaryLang}. The application does all of its thinking directly inside your web browser, which means it works with lightning speed without waiting for a distant server across the country.`);
  } else {
    archSteps.push(`2. **Processing Core (Application Engine)**: Driven by ${primaryLang} to follow step-by-step instructions with deterministic, predictable accuracy.`);
  }

  if (dbTechs.length > 0) {
    archSteps.push(`3. **Data Layer & Storage (Database)**: Safeguarded by ${dbTechs.slice(0, 3).join(', ')}. Think of this as the permanent, locked storage room where every single record is filed away neatly so nothing is ever misplaced, forgotten, or overwritten by mistake.`);
  }

  if (aiTechs.length > 0) {
    archSteps.push(`4. **Intelligent Assistance (Data & AI)**: Assisted by ${aiTechs.slice(0, 2).join(', ')}. Think of this as a smart assistant with a sharp memory who analyzes information, recognizes helpful patterns, and automates repetitive tasks to save you time.`);
  }

  if (cloudTechs.length > 0) {
    archSteps.push(`5. **Hosting & Continuous Care (Cloud & Delivery)**: Managed by ${cloudTechs.slice(0, 2).join(', ')}. Think of this as the dependable utility grid that keeps the building lighted, powered, and open 24/7 so anyone around the world can visit at any moment.`);
  }

  const architecture = `**${name}** divides its responsibilities into clear, specialized stations so that no single part gets overloaded:\n\n` + archSteps.join('\n\n');

  // 6. Section 5: Walkthrough
  const walkthroughSteps = [
    '1. **Step 1: The Gentle Touch (Starting the Action)**: You click a button, tap a card, or submit information on your screen.',
    '2. **Step 2: The Polite Check at the Door (Instant Validation)**: Before anything travels anywhere, the system double-checks what you entered to ensure nothing was left blank, misspelled, or typed in an unusual way.',
    '3. **Step 3: The Sealed Envelope on the Road (Safe Travel)**: A secure digital messenger takes your request, places it into a protected envelope, and carries it smoothly across the wire to the processing center.',
    '4. **Step 4: The Security Gate & Welcome (Verification)**: The processing center verifies the seal on the envelope to confirm it is authentic and safe to open.',
    '5. **Step 5: The Thinking Brain (Doing the Work)**: The system follows its clear recipes, carries out the calculations, and prepares the exact result you requested.',
    '6. **Step 6: The Locked Safe (Permanent Storage)**: Any new or modified records are neatly placed inside the permanent filing cabinet with a confirmed stamp, making sure your work is safe even if power goes out.',
    '7. **Step 7: The Happy Delivery (Instant Feedback)**: The messenger races back to your screen and instantly displays the update or a cheerful green confirmation badge without any confusing delay.'
  ].join('\n\n');

  // 7. Section 6: Capabilities
  const caps = [
    'Massive Time Saver: Accomplishes in two seconds what used to take thirty minutes of manual hunting and typing',
    'Zero Lost Work: Automatically protects every entry into a permanent vault so nothing is ever lost or erased by mistake',
    'Comfortable on Any Screen: Adjusts its shape naturally whether you use it on a pocket phone, tablet, or large desk monitor',
    'Clean & Organized Layout: Keeps all information arranged on tidy, labeled shelves so you never have to search blindly',
    'Mistake-Proof Guardrails: Gently guides you if you leave something blank or type something incorrectly, stopping mistakes before they happen',
    'Instant Responsiveness: Operates with smooth, instant feedback so you never have to sit staring at a frozen screen or spinning wheel',
    'Private & Secure: Protects important settings behind verified locks so only authorized caretakers can make permanent updates'
  ];
  if (topics && topics.length > 0) {
    caps.unshift(`Specialized Purpose: Tailored specifically for modern workflows including ${topics.slice(0, 4).join(', ')}`);
  }
  if (stars > 0) {
    caps.push(`Community Trusted: Celebrated by ${stars} person${stars === 1 ? '' : 's'} who bookmarked and recommended this project`);
  }
  const capLines = caps.map((c) => `- ✨ **${c}**`).join('\n');

  // 8. Section 7: Safety & Reliability
  const reliabilitySection = [
    '- **Digital Seatbelts & Input Guardrails**: Every piece of information entered is checked against strict rules before being processed. Unexpected clicks or accidental typos bounce off harmlessly without causing glitches or crashes.',
    '- **Fireproof Locked Drawers**: Data is written using confirmed save operations. If a phone battery dies or the internet blinks during a save, incomplete records are rolled back cleanly, leaving your data in a perfect, uncorrupted state.',
    '- **Polite & Clear Guidance**: When something outside the system\'s control goes wrong (such as an offline network), the system provides a calm, clear message in plain words explaining what happened and how to proceed.',
    '- **Strict Key Access**: Critical controls and administrative settings are protected behind verified security locks, ensuring that only authorized caretakers can make permanent updates.'
  ].join('\n');

  // 9. Section 8: Future Improvements
  const futureLines = [
    '- 🚀 **One-Touch Pocket Mobile Apps**: Creating downloadable phone apps with offline-ready support so people can access their work even without an internet signal.',
    '- 🚀 **Helpful Reminders & Smart Alerts**: Adding friendly, gentle notifications that remind users of important upcoming milestones.',
    '- 🚀 **Natural Voice Interaction**: Allowing users to speak their requests out loud in everyday language.',
    '- 🚀 **Worldwide Language Translation**: Bringing instant language switching so people around the world can comfortably use it in their mother tongue.',
    '- 🚀 **Automated Safety & Quality Tracks**: Adding continuous background health monitors that inspect every line of code around the clock to ensure top-tier stability.'
  ].join('\n');

  // 10. Section 9: Links
  const linkLines = links.length > 0
    ? links.map((l) => {
        const badge = l.link_type === 'GitHub' ? ' *(Mandatory Source Repository)*' : ' *(Optional Live Deployment)*';
        return `- [${l.label}](${l.url})${badge}`;
      }).join('\n')
    : '- No links currently registered.';

  const fullDossier = `# ${name}

> **Quick Summary**: ${shortDesc}

---

## 🎯 1. Purpose of the Project & The Big Picture

### The Real-World Frustration Before This Existed
${painPoint}

### How This Project Fixes It Once and for All
${solution}

### Who Benefits & Why It Matters
This project is built for everyday people who want their day-to-day work to feel calm, straightforward, and dependable. By bringing clarity, speed, and automatic safety checks to the table, it frees people up to focus on what actually matters without getting bogged down by technical headaches.

---

## 🏠 Real-World Analogy: How to Picture It in Daily Life
${analogyText}

---

## 🛠️ 2. What I Used & Why I Used It
Here is a breakdown of every building block used to build this project, explained in everyday words:

${techLines}

---

## 🏗️ 3. Architecture & How It Works (In Super Simple Words)
${architecture}

---

## 🚶 Step-by-Step Walkthrough: What Happens Behind the Scenes When You Touch a Button
When you interact with **${name}**, here is the exact 7-step journey that takes place behind the scenes:

${walkthroughSteps}

---

## ✨ 4. What This Project Can Do
Here are the practical everyday superpowers that make this project uniquely helpful:

${capLines}

---

## 🛡️ Behind the Scenes: How It Stays Strong, Safe & Reliable
${reliabilitySection}

---

## 🚀 5. How It Can Be Improved in the Future
Here are exciting ways this project can expand and become even more capable over time:

${futureLines}

---

## 🔗 6. Project Links
${linkLines}
`;

  return { shortDesc, fullDossier: fullDossier.trim() };
};

export const downloadProjectDossier = (project: ExtractedProject | Project): void => {
  const content = (project as ExtractedProject).full_ai_dossier || project.description || `# ${project.name}\n\n${project.short_description || ''}`;
  const safeFilename = `${project.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'project'}-ai-dossier.md`;

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = safeFilename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

export const downloadAllDossiers = (projects: (ExtractedProject | Project)[]): void => {
  if (projects.length === 0) return;

  const header = `# Existence Portfolio – Extracted Projects AI Dossiers
Generated on: ${new Date().toLocaleDateString()}
Total Projects: ${projects.length}

---

## Table of Contents
${projects.map((p, idx) => `${idx + 1}. [${p.name}](#${p.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')})`).join('\n')}

---

`;

  const bodies = projects.map((p) => {
    return (p as ExtractedProject).full_ai_dossier || p.description || `# ${p.name}\n\n${p.short_description || ''}`;
  }).join('\n\n---\n\n');

  const fullContent = header + bodies;
  const blob = new Blob([fullContent], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `existence-portfolio-projects-dossier-bundle.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch (err) {
    // fallback
  }

  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);
    return successful;
  } catch (err) {
    return false;
  }
};

export const extractGithubClientSide = async (
  inputUrl: string,
  token?: string
): Promise<GitHubExtractionResponse> => {
  const { owner, repo } = parseGithubInput(inputUrl);

  const headers: Record<string, string> = {
    Accept: 'application/vnd.github.v3+json'
  };
  if (token && token.trim()) {
    headers.Authorization = `token ${token.trim()}`;
  }

  let rawRepos: any[] = [];
  let sourceType: 'user' | 'repo' = 'user';

  if (repo) {
    sourceType = 'repo';
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}`, { headers });
    if (!res.ok) {
      if (res.status === 404) throw new Error(`Repository ${owner}/${repo} was not found on GitHub.`);
      if (res.status === 403) throw new Error('GitHub API rate limit reached. Please provide a Personal Access Token or wait a short while.');
      throw new Error(`GitHub API error: ${res.statusText}`);
    }
    const data = await res.json();
    rawRepos = [data];
  } else {
    sourceType = 'user';
    const res = await fetch(`https://api.github.com/users/${owner}/repos?sort=updated&per_page=100`, { headers });
    if (!res.ok) {
      if (res.status === 404) throw new Error(`GitHub user '${owner}' was not found.`);
      if (res.status === 403) throw new Error('GitHub API rate limit reached. Please provide a Personal Access Token or wait a short while.');
      throw new Error(`GitHub API error: ${res.statusText}`);
    }
    const data = await res.json();
    if (Array.isArray(data)) {
      const nonForks = data.filter((r) => !r.fork);
      rawRepos = nonForks.length > 0 ? nonForks : data;
    }
  }

  const projects: ExtractedProject[] = rawRepos.map((r) => {
    const cleanName = cleanProjectTitle(r.name);
    const primaryLang = r.language || null;
    const topics: string[] = Array.isArray(r.topics) ? r.topics : [];
    const stars = r.stargazers_count || 0;
    const forks = r.forks_count || 0;
    const isArchived = Boolean(r.archived);

    // Build techs
    const techMap = new Map<string, ExtractedTechnology>();
    if (primaryLang) {
      const norm = primaryLang.toLowerCase();
      const meta = TECH_KNOWLEDGE[norm];
      techMap.set(norm, {
        name: meta ? meta.name : primaryLang,
        category: meta ? meta.category : 'Programming Language'
      });
    }

    topics.forEach((top) => {
      const norm = top.toLowerCase();
      if (!techMap.has(norm)) {
        const meta = TECH_KNOWLEDGE[norm];
        techMap.set(norm, {
          name: meta ? meta.name : top.charAt(0).toUpperCase() + top.slice(1),
          category: meta ? meta.category : 'Other'
        });
      }
    });

    const technologies = Array.from(techMap.values());

    // Build links (Mandatory GitHub + Optional Deployments)
    const links: ExtractedProjectLink[] = [];
    if (r.html_url) {
      links.push({
        label: 'GitHub Repository',
        url: r.html_url,
        link_type: 'GitHub',
        is_primary: true,
        is_visible: true,
        display_order: 0
      });
    }

    if (r.homepage && typeof r.homepage === 'string' && r.homepage.trim().startsWith('http')) {
      const hp = r.homepage.trim();
      const lowered = hp.toLowerCase();
      let label = 'Live Demo';
      let lType: ProjectLinkType = 'Live Demo';

      if (lowered.includes('onrender.com')) {
        label = 'Render Live Deployment';
        lType = 'Deployment';
      } else if (lowered.includes('vercel.app')) {
        label = 'Vercel Live Deployment';
        lType = 'Deployment';
      } else if (lowered.includes('railway.app')) {
        label = 'Railway Live Deployment';
        lType = 'Deployment';
      } else if (lowered.includes('github.io')) {
        label = 'GitHub Pages Demo';
        lType = 'Live Demo';
      }

      links.push({
        label,
        url: hp,
        link_type: lType,
        is_primary: false,
        is_visible: true,
        display_order: 1
      });
    }

    // Set first deployment link as primary if available
    if (links.length > 1) {
      links[0].is_primary = false;
      links[1].is_primary = true;
    }

    const { shortDesc, fullDossier } = synthesizeAiDossier(
      cleanName,
      r.description || '',
      primaryLang,
      topics,
      technologies,
      links,
      stars
    );

    return {
      name: cleanName,
      short_description: shortDesc,
      description: fullDossier,
      full_ai_dossier: fullDossier,
      status: isArchived ? 'Archived' : 'Completed',
      technologies,
      links,
      stars,
      forks,
      repo_url: r.html_url || '',
      homepage_url: r.homepage || null,
      is_featured: stars >= 5 || links.length > 1
    };
  });

  return {
    username: owner,
    source_type: sourceType,
    projects_count: projects.length,
    projects
  };
};
