# Existence Frontend — Public Portfolio & Custom Admin CMS

The public-facing portfolio and administrative content management interface for the **Existence** personal-identity and personality-intelligence platform.

---

## 1. Technology Stack

* **Framework**: React 19 (TypeScript)
* **Build Tool**: Vite 8.3 (ESM, Hot Module Replacement)
* **Styling**: Tailwind CSS v4 + Vanilla CSS Design System with dark glassmorphism utilities (`glass-panel`, `glass-card`, `glow-indigo`, `glow-emerald`, `glow-amber`)
* **Icons**: Lucide React
* **Router**: Browser History API synchronized routing (`/`, `/about`, `/education`, `/experience`, `/skills`, `/personality`, `/interests`, `/contact`, `/admin`)
* **Testing**: Node.js 22 built-in test runner (`node --test`)
* **Deployment**: Vercel SPA (with pre-configured `vercel.json` rewrites)

---

## 2. Directory Architecture

```text
frontend/
├── src/
│   ├── App.tsx                     # Top-level public router & data hydration coordinator
│   ├── main.tsx                    # React DOM root entry
│   ├── index.css                   # Tailwind v4 import & glassmorphism custom styles
│   ├── context/
│   │   └── AuthContext.tsx         # JWT token & PIN verification session state
│   ├── types/
│   │   └── index.ts                # TypeScript domain interfaces (Profile, Education, Skills, etc.)
│   ├── services/
│   │   └── api.ts                  # Centralized REST API client for public & admin endpoints
│   └── components/
│       ├── common/
│       │   ├── PublicNavbar.tsx     # Accessible desktop & mobile drawer navigation
│       │   ├── PublicFooter.tsx     # Professional footer with verified stack indicators
│       │   ├── GlobalLoadingState.tsx # Smooth skeleton loader during initial fetch
│       │   ├── GlobalErrorState.tsx # Reusable error banner with functional retry button
│       │   ├── EmptyState.tsx       # Standardized empty state presentation
│       │   └── LoginModal.tsx       # Admin authentication dialog
│       ├── profile/
│       │   ├── HeroSection.tsx      # Landing identity hero with verified metrics strip
│       │   └── AboutView.tsx        # Dedicated executive narrative & paragraph layout
│       ├── education/
│       │   └── EducationView.tsx    # Academic lineage timeline with currently studying badges
│       ├── experience/
│       │   └── ExperienceView.tsx   # Professional trajectory timeline with work mode filters
│       ├── skills/
│       │   ├── SkillsView.tsx       # 7-Level mastery engine with search, category & level filters
│       │   └── SkillRatingBar.tsx   # Segmented visual rating indicator
│       ├── personality/
│       │   └── PersonalityView.tsx  # Empirical assessment scores & synthesized soft skills
│       ├── interests/
│       │   └── InterestsView.tsx    # Segregated Hobbies and Intellectual Interests views
│       ├── contact/
│       │   └── ContactView.tsx      # Direct communication endpoints with click-to-copy
│       └── cms/
│           ├── CmsDashboard.tsx     # Custom Admin Panel with 11 domain management tabs
│           ├── ConfirmDialog.tsx    # Destructive action confirmation modal
│           └── PinVerificationDialog.tsx # PIN action authorization modal
├── tests/
│   └── portfolio.test.mjs          # Automated frontend test suite (routing, mastery, invariants)
├── package.json
├── tsconfig.json
├── vercel.json                     # Vercel SPA rewrite configuration
└── vite.config.ts
```

---

## 3. Public Routes & Deep Linking

The application parses `window.location.pathname` and dynamically renders the appropriate public portfolio section while updating the browser address bar via `window.history.pushState`:

| Path | View Component | Description |
|---|---|---|
| `/` | `HeroSection` | Public identity landing, verified metrics bar, and domain navigation cards |
| `/about` | `AboutView` | Dedicated executive narrative, readable typography, and contact actions |
| `/education` | `EducationView` | Academic credentials, degree levels, and "Present · Currently Enrolled" status |
| `/experience` | `ExperienceView` | Career trajectory, work modes (`On-site`, `Remote`, `Hybrid`), and active badges |
| `/skills` | `SkillsView` | 7-Level mastery engine (`Beginner` to `Master`) with search and category filters |
| `/personality` | `PersonalityView` | MBTI, DISC, Big Five trait scores, Key Soft Skills, and Growth Blindspots |
| `/interests` | `InterestsView` | Visual segregation of Personal Hobbies and Intellectual Pursuits |
| `/contact` | `ContactView` | Verified direct email addresses, phone number, and LinkedIn link |
| `/admin` | `CmsDashboard` | Dedicated administrative CMS portal (protected by JWT + PIN authorization) |

---

## 4. Public / Private Data Isolation

* **Public Portfolio**: Consumes only non-administrative REST endpoints (`/profile`, `/education`, `/experience`, `/skills?include_hidden=false`, `/hobbies`, `/interests`, `/personality/synthesis`).
* **Zero Secret Leakage**: The frontend bundle contains zero passwords, database connection strings, JWT secret keys, or raw PIN hashes.
* **Administrative Isolation**: Content revision snapshots, security audit events, and PIN verification controls are strictly confined to the `/admin` area.

---

## 5. Development & Build Verification

```bash
# 1. Install dependencies
npm install

# 2. Start local Vite development server
npm run dev

# 3. Run automated frontend test suite
npm test

# 4. Check TypeScript types
npm run typecheck

# 5. Build production bundle for Vercel
npm run build
```

---

## 6. Vercel Deployment Configuration

Configured in `frontend/vercel.json`:
```json
{
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Environment Variable for Production:
In Vercel Project Settings > Environment Variables:
* `VITE_API_URL`: Your live Render backend API URL (e.g. `https://existence-backend.onrender.com`).
