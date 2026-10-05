import re
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Canonical taxonomies aligned with Existence Projects Engine (Prompt 08)
VALID_STATUSES = ["Planned", "In Progress", "Completed", "Archived"]

VALID_LINK_TYPES = [
    "Live Demo",
    "Deployment",
    "GitHub",
    "Repository",
    "Documentation",
    "API",
    "Video Demo",
    "Case Study",
    "Other"
]

VALID_TECH_CATEGORIES = [
    "Programming Language",
    "Framework",
    "Database",
    "Cloud/Deployment",
    "Frontend",
    "Backend",
    "DevOps",
    "Testing",
    "Data/AI",
    "Other"
]

# Mapping of known keywords to canonical technology categories and super-simple everyday explanations
TECH_KNOWLEDGE_BASE = {
    # Languages
    "python": ("Python", "Programming Language", "acts like a brilliant, patient master chef who reads every recipe instruction with absolute precision, handles heavy calculations effortlessly, and follows every instruction reliably without ever skipping a step."),
    "javascript": ("JavaScript", "Programming Language", "brings buttons, menus, and cards to life with fluid movement, making elements expand, slide, and react smoothly the split-second you touch them."),
    "typescript": ("TypeScript", "Programming Language", "acts like a careful proofreader who inspects every single sentence and bolt before anything leaves the workshop floor, catching typos and mistakes early so the software never breaks down unexpectedly."),
    "html": ("HTML5", "Frontend", "builds the solid walls, rooms, doors, and signposts of the application, ensuring every headline, button, and paragraph is standing in its rightful place."),
    "css": ("CSS3", "Frontend", "paints the walls, chooses harmonious lighting, softens sharp corners, and adds gentle hover transitions that make using the tool a visual pleasure."),
    "go": ("Go", "Programming Language", "runs like a fleet of ultra-lightweight delivery scooters that zip through heavy city traffic simultaneously without burning excess fuel."),
    "rust": ("Rust", "Programming Language", "builds machinery with unbreakable titanium locks, guaranteeing that memory and parts are protected from damage while operating at lightning speed."),
    "java": ("Java", "Programming Language", "acts like an established enterprise train system with standardized tracks, running dependably across every kind of computer environment."),
    "c++": ("C++", "Programming Language", "provides direct mechanical control over hardware gears and engines, executing instructions with raw, high-speed power."),
    "c#": ("C#", "Programming Language", "delivers modern tools and organized building blocks for crafting dependable business and interactive software."),
    "php": ("PHP", "Programming Language", "acts like a dependable printing press that quickly stamps out web pages on demand as visitors request them."),
    "ruby": ("Ruby", "Programming Language", "designed to read almost like natural English poetry, keeping the building process joyful and expressive."),
    "sql": ("SQL", "Database", "acts as the precise universal language used to ask the filing cabinet to store, organize, or fetch specific records in a fraction of a second."),

    # Frameworks & Libraries
    "react": ("React", "Framework", "acts like an interactive storefront window with bright, instant buttons. Whenever you touch or click something, it refreshes only that tiny piece on your screen in a split-second without making the whole page reload or flicker."),
    "fastapi": ("FastAPI", "Framework", "works like a super-fast postal dispatch center with organized express mailboxes. When an order or message arrives, it inspects the package instantly to ensure everything is correct, stamps it approved, and rushes it directly to where it needs to go without delay."),
    "next.js": ("Next.js", "Framework", "pre-prints beautiful pages ahead of time so they appear on your screen the exact millisecond you tap a link, giving visitors an effortless, instantaneous reading experience."),
    "nextjs": ("Next.js", "Framework", "pre-prints beautiful pages ahead of time so they appear on your screen the exact millisecond you tap a link, giving visitors an effortless, instantaneous reading experience."),
    "express": ("Express.js", "Framework", "acts as a swift, lightweight messenger that routes digital letters through city streets, directing each package to the right desk without taking up unnecessary space."),
    "flask": ("Flask", "Framework", "offers a clean, flexible set of essential tools that lets creators craft custom solutions without carrying unnecessary weight."),
    "django": ("Django", "Framework", "provides a fully furnished mansion with built-in security guards, an organized library, and administrative desks ready to handle large, complex operations securely."),
    "vue": ("Vue.js", "Framework", "provides clean, approachable building blocks that make screens pleasant to design and wonderful to look at."),
    "angular": ("Angular", "Framework", "applies disciplined blueprints and strict organizational systems to keep very large, multi-team projects orderly and dependable."),
    "svelte": ("Svelte", "Framework", "pre-assembles every part of the screen ahead of time, leaving zero excess machinery behind so the application runs with feather-light swiftness."),
    "tailwind": ("TailwindCSS", "Frontend", "works like an artist's precision styling kit, ensuring every button, card, font size, and color looks polished, elegant, and comfortable to read on small phone screens and big monitors alike."),
    "tailwindcss": ("TailwindCSS", "Frontend", "works like an artist's precision styling kit, ensuring every button, card, font size, and color looks polished, elegant, and comfortable to read on small phone screens and big monitors alike."),
    "bootstrap": ("Bootstrap", "Frontend", "provides a pre-assembled box of sturdy furniture—like ready-made buttons, menus, and layout grids—that fit comfortably into any room."),
    "spring": ("Spring Boot", "Framework", "prepares production-ready Java services with organized compartments and automated setup."),
    "nestjs": ("NestJS", "Framework", "organizes server operations into tidy, modular departments using clear architectural blueprints."),
    
    # Databases
    "postgresql": ("PostgreSQL", "Database", "acts like a massive steel bank vault with thousands of labeled deposit boxes. Every piece of information placed inside is permanently protected, locked tight, and can be retrieved in a millisecond whenever asked for."),
    "postgres": ("PostgreSQL", "Database", "acts like a massive steel bank vault with thousands of labeled deposit boxes. Every piece of information placed inside is permanently protected, locked tight, and can be retrieved in a millisecond whenever asked for."),
    "sqlite": ("SQLite", "Database", "operates as a self-contained, lockable strongbox that sits right on your desk, keeping all your records safe and tidy without needing a whole team of caretakers to run it."),
    "mongodb": ("MongoDB", "Database", "stores records inside neat digital folders that can easily expand, stretch, or adapt whenever you need to tuck in new details or notes."),
    "redis": ("Redis", "Database", "acts like a handy notepad placed right at the front desk for questions people ask all day long, delivering answers in a millisecond without needing to unlock the big storage room every time."),
    "mysql": ("MySQL", "Database", "maintains clean, dependable ledgers of official records, ensuring everything is recorded in orderly columns and rows."),
    "supabase": ("Supabase", "Database", "combines a heavy-duty vault with instant messengers and security guards ready to work on the cloud with zero hassle."),
    "firebase": ("Firebase", "Database", "keeps information instantly synchronized across thousands of screens at once, like a magical chalkboard where writing in one room appears on all walls simultaneously."),
    "prisma": ("Prisma", "Database", "acts as a courteous filing clerk who ensures every request for records is clearly labeled and checked for accuracy before opening the filing cabinets."),
    "sqlalchemy": ("SQLAlchemy", "Database", "translates everyday instructions into the exact filing system language that the vault understands, ensuring records are stored and retrieved without confusion."),

    # Cloud & Deployment
    "docker": ("Docker", "Cloud/Deployment", "packs the entire software along with everything it needs inside a sturdy, sealed shipping crate so it runs identically on any computer in the world without missing parts."),
    "kubernetes": ("Kubernetes", "Cloud/Deployment", "coordinates a fleet of shipping containers, automatically calling in backup when things get busy and replacing any container that needs maintenance."),
    "render": ("Render", "Cloud/Deployment", "keeps the application running continuously on the internet, automatically updating whenever new work is finished."),
    "vercel": ("Vercel", "Cloud/Deployment", "distributes visual pages to speedy delivery outposts stationed across the entire globe, so visitors see pages load instantly no matter where they live."),
    "railway": ("Railway", "Cloud/Deployment", "lays down fast, isolated tracks in the cloud so services can start up and communicate without roadblocks."),
    "aws": ("AWS", "Cloud/Deployment", "provides a vast global power grid and computer facility capable of scaling from a small room to a bustling city."),
    "netlify": ("Netlify", "Cloud/Deployment", "serves as an automated cloud launcher that publishes web pages to the world the moment changes are saved."),
    "git": ("Git", "DevOps", "keeps an accurate historical snapshot of every sentence and file ever written, allowing anyone to travel backward in time or undo any mistake with absolute safety."),
    "github": ("GitHub", "DevOps", "provides a welcoming online studio where creators store their code, discuss improvements, and share their inventions with the world."),
    "github actions": ("GitHub Actions", "DevOps", "runs automatic safety and quality tests every time an update is proposed, making sure no broken parts ever slip into the final product."),

    # Data / AI
    "pytorch": ("PyTorch", "Data/AI", "learns from thousands of examples to recognize subtle patterns in pictures, text, or numbers, just like an apprentice practicing a craft until they master it."),
    "tensorflow": ("TensorFlow", "Data/AI", "trains intelligent models and prepares them to run reliably on phones, laptops, and large data centers."),
    "scikit-learn": ("Scikit-Learn", "Data/AI", "supplies clean, classic recipes for sorting data, predicting trends, and grouping similar items together."),
    "pandas": ("Pandas", "Data/AI", "transforms massive stacks of scattered numbers and text into tidy, filterable tables that are effortless to read and analyze."),
    "numpy": ("NumPy", "Data/AI", "solves millions of numerical calculations in the blink of an eye, handling heavy math transformations with ease."),
    "langchain": ("LangChain", "Data/AI", "connects intelligent language assistants to external notes, documents, and tools so they can answer questions with factual context."),
    "openai": ("OpenAI API", "Data/AI", "acts like a wise assistant with an encyclopedic memory who reads text, spots helpful connections, and answers complex questions in everyday language."),
    "gemini": ("Google Gemini", "Data/AI", "understands text, pictures, spoken words, and code simultaneously, providing lightning-fast reasoning and helpful suggestions."),
    "huggingface": ("Hugging Face", "Data/AI", "serves as a giant public library filled with pre-trained smart models ready to help with reading, seeing, and listening."),
    "chromadb": ("ChromaDB", "Data/AI", "stores thoughts and concepts as coordinate points on a map so the assistant can locate relevant facts by their meaning rather than just keywords."),
    "pinecone": ("Pinecone", "Data/AI", "operates as a high-speed search station that pinpoints matching concepts across billions of records in a few milliseconds."),
    "streamlit": ("Streamlit", "Frontend", "turns notes and data recipes into interactive web pages in minutes without needing complex design work."),

    # Additional Languages & Platforms
    "swift": ("Swift", "Programming Language", "delivers fast, safe, and pleasant software specifically designed for Apple devices like iPhones and Macs."),
    "kotlin": ("Kotlin", "Programming Language", "provides modern, concise, and safe programming tailored for modern Android smartphones and tablets."),
    "dart": ("Dart", "Programming Language", "powers fast client applications that run with silky smoothness on screens of all varieties."),
    "flutter": ("Flutter", "Framework", "draws unified, beautiful screens that work seamlessly on phones, computers, and tablets from a single shared blueprint."),
    "electron": ("Electron", "Framework", "packages web designs into installable desktop applications for Mac, Windows, and Linux."),
    "tauri": ("Tauri", "Framework", "builds ultra-lightweight desktop applications with tiny file sizes and high security."),
    "vite": ("Vite", "Frontend", "powers up the creator's workspace in a fraction of a second, reflecting changes the very instant they are typed without waiting around."),
    "nodejs": ("Node.js", "Backend", "handles thousands of incoming questions and requests simultaneously without ever breaking a sweat or freezing up."),
    "node": ("Node.js", "Backend", "handles thousands of incoming questions and requests simultaneously without ever breaking a sweat or freezing up."),
    "graphql": ("GraphQL", "Backend", "allows visitors to ask for exactly the specific details they need on a single card, preventing unnecessary clutter or extra trips."),
    "nginx": ("Nginx", "DevOps", "serves as a high-speed traffic officer at the building gates, welcoming thousands of visitors and smoothly guiding them to open doorways."),
    "linux": ("Linux", "DevOps", "provides the rock-solid, dependable foundation that keeps computers running quietly and faithfully for years without rebooting."),
    "terraform": ("Terraform", "DevOps", "writes down instructions for an entire digital city on paper so whole infrastructures can be built consistently at the push of a button."),
    "jest": ("Jest", "Testing", "tests screen components and logic rapidly, sounding an alarm if any unexpected change breaks an existing feature."),
    "pytest": ("Pytest", "Testing", "runs hundreds of practice trials automatically, verifying that every button, calculation, and safety check behaves perfectly before anyone uses it."),
    "playwright": ("Playwright", "Testing", "navigates through the website like a real person—clicking buttons, filling forms, and testing links—to ensure the experience is flawless on all devices."),
    "cypress": ("Cypress", "Testing", "verifies that every screen looks and responds properly by running simulated user walkthroughs right inside the web browser.")
}


def parse_github_target(raw_url: str) -> Tuple[str, Optional[str]]:
    """
    Parses a GitHub URL or handle into (owner, repo_name or None).
    Supports:
      - https://github.com/username
      - https://github.com/username?tab=repositories
      - https://github.com/username/repositories
      - https://github.com/username/repository
      - https://github.com/username/repository?tab=readme-ov-file
      - github.com/username/repository
      - username/repository
      - @username
      - username
    """
    cleaned = raw_url.strip()
    if not cleaned:
        raise ValueError("GitHub link cannot be empty.")

    # Strip leading @
    if cleaned.startswith("@"):
        cleaned = cleaned[1:].strip()

    # Strip query parameters (?...) and hash fragments (#...)
    cleaned = cleaned.split("?")[0].split("#")[0].strip()

    # Remove protocol and domain prefix
    cleaned = re.sub(r"^(https?://)?(www\.)?github\.com/", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip("/ \t\r\n")

    parts = [p.strip() for p in cleaned.split("/") if p.strip()]
    if not parts:
        raise ValueError("Please provide a valid GitHub username or repository link.")

    owner = re.sub(r"[^a-zA-Z0-9\-_]", "", parts[0])
    if not owner:
        raise ValueError("Invalid GitHub username format. Please use a valid GitHub handle.")

    NON_REPO_SLUGS = {
        "repositories", "projects", "packages", "stars", "followers",
        "following", "tab", "orgs", "overview"
    }

    repo = None
    if len(parts) > 1:
        candidate_repo = parts[1]
        if candidate_repo.endswith(".git"):
            candidate_repo = candidate_repo[:-4]
        if candidate_repo.lower() not in NON_REPO_SLUGS:
            repo = candidate_repo

    return owner, repo


def scrape_github_public_repos(username: str) -> List[Dict[str, Any]]:
    """
    HTML scraping fallback for public GitHub repositories.
    Used when GitHub REST API rate limits (HTTP 403) are hit.
    Fetches https://github.com/{username}?tab=repositories.
    """
    url = f"https://github.com/{username}?tab=repositories"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            html = res.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    card_pattern = re.compile(
        r'<div class="col-10 col-lg-9 d-inline-block">([\s\S]*?)(?:</div>\s*</div>\s*</li>|</li>)',
        re.IGNORECASE
    )
    cards = card_pattern.findall(html)

    results: List[Dict[str, Any]] = []
    for card in cards:
        name_match = re.search(r'<a\s+href="(/[^/]+/[^/\"?#]+)"[^>]*itemprop="name codeRepository"[^>]*>([\s\S]*?)</a>', card)
        if not name_match:
            name_match = re.search(r'itemprop="name codeRepository"[^>]*href="(/[^/]+/[^/\"?#]+)"[^>]*>([\s\S]*?)</a>', card)
        if not name_match:
            continue

        repo_path = name_match.group(1).strip()
        repo_name = re.sub(r'<[^>]+>', '', name_match.group(2)).strip()
        html_url = f"https://github.com{repo_path}"

        is_fork = "forked from" in card.lower()

        desc_match = re.search(r'itemprop="description"[^>]*>([\s\S]*?)</p>', card)
        description = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip() if desc_match else ""

        lang_match = re.search(r'itemprop="programmingLanguage"[^>]*>([^<]+)</span>', card)
        language = lang_match.group(1).strip() if lang_match else None

        stars = 0
        star_match = re.search(r'href="[^"]*/stargazers"[^>]*>([\s\S]*?)</a>', card)
        if star_match:
            star_text = re.sub(r'<[^>]+>', '', star_match.group(1)).strip().replace(',', '')
            if 'k' in star_text.lower():
                try:
                    stars = int(float(star_text.lower().replace('k', '')) * 1000)
                except Exception:
                    stars = 0
            else:
                try:
                    stars = int(star_text)
                except Exception:
                    stars = 0

        forks = 0
        fork_match = re.search(r'href="[^"]*/forks"[^>]*>([\s\S]*?)</a>', card)
        if fork_match:
            fork_text = re.sub(r'<[^>]+>', '', fork_match.group(1)).strip().replace(',', '')
            if 'k' in fork_text.lower():
                try:
                    forks = int(float(fork_text.lower().replace('k', '')) * 1000)
                except Exception:
                    forks = 0
            else:
                try:
                    forks = int(fork_text)
                except Exception:
                    forks = 0

        topics = [t.strip() for t in re.findall(r'class="topic-tag[^"]*"[^>]*>([^<]+)</a>', card)]

        time_match = re.search(r'<relative-time[^>]*datetime="([^"]+)"', card)
        updated_at = time_match.group(1) if time_match else None

        results.append({
            "name": repo_name,
            "html_url": html_url,
            "description": description,
            "language": language,
            "fork": is_fork,
            "stargazers_count": stars,
            "forks_count": forks,
            "topics": topics,
            "updated_at": updated_at,
            "owner": {"login": username}
        })

    return results


def scrape_repos_from_atom(username: str) -> List[Dict[str, Any]]:
    """
    Atom RSS XML fallback for discovering public repositories.
    Fetches https://github.com/{username}.atom which is never API rate-limited.
    """
    url = f"https://github.com/{username}.atom"
    headers = {"User-Agent": "Existence-CMS-Portfolio"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            xml = res.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    repo_links = re.findall(rf'https://github\.com/{re.escape(username)}/([a-zA-Z0-9_\-\.]+)', xml)
    seen = set()
    repos: List[Dict[str, Any]] = []
    ignore_set = {
        "tab", "followers", "following", "stars", "packages", "projects",
        "repositories", "compare", "commits", "pull", "issues", "releases"
    }
    for r in repo_links:
        clean_r = r.split("/")[0].split("?")[0].split("#")[0].strip()
        if clean_r.endswith(".git"):
            clean_r = clean_r[:-4]
        if clean_r and clean_r.lower() not in ignore_set and clean_r not in seen:
            seen.add(clean_r)
            repos.append({
                "name": clean_r,
                "html_url": f"https://github.com/{username}/{clean_r}",
                "description": "",
                "language": None,
                "stargazers_count": 0,
                "forks_count": 0,
                "topics": [],
                "fork": False,
                "owner": {"login": username}
            })
    return repos


def fetch_github_json(endpoint_url: str, custom_token: Optional[str] = None) -> Any:
    """Safely fetch JSON from GitHub API with standard user agent."""
    headers = {
        "User-Agent": "Existence-CMS-Portfolio-Engine",
        "Accept": "application/vnd.github.v3+json"
    }
    if custom_token:
        headers["Authorization"] = f"token {custom_token}"

    req = urllib.request.Request(endpoint_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status not in (200, 201):
                raise ValueError(f"GitHub API returned HTTP {response.status}")
            data = json.loads(response.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError("Target GitHub user or repository was not found. Please verify the URL.")
        elif e.code == 403:
            raise ValueError("GitHub API rate limit reached or access forbidden. Please try again shortly.")
        else:
            raise ValueError(f"GitHub API error (HTTP {e.code}): {e.reason}")
    except Exception as e:
        raise ValueError(f"Failed to communicate with GitHub: {str(e)}")


def fetch_repo_readme(owner: str, repo: str) -> str:
    """Attempt to fetch README text for richer AI analysis."""
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
        req = urllib.request.Request(url, headers={"User-Agent": "Existence-CMS"})
        try:
            with urllib.request.urlopen(req, timeout=8) as res:
                if res.status == 200:
                    text = res.read().decode("utf-8", errors="ignore")
                    if text.strip():
                        return text[:3000]  # Cap at 3000 chars for prompt efficiency
        except Exception:
            continue
    return ""


def fetch_repo_file_text(owner: str, repo: str, file_path: str, custom_token: Optional[str] = None) -> Optional[str]:
    """Attempt to fetch raw file content from main or master branch."""
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        headers = {"User-Agent": "Existence-CMS"}
        if custom_token:
            headers["Authorization"] = f"token {custom_token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                if res.status == 200:
                    return res.read().decode("utf-8", errors="ignore")
        except Exception:
            continue
    return None


def fetch_active_languages(owner: str, repo: str, custom_token: Optional[str] = None) -> List[str]:
    """
    Fetch active language distribution from GitHub languages API.
    Only returns languages currently present with >0 bytes in the repository.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    try:
        lang_data = fetch_github_json(url, custom_token)
        if isinstance(lang_data, dict):
            active_langs = [k for k, v in sorted(lang_data.items(), key=lambda x: x[1], reverse=True) if v > 0]
            return active_langs
    except Exception:
        pass
    return []


def inspect_manifest_technologies(owner: str, repo: str, custom_token: Optional[str] = None) -> List[str]:
    """
    Inspects active manifests in the repository (package.json, requirements.txt, Dockerfile, etc.).
    If a technology/dependency was deleted from these files, it will NOT be detected.
    """
    detected: List[str] = []

    # 1. Check Docker / Docker Compose
    df = fetch_repo_file_text(owner, repo, "Dockerfile", custom_token)
    if df:
        detected.append("Docker")
    dc = fetch_repo_file_text(owner, repo, "docker-compose.yml", custom_token) or fetch_repo_file_text(owner, repo, "docker-compose.yaml", custom_token)
    if dc and "Docker" not in detected:
        detected.append("Docker")

    # 2. Check Node / JS package.json
    pkg_json_str = fetch_repo_file_text(owner, repo, "package.json", custom_token)
    if pkg_json_str:
        try:
            pkg_data = json.loads(pkg_json_str)
            all_deps = {}
            all_deps.update(pkg_data.get("dependencies") or {})
            all_deps.update(pkg_data.get("devDependencies") or {})
            deps_keys = {k.lower() for k in all_deps.keys()}

            dep_map = {
                "react": "React",
                "next": "Next.js",
                "vue": "Vue.js",
                "svelte": "Svelte",
                "angular": "Angular",
                "express": "Express.js",
                "fastify": "Fastify",
                "nestjs": "NestJS",
                "@nestjs/core": "NestJS",
                "tailwindcss": "TailwindCSS",
                "bootstrap": "Bootstrap",
                "prisma": "Prisma",
                "@prisma/client": "Prisma",
                "mongoose": "MongoDB",
                "mongodb": "MongoDB",
                "pg": "PostgreSQL",
                "postgres": "PostgreSQL",
                "mysql": "MySQL",
                "mysql2": "MySQL",
                "redis": "Redis",
                "ioredis": "Redis",
                "sqlite3": "SQLite",
                "better-sqlite3": "SQLite",
                "graphql": "GraphQL",
                "vite": "Vite",
                "electron": "Electron",
                "tauri": "Tauri",
                "jest": "Jest",
                "playwright": "Playwright",
                "cypress": "Cypress",
                "zustand": "Zustand",
                "redux": "Redux",
                "@reduxjs/toolkit": "Redux"
            }
            for pkg_key, canonical_name in dep_map.items():
                if pkg_key in deps_keys and canonical_name not in detected:
                    detected.append(canonical_name)
        except Exception:
            pass

    # 3. Check Python requirements.txt, pyproject.toml, Pipfile
    req_txt = fetch_repo_file_text(owner, repo, "requirements.txt", custom_token)
    pyproject = fetch_repo_file_text(owner, repo, "pyproject.toml", custom_token)
    pipfile = fetch_repo_file_text(owner, repo, "Pipfile", custom_token)
    py_content = (req_txt or "") + "\n" + (pyproject or "") + "\n" + (pipfile or "")
    if py_content.strip():
        py_lower = py_content.lower()
        py_dep_map = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "sqlalchemy": "SQLAlchemy",
            "psycopg": "PostgreSQL",
            "asyncpg": "PostgreSQL",
            "pymongo": "MongoDB",
            "redis": "Redis",
            "celery": "Celery",
            "torch": "PyTorch",
            "tensorflow": "TensorFlow",
            "scikit-learn": "Scikit-Learn",
            "pandas": "Pandas",
            "numpy": "NumPy",
            "langchain": "LangChain",
            "openai": "OpenAI API",
            "pytest": "Pytest",
            "alembic": "SQLAlchemy"
        }
        for kw, canonical_name in py_dep_map.items():
            if re.search(rf"\b{re.escape(kw)}\b", py_lower) and canonical_name not in detected:
                detected.append(canonical_name)

    # 4. Check Go & Rust
    if fetch_repo_file_text(owner, repo, "go.mod", custom_token) and "Go" not in detected:
        detected.append("Go")
    if fetch_repo_file_text(owner, repo, "Cargo.toml", custom_token) and "Rust" not in detected:
        detected.append("Rust")

    return detected


def clean_project_name(raw_name: str) -> str:
    """Format kebab-case, snake_case or dashed repo names into clean readable title."""
    if not raw_name:
        return "Untitled Project"
    # Replace dashes and underscores with spaces
    words = re.split(r"[-_]+", raw_name.strip())
    # Capitalize acronyms or normal words nicely
    cleaned_words = []
    for w in words:
        if not w:
            continue
        if w.lower() in ("ai", "api", "ui", "ux", "cms", "db", "sdk", "cli", "id", "ml", "nlp"):
            cleaned_words.append(w.upper())
        elif w.isupper() and len(w) <= 4:
            cleaned_words.append(w)
        else:
            cleaned_words.append(w.capitalize())
    title = " ".join(cleaned_words)
    return title if len(title) <= 150 else title[:147] + "..."


def categorize_technology(tech_name: str) -> Tuple[str, str, str]:
    """
    Returns (normalized_name, canonical_category, plain_english_why).
    """
    lower = tech_name.lower().strip()
    if lower in TECH_KNOWLEDGE_BASE:
        return TECH_KNOWLEDGE_BASE[lower]
    
    # Substring matching for common patterns
    if "sql" in lower and "postgresql" not in lower:
        return (tech_name.strip().title(), "Database", "manages structured data transactions and reliable querying.")
    if "css" in lower or "style" in lower:
        return (tech_name.strip(), "Frontend", "styles the user visual interface and responsive components.")
    if "cloud" in lower or "deploy" in lower or "host" in lower:
        return (tech_name.strip().title(), "Cloud/Deployment", "hosts and scales application infrastructure reliably.")
    if "test" in lower:
        return (tech_name.strip().title(), "Testing", "verifies code correctness through automated assertions.")
    if "ai" in lower or "learn" in lower or "model" in lower:
        return (tech_name.strip().title(), "Data/AI", "powers intelligent inference and data analysis.")
    
    return (tech_name.strip().title(), "Other", "powers specialized functionality and system capabilities.")


def detect_deployment_links(repo_data: Dict[str, Any], readme_text: str) -> List[Dict[str, Any]]:
    """
    Detects mandatory GitHub link and optional live deployment links (Vercel, Render, Railway, etc.).
    """
    links: List[Dict[str, Any]] = []
    github_url = repo_data.get("html_url", "").strip()

    # 1. Mandatory GitHub Link
    if github_url:
        links.append({
            "label": "GitHub Repository",
            "url": github_url,
            "link_type": "GitHub",
            "is_primary": True,
            "is_visible": True,
            "display_order": 0
        })

    # 2. Check repo homepage
    homepage = (repo_data.get("homepage") or "").strip()
    seen_urls = {github_url.rstrip("/").lower()}

    def add_optional_link(url: str, label_hint: str):
        u_clean = url.strip()
        if not (u_clean.startswith("http://") or u_clean.startswith("https://")):
            return
        if u_clean.rstrip("/").lower() in seen_urls:
            return
        seen_urls.add(u_clean.rstrip("/").lower())

        lowered = u_clean.lower()
        if "onrender.com" in lowered:
            label = "Render Live Deployment"
            l_type = "Deployment"
        elif "vercel.app" in lowered:
            label = "Vercel Live Deployment"
            l_type = "Deployment"
        elif "railway.app" in lowered or "up.railway.app" in lowered:
            label = "Railway Live Deployment"
            l_type = "Deployment"
        elif "github.io" in lowered:
            label = "GitHub Pages Demo"
            l_type = "Live Demo"
        elif "netlify.app" in lowered:
            label = "Netlify Live Demo"
            l_type = "Live Demo"
        elif "docs" in lowered or "documentation" in lowered:
            label = "Documentation"
            l_type = "Documentation"
        else:
            label = label_hint or "Live Demo"
            l_type = "Live Demo"

        links.append({
            "label": label,
            "url": u_clean,
            "link_type": l_type,
            "is_primary": False,
            "is_visible": True,
            "display_order": len(links)
        })

    if homepage:
        add_optional_link(homepage, "Live Deployment")

    # 3. Check README for prominent Vercel / Render / Railway links
    if readme_text:
        found_deployments = re.findall(
            r'https?://[a-zA-Z0-9_\-\.]+(?:\.onrender\.com|\.vercel\.app|\.up\.railway\.app|\.railway\.app|\.netlify\.app|\.github\.io)[^\s\)\]\"\'<>]*',
            readme_text,
            flags=re.IGNORECASE
        )
        for dep in found_deployments:
            add_optional_link(dep.rstrip(".,;"), "Live Deployment")

    # If an active live deployment link exists, make it primary and GitHub secondary
    if len(links) > 1:
        # First non-github deployment link becomes primary
        for idx, l in enumerate(links):
            if l["link_type"] in ("Deployment", "Live Demo"):
                l["is_primary"] = True
                break
        for idx, l in enumerate(links):
            if l["link_type"] == "GitHub":
                l["is_primary"] = False
                break

    return links


TECH_FRIENDLY_ROLES = {
    "python": "The Master Recipe Chef",
    "javascript": "The Spark of Motion",
    "typescript": "The Strict Safety Inspector",
    "react": "The Interactive Storefront Window",
    "fastapi": "The High-Speed Dispatch Hub",
    "next.js": "The Complete Publishing House",
    "nextjs": "The Complete Publishing House",
    "express.js": "The Nimble City Courier",
    "express": "The Nimble City Courier",
    "django": "The All-In-One Grand Manor",
    "flask": "The Handy Pocket Toolkit",
    "vue.js": "The Friendly Guidebook",
    "vue": "The Friendly Guidebook",
    "angular": "The Structured Engineering Firm",
    "svelte": "The Pure Handcrafted Artisan",
    "tailwind": "The Master Styling Palette",
    "tailwindcss": "The Master Styling Palette",
    "bootstrap": "The Ready-Made Decor Kit",
    "html5": "The Architectural Frame",
    "html": "The Architectural Frame",
    "css3": "The Interior Designer",
    "css": "The Interior Designer",
    "postgresql": "The Heavy-Duty Bank Vault",
    "postgres": "The Heavy-Duty Bank Vault",
    "sqlite": "The Fireproof Desk Drawer Safe",
    "mongodb": "The Flexible Folder Archive",
    "redis": "The Quick-Access Memory Desk",
    "mysql": "The Reliable Town Hall Registrar",
    "supabase": "The Modern Cloud Strongroom",
    "firebase": "The Live Synchronized Chalkboard",
    "docker": "The Sturdy Shipping Container",
    "kubernetes": "The Harbor Master & Traffic Conductor",
    "render": "The Automated Cloud Workshop",
    "vercel": "The Global Lightning Relay",
    "railway": "The Rapid Infrastructure Track",
    "git": "The Unbreakable Time Machine",
    "github": "The Global Community Workshop",
    "github actions": "The Automatic Quality Assembly Line",
    "pytorch": "The Pattern Learning Laboratory",
    "tensorflow": "The Industrial Machine Learning Factory",
    "openai api": "The Observant Intelligent Assistant",
    "google gemini": "The Multi-Talented Intelligent Partner",
    "pandas": "The Master Data Organizer",
    "numpy": "The High-Speed Math Engine",
    "vite": "The Instant Workshop Motor",
    "node.js": "The Fast-Paced Order Taker",
    "nodejs": "The Fast-Paced Order Taker",
    "graphql": "The Custom Order Menu",
    "nginx": "The High-Speed Traffic Conductor",
    "linux": "The Rock-Solid Bedrock Foundation",
    "pytest": "The Rigorous Quality Testing Track",
    "jest": "The Swift Code Asserter",
    "playwright": "The Automated Secret Shopper",
    "cypress": "The In-Browser Inspection Scout"
}

CATEGORY_DEFAULT_ROLES = {
    "Frontend": "The User-Friendly Display Window",
    "Backend": "The Central Thinking Engine",
    "Framework": "The Organized Building Blueprint",
    "Database": "The Permanent Record Vault",
    "Programming Language": "The Clear Instruction Set",
    "Cloud/Deployment": "The 24/7 Global Host",
    "DevOps": "The Automation & Protection Station",
    "Data/AI": "The Smart Pattern Assistant",
    "Testing": "The Quality Assurance Inspector",
    "Other": "The Specialized Helper Tool"
}


def get_technology_super_simple_info(name: str, category: str, rationale: str = "") -> Tuple[str, str]:
    """
    Returns (friendly_role, super_simple_explanation) written in everyday words without jargon.
    """
    key = name.lower().strip()
    role = TECH_FRIENDLY_ROLES.get(key) or CATEGORY_DEFAULT_ROLES.get(category, "The Specialized Helper Tool")

    if rationale and len(rationale) > 20:
        clean_rat = rationale.strip().rstrip('.')
        explanation = f"{clean_rat}."
    elif key in TECH_KNOWLEDGE_BASE:
        explanation = TECH_KNOWLEDGE_BASE[key][2]
    elif category == "Frontend":
        explanation = "draws the visual screens, buttons, and layout so everything is easy to see, tap, and interact with on any screen size."
    elif category in ("Backend", "Framework"):
        explanation = "serves as the behind-the-scenes thinking engine that receives requests, makes decisions, and prepares answers quickly and reliably."
    elif category == "Database":
        explanation = "acts like a secure, permanent filing cabinet where all your records are safely organized and never lost."
    elif category == "Programming Language":
        explanation = "provides the clear set of instructions that tells the computer exactly what to do step by step."
    elif category in ("Cloud/Deployment", "DevOps"):
        explanation = "packs and protects the project so it stays awake, fast, and accessible to anyone on the internet day and night."
    elif category == "Data/AI":
        explanation = "learns patterns from information to help answer questions, suggest helpful ideas, and automate tedious chores."
    elif category == "Testing":
        explanation = "runs automated practice runs behind the scenes to verify that every part works perfectly before anyone uses it."
    else:
        explanation = "provides specialized capabilities to keep the application running smoothly, safely, and efficiently."

    return role, explanation


def generate_simple_ai_dossier(
    project_name: str,
    raw_desc: str,
    language: Optional[str],
    topics: List[str],
    tech_items: List[Dict[str, str]],
    links: List[Dict[str, Any]],
    stars: int,
    forks: int,
    readme_snippet: str
) -> Tuple[str, str]:
    """
    Synthesizes:
      1. A short crisp description (1-2 sentences for card previews).
      2. A massively big, advancedly detailed, beautifully formatted AI project dossier written
         in super simple words using everyday physical analogies, without condescending references.
    """
    clean_desc = raw_desc.strip() if raw_desc else ""
    tech_names = [t["name"] for t in tech_items]
    primary_lang = language or (tech_names[0] if tech_names else "Modern Software")

    # 1. Short Description (Crisp, approachable preview)
    if clean_desc:
        clean_phrase = clean_desc.rstrip('.')
        short_desc = f"{clean_phrase}. Built with {', '.join(tech_names[:3]) if tech_names else primary_lang} to keep everyday workflows fast, organized, and reliable."
    else:
        short_desc = f"An intuitive, dependable solution built with {', '.join(tech_names[:3]) if tech_names else primary_lang} that turns complicated tasks into smooth, effortless steps."
    if len(short_desc) > 245:
        short_desc = short_desc[:242] + "..."

    # 2. Section 1: Purpose & Big Picture
    if clean_desc:
        pain_point = (
            f"Before **{project_name}** was created, people dealing with this task had to manage slow, repetitive, and often confusing manual work around {clean_desc.lower().rstrip('.')}. "
            f"Without an organized tool, essential details easily get scattered across messy notes, lost in buried folders, or forgotten in endless email threads. "
            f"A single innocent mistake could mean starting all over again from scratch, causing wasted hours and unnecessary stress."
        )
        solution = (
            f"**{project_name}** steps in as a calm, dependable digital helper. It brings all the necessary controls and information into one clean, welcoming space. "
            f"Instead of memorizing complicated rules or worrying about making an error, users can simply open this tool, follow clear cues, and finish what they set out to do with total peace of mind. "
            f"It takes care of the tricky behind-the-scenes checks automatically so you never have to second-guess yourself."
        )
    else:
        pain_point = (
            f"Before **{project_name}** was created, accomplishing this work required juggling multiple disjointed steps, manual checklists, and constant double-checking. "
            f"Important information was vulnerable to misplacement, and even small oversights could lead to delays or lost progress."
        )
        solution = (
            f"**{project_name}** was engineered to turn that complex workflow into a straightforward, predictable, and delightful experience. "
            f"It organizes every moving part into intuitive steps, handling all the heavy thinking and verification in the background so users achieve dependable results every single time."
        )

    # 3. Section 2: Real-World Physical Analogy
    analogy_text = (
        f"To understand exactly how **{project_name}** works, imagine a welcoming neighborhood bakery or master artisan workshop:\n\n"
        f"- **The Front Display Counter (What You See & Touch)**: Bright, clean display shelves showing everything clearly. "
        f"You simply point at what you want or hand over a note. It responds immediately with a smile.\n"
        f"- **The Friendly Attendant (The Quick Messenger)**: Takes your order ticket, double-checks that nothing was missed, and carries it briskly into the kitchen.\n"
        f"- **The Master Kitchen & Chef (The Thinking Engine)**: Follows the recipe with absolute precision, mixes the ingredients, cooks everything to perfection, and ensures every rule is honored.\n"
        f"- **The Fireproof Pantry & Safe (The Permanent Storage Vault)**: Every single recipe, order history, and ingredient count is neatly placed inside labeled, locked drawers so nothing is ever spoiled, lost, or forgotten."
    )

    # 4. Section 3: Building Blocks & Tools
    tech_breakdown_lines = []
    if tech_items:
        for t in tech_items:
            role, explanation = get_technology_super_simple_info(t["name"], t.get("category", "Other"), t.get("rationale", ""))
            tech_breakdown_lines.append(f"- **{t['name']}** (*{role}*): {explanation}")
    else:
        role, explanation = get_technology_super_simple_info(primary_lang, "Programming Language", "")
        tech_breakdown_lines.append(f"- **{primary_lang}** (*{role}*): {explanation}")

    tech_section = "\n".join(tech_breakdown_lines)

    # 5. Section 4: Architecture & Stations
    frontend_techs = [t["name"] for t in tech_items if t.get("category") == "Frontend" or t["name"] in ("React", "Vue.js", "Angular", "Svelte", "Next.js", "HTML5", "CSS3", "TailwindCSS")]
    backend_techs = [t["name"] for t in tech_items if (t.get("category") in ("Backend", "Framework") and t["name"] not in ("React", "Vue.js", "Angular", "Svelte", "TailwindCSS", "Bootstrap")) or t["name"] in ("FastAPI", "Express.js", "Django", "Flask", "Spring Boot", "NestJS", "Go", "Rust", "Node.js")]
    db_techs = [t["name"] for t in tech_items if t.get("category") == "Database" or t["name"] in ("PostgreSQL", "SQLite", "MongoDB", "Redis", "MySQL", "Prisma", "SQLAlchemy", "Supabase", "Firebase")]
    ai_techs = [t["name"] for t in tech_items if t.get("category") == "Data/AI"]
    cloud_techs = [t["name"] for t in tech_items if t.get("category") in ("Cloud/Deployment", "DevOps")]

    arch_steps = []
    if frontend_techs:
        arch_steps.append(
            f"1. **User Interface (Frontend)**: Styled and guided by {', '.join(frontend_techs[:3])}. "
            f"Think of this as the welcoming storefront counter. It presents clean screens, helpful buttons, and clear text that anyone can navigate comfortably."
        )
    else:
        arch_steps.append(
            f"1. **Input & Entry Points**: Structured with clear, friendly entry points and straightforward prompts that guide users naturally."
        )

    if backend_techs:
        arch_steps.append(
            f"2. **Processing Core (Backend)**: Powered by {', '.join(backend_techs[:3])}. "
            f"Think of this as the bustling kitchen behind the counter. It takes in requests, double-checks the rules, calculates the answers, and prepares everything safely and securely."
        )
    elif primary_lang and primary_lang in ("JavaScript", "TypeScript", "HTML5", "CSS3"):
        arch_steps.append(
            f"2. **Processing Core (Client-Side Logic)**: Driven directly by {primary_lang}. "
            f"The application does all of its thinking directly inside your web browser, which means it works with lightning speed without waiting for a distant server across the country."
        )
    else:
        arch_steps.append(
            f"2. **Processing Core (Application Engine)**: Driven by {primary_lang} to follow step-by-step instructions with deterministic, predictable accuracy."
        )

    if db_techs:
        arch_steps.append(
            f"3. **Data Layer & Storage (Database)**: Safeguarded by {', '.join(db_techs[:3])}. "
            f"Think of this as the permanent, locked storage room where every single record is filed away neatly so nothing is ever misplaced, forgotten, or overwritten by mistake."
        )

    if ai_techs:
        arch_steps.append(
            f"4. **Intelligent Assistance (Data & AI)**: Assisted by {', '.join(ai_techs[:2])}. "
            f"Think of this as a smart assistant with a sharp memory who analyzes information, recognizes helpful patterns, and automates repetitive tasks to save you time."
        )

    if cloud_techs:
        arch_steps.append(
            f"5. **Hosting & Continuous Care (Cloud & Delivery)**: Managed by {', '.join(cloud_techs[:2])}. "
            f"Think of this as the dependable utility grid that keeps the building lighted, powered, and open 24/7 so anyone around the world can visit at any moment."
        )

    if not arch_steps:
        arch_steps = [
            f"1. **Input Window**: User clicks or typed inputs are gently received.",
            f"2. **Processing Core (Backend)**: {primary_lang} calculates answers and checks rules.",
            f"3. **Output Screen**: Clear results and confirmations are shown on screen immediately."
        ]

    arch_explanation = (
        f"**{project_name}** divides its responsibilities into clear, specialized stations so that no single part gets overloaded:\n\n"
        + "\n\n".join(arch_steps)
    )

    # 6. Section 5: Step-by-Step Walkthrough
    walkthrough_steps = [
        "1. **Step 1: The Gentle Touch (Starting the Action)**: You click a button, tap a card, or submit information on your screen.",
        "2. **Step 2: The Polite Check at the Door (Instant Validation)**: Before anything travels anywhere, the system double-checks what you entered to ensure nothing was left blank, misspelled, or typed in an unusual way.",
        "3. **Step 3: The Sealed Envelope on the Road (Safe Travel)**: A secure digital messenger takes your request, places it into a protected envelope, and carries it smoothly across the wire to the processing center.",
        "4. **Step 4: The Security Gate & Welcome (Verification)**: The processing center verifies the seal on the envelope to confirm it is authentic and safe to open.",
        "5. **Step 5: The Thinking Brain (Doing the Work)**: The system follows its clear recipes, carries out the calculations, and prepares the exact result you requested.",
        "6. **Step 6: The Locked Safe (Permanent Storage)**: Any new or modified records are neatly placed inside the permanent filing cabinet with a confirmed stamp, making sure your work is safe even if power goes out.",
        "7. **Step 7: The Happy Delivery (Instant Feedback)**: The messenger races back to your screen and instantly displays the update or a cheerful green confirmation badge without any confusing delay."
    ]
    walkthrough_section = "\n\n".join(walkthrough_steps)

    # 7. Section 6: Everyday Superpowers
    capabilities = [
        "Massive Time Saver: Accomplishes in two seconds what used to take thirty minutes of manual hunting and typing",
        "Zero Lost Work: Automatically protects every entry into a permanent vault so nothing is ever lost or erased by mistake",
        "Comfortable on Any Screen: Adjusts its shape naturally whether you use it on a pocket phone, tablet, or large desk monitor",
        "Clean & Organized Layout: Keeps all information arranged on tidy, labeled shelves so you never have to search blindly",
        "Mistake-Proof Guardrails: Gently guides you if you leave something blank or type something incorrectly, stopping mistakes before they happen",
        "Instant Responsiveness: Operates with smooth, instant feedback so you never have to sit staring at a frozen screen or spinning wheel",
        "Private & Secure: Protects important settings behind verified locks so only authorized caretakers can make permanent updates"
    ]
    if topics:
        capabilities.insert(0, f"Specialized Purpose: Tailored specifically for modern workflows including {', '.join(topics[:4])}")
    if stars > 0:
        capabilities.append(f"Community Trusted: Celebrated by {stars} person{'s' if stars > 1 else ''} who bookmarked and recommended this project")

    cap_lines = "\n".join([f"- ✨ **{c}**" for c in capabilities])

    # 8. Section 7: Safety & Reliability
    reliability_points = [
        "- **Digital Seatbelts & Input Guardrails**: Every piece of information entered is checked against strict rules before being processed. Unexpected clicks or accidental typos bounce off harmlessly without causing glitches or crashes.",
        "- **Fireproof Locked Drawers**: Data is written using confirmed save operations. If a phone battery dies or the internet blinks during a save, incomplete records are rolled back cleanly, leaving your data in a perfect, uncorrupted state.",
        "- **Polite & Clear Guidance**: When something outside the system's control goes wrong (such as an offline network), the system provides a calm, clear message in plain words explaining what happened and how to proceed.",
        "- **Strict Key Access**: Critical controls and administrative settings are protected behind verified security locks, ensuring that only authorized caretakers can make permanent updates."
    ]
    reliability_section = "\n".join(reliability_points)

    # 9. Section 8: Future Improvements
    future_improvements = [
        "**One-Touch Pocket Mobile Apps**: Creating downloadable phone apps with offline-ready support so people can access their work even without an internet signal.",
        "**Helpful Reminders & Smart Alerts**: Adding friendly, gentle notifications that remind users of important upcoming milestones.",
        "**Natural Voice Interaction**: Allowing users to speak their requests out loud in everyday language.",
        "**Worldwide Language Translation**: Bringing instant language switching so people around the world can comfortably use it in their mother tongue.",
        "**Automated Safety & Quality Tracks**: Adding continuous background health monitors that inspect every line of code around the clock to ensure top-tier stability."
    ]
    future_lines = "\n".join([f"- 🚀 {f}" for f in future_improvements])

    # 10. Section 9: Links Section
    link_lines = []
    for l in links:
        is_mand = " *(Mandatory Source Repository)*" if l["link_type"] == "GitHub" else " *(Optional Live Deployment)*"
        link_lines.append(f"- [{l['label']}]({l['url']}){is_mand}")
    links_section = "\n".join(link_lines) if link_lines else "- No links currently registered."

    # Full Dossier in Markdown (Massively Big & Advancedly Detailed in Super Simple Words)
    full_dossier = f"""# {project_name}

> **Quick Summary**: {short_desc}

---

## 🎯 1. Purpose of the Project & The Big Picture

### The Real-World Frustration Before This Existed
{pain_point}

### How This Project Fixes It Once and for All
{solution}

### Who Benefits & Why It Matters
This project is built for everyday people who want their day-to-day work to feel calm, straightforward, and dependable. By bringing clarity, speed, and automatic safety checks to the table, it frees people up to focus on what actually matters without getting bogged down by technical headaches.

---

## 🏠 Real-World Analogy: How to Picture It in Daily Life
{analogy_text}

---

## 🛠️ 2. What I Used & Why I Used It
Here is a breakdown of every building block used to build this project, explained in everyday words:

{tech_section}

---

## 🏗️ 3. Architecture & How It Works (In Super Simple Words)
{arch_explanation}

---

## 🚶 Step-by-Step Walkthrough: What Happens Behind the Scenes When You Touch a Button
When you interact with **{project_name}**, here is the exact 7-step journey that takes place behind the scenes:

{walkthrough_section}

---

## ✨ 4. What This Project Can Do
Here are the practical everyday superpowers that make this project uniquely helpful:

{cap_lines}

---

## 🛡️ Behind the Scenes: How It Stays Strong, Safe & Reliable
{reliability_section}

---

## 🚀 5. How It Can Be Improved in the Future
Here are exciting ways this project can expand and become even more capable over time:

{future_lines}

---

## 🔗 6. Project Links
{links_section}
"""
    return short_desc, full_dossier.strip()



def extract_github_projects(github_url: str, custom_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Primary engine for extracting projects from a GitHub URL.
    Handles user profile URLs (all repos) and direct single repository URLs.
    """
    owner, repo_name = parse_github_target(github_url)

    raw_repos: List[Dict[str, Any]] = []
    source_type = "repo" if repo_name else "user"

    if repo_name:
        # Single repository extraction
        repo_api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        try:
            single_repo = fetch_github_json(repo_api_url, custom_token)
            raw_repos.append(single_repo)
        except Exception:
            # Fallback for single repository: construct repo object from public URL
            raw_repos.append({
                "name": repo_name,
                "html_url": f"https://github.com/{owner}/{repo_name}",
                "description": "",
                "language": None,
                "stargazers_count": 0,
                "forks_count": 0,
                "topics": [],
                "fork": False,
                "owner": {"login": owner}
            })
    else:
        # User profile extraction: fetch all public repos (up to 100 sorted by updated)
        user_repos_url = f"https://api.github.com/users/{owner}/repos?sort=updated&per_page=100"
        try:
            user_repos = fetch_github_json(user_repos_url, custom_token)
            if isinstance(user_repos, list):
                non_forks = [r for r in user_repos if not r.get("fork", False)]
                raw_repos = non_forks if non_forks else user_repos
        except Exception as exc:
            # API call failed (e.g. rate limit 403 or network issue) -> Try HTML scraping fallback
            scraped = scrape_github_public_repos(owner)
            if not scraped:
                # Try Atom feed fallback
                scraped = scrape_repos_from_atom(owner)
            if scraped:
                non_forks = [r for r in scraped if not r.get("fork", False)]
                raw_repos = non_forks if non_forks else scraped
            else:
                err_msg = str(exc)
                if "rate limit" in err_msg.lower() or "403" in err_msg:
                    raise ValueError(
                        f"GitHub API rate limit reached for your IP when connecting @{owner}. "
                        "Please paste a GitHub Personal Access Token (classic with public_repo) in Connect GitHub to unlock 5,000 requests/hr."
                    )
                raise ValueError(f"Could not load repositories for GitHub account '{owner}': {err_msg}")

    extracted_projects: List[Dict[str, Any]] = []

    for r in raw_repos:
        name_clean = clean_project_name(r.get("name", "Project"))
        raw_desc = r.get("description") or ""
        primary_lang = r.get("language")
        topics = r.get("topics") or []
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)
        is_archived = r.get("archived", False)

        # Dates
        created_at_str = r.get("created_at")
        updated_at_str = r.get("updated_at")
        start_year = None
        start_month = None
        end_year = None
        end_month = None

        if created_at_str:
            try:
                dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                start_year = dt.year
                start_month = dt.month
            except Exception:
                pass

        if updated_at_str:
            try:
                dt = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                end_year = dt.year
                end_month = dt.month
            except Exception:
                pass

        # Technology extraction & deduplication
        tech_dict: Dict[str, Dict[str, str]] = {}
        repo_owner = r.get("owner", {}).get("login", owner)
        repo_name_str = r.get("name", "")

        # 1. Active languages from GitHub API (only currently present languages with >0 bytes)
        active_langs = fetch_active_languages(repo_owner, repo_name_str, custom_token)
        if not active_langs and primary_lang:
            active_langs = [primary_lang]

        for lang in active_langs:
            norm_name, cat, rat = categorize_technology(lang)
            tech_dict[norm_name.lower()] = {
                "name": norm_name,
                "category": cat,
                "rationale": rat
            }

        # 2. Inspect active manifests (package.json, requirements.txt, Dockerfile, etc.)
        manifest_techs = inspect_manifest_technologies(repo_owner, repo_name_str, custom_token)
        for m_tech in manifest_techs:
            norm_name, cat, rat = categorize_technology(m_tech)
            tech_dict[norm_name.lower()] = {
                "name": norm_name,
                "category": cat,
                "rationale": rat
            }

        # 3. Active topics from repository metadata
        for top in topics:
            norm_name, cat, rat = categorize_technology(top)
            if norm_name.lower() not in tech_dict:
                tech_dict[norm_name.lower()] = {
                    "name": norm_name,
                    "category": cat,
                    "rationale": rat
                }

        tech_list = list(tech_dict.values())

        # README snippet
        readme_snippet = ""
        try:
            readme_snippet = fetch_repo_readme(r.get("owner", {}).get("login", owner), r.get("name", ""))
        except Exception:
            pass

        # Links (Mandatory GitHub + Optional Deployments)
        links = detect_deployment_links(r, readme_snippet)

        # Generate AI Descriptions
        short_desc, full_dossier = generate_simple_ai_dossier(
            project_name=name_clean,
            raw_desc=raw_desc,
            language=primary_lang,
            topics=topics,
            tech_items=tech_list,
            links=links,
            stars=stars,
            forks=forks,
            readme_snippet=readme_snippet
        )

        status = "Archived" if is_archived else "Completed"

        extracted_projects.append({
            "name": name_clean,
            "short_description": short_desc,
            "description": full_dossier,
            "full_ai_dossier": full_dossier,
            "status": status,
            "technologies": [{"name": t["name"], "category": t["category"]} for t in tech_list],
            "links": links,
            "stars": stars,
            "forks": forks,
            "repo_url": r.get("html_url", ""),
            "homepage_url": r.get("homepage"),
            "is_featured": stars >= 5 or len(links) > 1,
            "start_month": start_month,
            "start_year": start_year,
            "end_month": end_month,
            "end_year": end_year
        })

    return {
        "username": owner,
        "source_type": source_type,
        "projects_count": len(extracted_projects),
        "projects": extracted_projects
    }
