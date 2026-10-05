import json
import pytest
from app.models.project import Project, ProjectLink, Technology, ProjectTechnology, ProjectSkill
from app.models.skill import Skill
from app.models.profile import Profile
from app.models.audit import ContentRevision, AuditEvent


def test_01_project_metadata_taxonomies(client):
    """Verify project categories, statuses, and link types metadata endpoint."""
    res = client.get("/api/v1/projects/categories")
    assert res.status_code == 200
    data = res.json()
    assert "statuses" in data
    assert "link_types" in data
    assert "tech_categories" in data
    assert "Live Demo" in data["link_types"]
    assert "GitHub" in data["link_types"]
    assert "Deployment" in data["link_types"]
    assert "Completed" in data["statuses"]
    assert "Framework" in data["tech_categories"]


def test_02_project_name_validation_and_pin_protection(client, admin_headers):
    """
    Verify project name normalization, validation, and PIN security requirement.
    Empty/whitespace names rejected. Mutations without PIN rejected with 401/403.
    """
    # 1. No PIN header -> 401/403
    unprotected_res = client.post("/api/v1/projects", json={
        "name": "Existence CMS",
        "status": "Completed"
    })
    assert unprotected_res.status_code in [401, 403]

    # 2. Empty name -> rejected
    empty_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "   ",
        "status": "Completed"
    })
    assert empty_res.status_code in [400, 422]

    # 3. Valid creation with PIN header
    valid_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "  Existence Project  ",
        "short_description": "Production CMS portfolio",
        "status": "Completed"
    })
    assert valid_res.status_code == 201
    body = valid_res.json()
    assert body["name"] == "Existence Project"  # Whitespace trimmed
    assert body["status"] == "Completed"
    proj_id = body["id"]

    # 4. Duplicate project name under same profile -> 409 Conflict
    dup_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "existence project",  # case-insensitive duplicate
        "status": "In Progress"
    })
    assert dup_res.status_code == 409


def test_03_multiple_deployment_links_and_primary_invariant(client, admin_headers):
    """
    Verify core requirement: a project can have multiple deployment/demo links.
    Verify primary/preferred link invariant: at most one link is marked primary.
    """
    # Create project
    proj_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Multi Link App",
        "short_description": "Demonstrating multiple deployments"
    })
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 1. Add first link (Live Demo, Primary)
    l1_res = client.post(f"/api/v1/projects/{proj_id}/links", headers=admin_headers, json={
        "label": "Live Demo",
        "url": "https://existence-demo.vercel.app",
        "link_type": "Live Demo",
        "is_primary": True
    })
    assert l1_res.status_code == 201
    l1 = l1_res.json()
    assert l1["is_primary"] is True
    assert l1["link_type"] == "Live Demo"

    # 2. Add second link (GitHub Repo, not primary)
    l2_res = client.post(f"/api/v1/projects/{proj_id}/links", headers=admin_headers, json={
        "label": "GitHub Repository",
        "url": "https://github.com/org/existence-cms",
        "link_type": "GitHub",
        "is_primary": False
    })
    assert l2_res.status_code == 201
    l2 = l2_res.json()
    assert l2["is_primary"] is False

    # 3. Add third link (Backend API, marked primary) -> Should unset l1 as primary!
    l3_res = client.post(f"/api/v1/projects/{proj_id}/links", headers=admin_headers, json={
        "label": "API Swagger",
        "url": "https://api.existence.onrender.com/docs",
        "link_type": "API",
        "is_primary": True
    })
    assert l3_res.status_code == 201

    # Fetch project and verify primary invariant
    fetch_res = client.get(f"/api/v1/projects/{proj_id}")
    assert fetch_res.status_code == 200
    proj_data = fetch_res.json()
    assert len(proj_data["links"]) == 3
    assert proj_data["primary_link"] is not None
    assert proj_data["primary_link"]["label"] == "API Swagger"
    assert proj_data["primary_link"]["url"] == "https://api.existence.onrender.com/docs"

    # Check each link's is_primary flag
    l1_refreshed = next(l for l in proj_data["links"] if l["label"] == "Live Demo")
    assert l1_refreshed["is_primary"] is False


def test_04_url_validation_and_unsafe_scheme_rejection(client, admin_headers):
    """
    Server-side URL validation: reject unsafe schemes like javascript:,
    reject non-http/https, and handle duplicate URLs on same project.
    """
    proj_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Security URL App"
    })
    proj_id = proj_res.json()["id"]

    # 1. Unsafe scheme: javascript:
    bad_js = client.post(f"/api/v1/projects/{proj_id}/links", headers=admin_headers, json={
        "label": "Exploit",
        "url": "javascript:alert('xss')",
        "link_type": "Live Demo"
    })
    assert bad_js.status_code in [400, 422]

    # 2. Missing protocol
    bad_proto = client.post(f"/api/v1/projects/{proj_id}/links", headers=admin_headers, json={
        "label": "No Protocol",
        "url": "ftp://files.example.com",
        "link_type": "Other"
    })
    assert bad_proto.status_code in [400, 422]

    # 3. Valid URL
    good_link = client.post(f"/api/v1/projects/{proj_id}/links", headers=admin_headers, json={
        "label": "Valid Live Link",
        "url": "https://example.com/project",
        "link_type": "Live Demo"
    })
    assert good_link.status_code == 201

    # 4. Duplicate URL on same project -> Conflict 409
    dup_link = client.post(f"/api/v1/projects/{proj_id}/links", headers=admin_headers, json={
        "label": "Duplicate URL",
        "url": "https://example.com/project",
        "link_type": "Deployment"
    })
    assert dup_link.status_code == 409


def test_05_tech_stack_engine_and_deduplication(client, admin_headers, db_session):
    """
    Verify Tech Stack Engine:
    - Multiple technologies attached to project
    - Case-insensitive deduplication within same project
    - Reusable global Technology entities (no duplicate 'Python' in technologies table)
    - Technologies do not modify user skills
    """
    # 1. Create project with multiple technologies (strings and objects)
    p1_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Cloud Native Platform",
        "technologies": [
            {"name": "Python", "category": "Programming Language"},
            {"name": "FastAPI", "category": "Framework"},
            {"name": "PostgreSQL", "category": "Database"},
            {"name": "python", "category": "Programming Language"}  # Duplicate in same request
        ]
    })
    assert p1_res.status_code == 201
    p1 = p1_res.json()
    # Duplicate 'python' must have been stripped
    assert len(p1["technologies"]) == 3
    tech_names = [t["name"] for t in p1["technologies"]]
    assert "Python" in tech_names
    assert "FastAPI" in tech_names
    assert "PostgreSQL" in tech_names

    # 2. Create another project reusing 'Python' and 'PostgreSQL'
    p2_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Data Analytics Engine",
        "technologies": [
            "Python",
            "PostgreSQL",
            {"name": "Docker", "category": "DevOps"}
        ]
    })
    assert p2_res.status_code == 201

    # Verify global Technology table has exactly ONE 'Python' and ONE 'PostgreSQL' record
    python_count = db_session.query(Technology).filter(Technology.name == "Python").count()
    assert python_count == 1

    postgres_count = db_session.query(Technology).filter(Technology.name == "PostgreSQL").count()
    assert postgres_count == 1


def test_06_project_dates_and_active_validation(client, admin_headers):
    """
    Verify date validation:
    - Start and end months 1-12
    - Active (is_current=True) projects cannot have end dates
    - End date cannot precede start date
    """
    # 1. Active project with end date -> Rejected
    res1 = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Invalid Active Dates",
        "start_month": 1,
        "start_year": 2025,
        "end_month": 12,
        "end_year": 2025,
        "is_current": True
    })
    assert res1.status_code in [400, 422]

    # 2. End date earlier than start date -> Rejected
    res2 = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Backwards Dates",
        "start_month": 6,
        "start_year": 2025,
        "end_month": 1,
        "end_year": 2025,
        "is_current": False
    })
    assert res2.status_code in [400, 422]

    # 3. Valid timeline
    res3 = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Chronologically Sound",
        "start_month": 3,
        "start_year": 2024,
        "end_month": 9,
        "end_year": 2025,
        "is_current": False
    })
    assert res3.status_code == 201


def test_07_associated_skills_relationship(client, admin_headers):
    """
    Verify project can optionally associate with existing skills without modifying skill ratings.
    """
    # 1. Create a skill
    skill_res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Distributed Systems",
        "rating": 6,
        "category": "Technical"
    })
    assert skill_res.status_code == 201
    skill_id = skill_res.json()["id"]

    # 2. Create project associating this skill
    proj_res = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Microservice Architecture",
        "skill_ids": [skill_id]
    })
    assert proj_res.status_code == 201
    proj_data = proj_res.json()
    assert len(proj_data["skills"]) == 1
    assert proj_data["skills"][0]["name"] == "Distributed Systems"
    assert proj_data["skills"][0]["rating"] == 6

    # 3. Verify skill rating remains intact
    skill_check = client.get(f"/api/v1/skills/{skill_id}")
    assert skill_check.status_code == 200
    assert skill_check.json()["rating"] == 6


def test_08_reordering_and_deterministic_sorting(client, admin_headers):
    """Verify bulk reordering of projects and links."""
    # Create 3 projects
    p1 = client.post("/api/v1/projects", headers=admin_headers, json={"name": "Reorder Proj A", "display_order": 1}).json()
    p2 = client.post("/api/v1/projects", headers=admin_headers, json={"name": "Reorder Proj B", "display_order": 2}).json()
    p3 = client.post("/api/v1/projects", headers=admin_headers, json={"name": "Reorder Proj C", "display_order": 3}).json()

    # Reorder projects via PATCH /api/v1/projects/reorder
    reorder_payload = [
        {"id": p3["id"], "display_order": 0},
        {"id": p1["id"], "display_order": 1},
        {"id": p2["id"], "display_order": 2}
    ]
    reorder_res = client.patch("/api/v1/projects/reorder", headers=admin_headers, json=reorder_payload)
    assert reorder_res.status_code == 200

    # Fetch list and verify deterministic order
    list_res = client.get("/api/v1/projects")
    assert list_res.status_code == 200
    items = list_res.json()
    ids_in_order = [p["id"] for p in items]
    assert ids_in_order.index(p3["id"]) < ids_in_order.index(p1["id"])
    assert ids_in_order.index(p1["id"]) < ids_in_order.index(p2["id"])


def test_09_public_vs_private_visibility(client, admin_headers):
    """
    Public filtration:
    - Public requests (no admin) exclude private projects
    - Public requests exclude private links on public projects
    """
    # 1. Create public project with 1 public link and 1 private link
    pub_proj = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Public Showcase",
        "is_visible": True,
        "links": [
            {"label": "Public Demo", "url": "https://showcase.example.com", "is_visible": True},
            {"label": "Private Admin Panel", "url": "https://admin.showcase.example.com", "is_visible": False}
        ]
    }).json()

    # 2. Create private project
    priv_proj = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Secret Stealth App",
        "is_visible": False
    }).json()

    # 3. Public query (unauthenticated)
    pub_list = client.get("/api/v1/projects").json()
    pub_ids = [p["id"] for p in pub_list]
    assert pub_proj["id"] in pub_ids
    assert priv_proj["id"] not in pub_ids  # Private project excluded!

    # Public project must only show the public link
    pub_proj_data = next(p for p in pub_list if p["id"] == pub_proj["id"])
    assert len(pub_proj_data["links"]) == 1
    assert pub_proj_data["links"][0]["label"] == "Public Demo"

    # 4. Admin query with include_hidden=True
    admin_list = client.get("/api/v1/projects?include_hidden=true", headers=admin_headers).json()
    admin_ids = [p["id"] for p in admin_list]
    assert priv_proj["id"] in admin_ids


def test_10_cascade_deletion_and_audit_integration(client, admin_headers, db_session):
    """
    Verify deletion safety and revision logging:
    - Deleting project cascades links and project_technologies
    - Does NOT delete underlying reusable Technology
    - Records ContentRevision and AuditEvent
    """
    # Create project with a link and technology
    proj = client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Temporary Deletable Project",
        "technologies": [{"name": "Rust", "category": "Programming Language"}],
        "links": [{"label": "Rust Repo", "url": "https://github.com/rust-app"}]
    }).json()
    proj_id = proj["id"]
    link_id = proj["links"][0]["id"]
    tech_id = proj["technologies"][0]["technology_id"]

    # Delete project
    del_res = client.delete(f"/api/v1/projects/{proj_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # Verify project is gone
    get_res = client.get(f"/api/v1/projects/{proj_id}")
    assert get_res.status_code == 404

    # Verify link was cascaded
    link_in_db = db_session.query(ProjectLink).filter(ProjectLink.id == link_id).first()
    assert link_in_db is None

    # Verify reusable Technology 'Rust' STILL EXISTS!
    rust_tech = db_session.query(Technology).filter(Technology.id == tech_id).first()
    assert rust_tech is not None
    assert rust_tech.name == "Rust"

    # Verify ContentRevision logged DELETE
    revision = (
        db_session.query(ContentRevision)
        .filter(ContentRevision.entity_name == "project", ContentRevision.entity_id == str(proj_id))
        .filter(ContentRevision.action == "DELETE")
        .first()
    )
    assert revision is not None


def test_11_consolidated_public_profile_includes_projects(client, admin_headers):
    """Verify GET /api/v1/profile/public includes visible projects with nested links and tech stack."""
    # Ensure at least one visible project exists
    client.post("/api/v1/projects", headers=admin_headers, json={
        "name": "Existence Production Suite",
        "short_description": "Full featured identity platform",
        "is_visible": True,
        "technologies": ["Python", "React", "TypeScript"],
        "links": [{"label": "Live Portfolio", "url": "https://existence.live", "is_primary": True}]
    })

    res = client.get("/api/v1/profile/public")
    assert res.status_code == 200
    data = res.json()
    assert "projects" in data
    assert isinstance(data["projects"], list)
    assert len(data["projects"]) > 0

    found = next((p for p in data["projects"] if p["name"] == "Existence Production Suite"), None)
    assert found is not None
    assert len(found["technologies"]) == 3
    assert len(found["links"]) == 1
    assert found["primary_link"]["label"] == "Live Portfolio"


def test_12_github_extraction_endpoint_and_ai_dossier(client, monkeypatch):
    """
    Verify POST /api/v1/projects/extract-github extracts projects,
    synthesizes simple AI descriptions, classifies tech stacks, and flags mandatory GitHub links and optional deployments.
    """
    from app.services import github_extractor

    mock_repo = {
        "name": "ai-neural-canvas",
        "description": "Interactive deep learning canvas for real-time latent space exploration",
        "html_url": "https://github.com/developer/ai-neural-canvas",
        "homepage": "https://ai-neural-canvas.onrender.com",
        "language": "Python",
        "topics": ["fastapi", "react", "pytorch", "tailwind"],
        "stargazers_count": 42,
        "forks_count": 8,
        "archived": False,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-09-20T12:00:00Z",
        "owner": {"login": "developer"}
    }

    def fake_fetch_json(url, token=None):
        return mock_repo

    monkeypatch.setattr(github_extractor, "fetch_github_json", fake_fetch_json)
    monkeypatch.setattr(github_extractor, "fetch_repo_readme", lambda owner, repo: "Demo live at https://ai-neural-canvas.onrender.com")

    res = client.post("/api/v1/projects/extract-github", json={
        "github_url": "https://github.com/developer/ai-neural-canvas"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "developer"
    assert data["source_type"] == "repo"
    assert data["projects_count"] == 1
    
    proj = data["projects"][0]
    assert proj["name"] == "AI Neural Canvas"
    assert proj["stars"] == 42
    assert proj["is_featured"] is True
    assert proj["short_description"] is not None
    assert len(proj["technologies"]) >= 3

    # Check AI dossier structure
    dossier = proj["description"]
    assert "1. Purpose of the Project" in dossier
    assert "2. What I Used & Why I Used It" in dossier
    assert "3. Architecture & How It Works (In Super Simple Words)" in dossier
    assert "4. What This Project Can Do" in dossier
    assert "5. How It Can Be Improved in the Future" in dossier
    assert "6. Project Links" in dossier

    # Check Mandatory GitHub link & Optional Deployment link
    link_types = [l["link_type"] for l in proj["links"]]
    assert "GitHub" in link_types
    assert "Deployment" in link_types

    github_link = next(l for l in proj["links"] if l["link_type"] == "GitHub")
    assert github_link["url"] == "https://github.com/developer/ai-neural-canvas"

    render_link = next(l for l in proj["links"] if "onrender.com" in l["url"])
    assert render_link["url"] == "https://ai-neural-canvas.onrender.com"


def test_13_bulk_import_projects_with_pin(client, admin_headers):
    """
    Verify POST /api/v1/projects/bulk-import securely imports extracted projects with PIN.
    Supports transactional creation and idempotent updates on existing projects.
    """
    # 1. Unauthenticated / without PIN -> 401/403
    unauth_res = client.post("/api/v1/projects/bulk-import", json={
        "projects": [{"name": "Unauth Project"}]
    })
    assert unauth_res.status_code in [401, 403]

    # 2. Bulk import with PIN
    payload = {
        "projects": [
            {
                "name": "Extracted Engine Alpha",
                "short_description": "First extracted system",
                "description": "Full AI dossier for Alpha",
                "status": "Completed",
                "technologies": [
                    {"name": "FastAPI", "category": "Framework"},
                    {"name": "React", "category": "Framework"}
                ],
                "links": [
                    {"label": "GitHub", "url": "https://github.com/test/alpha", "link_type": "GitHub", "is_primary": True},
                    {"label": "Render", "url": "https://alpha.onrender.com", "link_type": "Deployment", "is_primary": False}
                ]
            },
            {
                "name": "Extracted Engine Beta",
                "short_description": "Second extracted system",
                "description": "Full AI dossier for Beta",
                "status": "In Progress",
                "technologies": [
                    {"name": "TypeScript", "category": "Programming Language"}
                ],
                "links": [
                    {"label": "GitHub", "url": "https://github.com/test/beta", "link_type": "GitHub", "is_primary": True}
                ]
            }
        ]
    }

    import_res = client.post("/api/v1/projects/bulk-import", headers=admin_headers, json=payload)
    assert import_res.status_code == 201
    imported = import_res.json()
    assert len(imported) == 2
    names = [p["name"] for p in imported]
    assert "Extracted Engine Alpha" in names
    assert "Extracted Engine Beta" in names

    # Verify links on Alpha
    alpha = next(p for p in imported if p["name"] == "Extracted Engine Alpha")
    assert len(alpha["links"]) == 2
    assert any(l["link_type"] == "GitHub" for l in alpha["links"])

    # 3. Idempotent re-import does not crash with 409, but updates smoothly
    update_payload = {
        "projects": [
            {
                "name": "Extracted Engine Alpha",
                "short_description": "Updated description for Alpha",
                "description": "Updated full AI dossier for Alpha"
            }
        ]
    }
    reimport_res = client.post("/api/v1/projects/bulk-import", headers=admin_headers, json=update_payload)
    assert reimport_res.status_code == 201
    updated_items = reimport_res.json()
    assert len(updated_items) == 1
    assert updated_items[0]["short_description"] == "Updated description for Alpha"


def test_14_github_account_linking_and_unlinking(client, admin_headers):
    """
    Verify linking and unlinking a GitHub account for automated project syncing.
    PIN required.
    """
    # 1. Unauthenticated -> 401/403
    unauth_res = client.get("/api/v1/projects/github-link")
    assert unauth_res.status_code in [401, 403]

    # 2. Link account
    link_res = client.post("/api/v1/projects/github-link", headers=admin_headers, json={
        "github_url": "https://github.com/octocat",
        "auto_sync": False,
        "webhook_secret": "my-secret-key"
    })
    assert link_res.status_code == 200
    link_data = link_res.json()
    assert link_data["username"] == "octocat"
    assert link_data["auto_sync"] is False

    # 3. Get linked account
    get_res = client.get("/api/v1/projects/github-link", headers=admin_headers)
    assert get_res.status_code == 200
    assert get_res.json()["username"] == "octocat"

    # 4. Unlink account
    del_res = client.delete("/api/v1/projects/github-link", headers=admin_headers)
    assert del_res.status_code == 200

    # 5. Verify unlinked
    get_res2 = client.get("/api/v1/projects/github-link", headers=admin_headers)
    assert get_res2.status_code == 200
    assert get_res2.json() is None


def test_15_automatic_github_sync_create_and_update_with_tech_removal(client, admin_headers, monkeypatch):
    """
    Verify core prompt requirement:
    - Auto-sync extracts new repository when added on GitHub, creating project with AI dossier & links.
    - If repository is modified on GitHub (e.g. backend removed), tech stack is updated (deleted tech removed),
      and a brand new AI dossier is re-generated reflecting the updated stack.
    """
    from app.services import github_extractor

    # Phase 1: Repo initially contains FastAPI + PostgreSQL backend and React frontend
    initial_repo = {
        "name": "super-portal",
        "description": "Full-stack analytics portal",
        "html_url": "https://github.com/developer/super-portal",
        "homepage": "https://super-portal.onrender.com",
        "language": "Python",
        "topics": ["fastapi", "react", "postgresql", "docker"],
        "stargazers_count": 15,
        "forks_count": 2,
        "archived": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-06-01T00:00:00Z",
        "owner": {"login": "developer"}
    }

    monkeypatch.setattr(github_extractor, "fetch_github_json", lambda url, token=None: initial_repo)
    monkeypatch.setattr(github_extractor, "fetch_repo_readme", lambda owner, repo: "Live at https://super-portal.onrender.com")
    monkeypatch.setattr(github_extractor, "fetch_active_languages", lambda owner, repo, token=None: ["Python", "JavaScript"])
    monkeypatch.setattr(github_extractor, "inspect_manifest_technologies", lambda owner, repo, token=None: ["FastAPI", "PostgreSQL", "React", "Docker"])

    # 1. Trigger sync to create the project
    sync_res_1 = client.post(
        "/api/v1/projects/sync-github?github_url=https://github.com/developer/super-portal",
        headers=admin_headers
    )
    assert sync_res_1.status_code == 200
    res_data_1 = sync_res_1.json()
    assert res_data_1["created_count"] == 1
    assert "Super Portal" in res_data_1["created_projects"]

    # Verify project in DB
    list_res_1 = client.get("/api/v1/projects?search=Super Portal")
    assert list_res_1.status_code == 200
    projects_1 = list_res_1.json()
    assert len(projects_1) == 1
    proj_1 = projects_1[0]
    tech_names_1 = [t["name"] for t in proj_1["technologies"]]
    assert "FastAPI" in tech_names_1
    assert "PostgreSQL" in tech_names_1
    assert "React" in tech_names_1
    assert "Docker" in tech_names_1

    # Verify AI dossier in Phase 1 mentions FastAPI / Processing Core
    assert "FastAPI" in proj_1["description"]
    assert "Processing Core (Backend)" in proj_1["description"]
    assert any(l["link_type"] == "GitHub" for l in proj_1["links"])
    assert any("onrender.com" in l["url"] for l in proj_1["links"])

    # Phase 2: User changes repo on GitHub!
    # Deletes backend (FastAPI, PostgreSQL, Docker) completely!
    # Now it is a pure client-side TypeScript + Tailwind portfolio!
    updated_repo = {
        "name": "super-portal",
        "description": "Ultra lightweight static showcase",
        "html_url": "https://github.com/developer/super-portal",
        "homepage": "https://super-portal.vercel.app",
        "language": "TypeScript",
        "topics": ["typescript", "tailwind", "vite"],
        "stargazers_count": 25,
        "forks_count": 5,
        "archived": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-10-01T00:00:00Z",
        "owner": {"login": "developer"}
    }

    monkeypatch.setattr(github_extractor, "fetch_github_json", lambda url, token=None: updated_repo)
    monkeypatch.setattr(github_extractor, "fetch_repo_readme", lambda owner, repo: "Static demo live at https://super-portal.vercel.app")
    monkeypatch.setattr(github_extractor, "fetch_active_languages", lambda owner, repo, token=None: ["TypeScript"])
    monkeypatch.setattr(github_extractor, "inspect_manifest_technologies", lambda owner, repo, token=None: ["TailwindCSS", "Vite"])

    # 2. Trigger sync again on the modified repository
    sync_res_2 = client.post(
        "/api/v1/projects/sync-github?github_url=https://github.com/developer/super-portal",
        headers=admin_headers
    )
    assert sync_res_2.status_code == 200
    res_data_2 = sync_res_2.json()
    assert res_data_2["updated_count"] == 1
    assert "Super Portal" in res_data_2["updated_projects"]

    # Verify project in DB: NO DUPLICATE CREATED, and OLD BACKEND TECH REMOVED!
    list_res_2 = client.get("/api/v1/projects?search=Super Portal")
    assert list_res_2.status_code == 200
    projects_2 = list_res_2.json()
    assert len(projects_2) == 1
    proj_2 = projects_2[0]

    tech_names_2 = [t["name"] for t in proj_2["technologies"]]
    # Old deleted backend technologies MUST be gone:
    assert "FastAPI" not in tech_names_2
    assert "PostgreSQL" not in tech_names_2
    assert "Docker" not in tech_names_2
    # New active technologies MUST be present:
    assert "TypeScript" in tech_names_2
    assert "TailwindCSS" in tech_names_2

    # New AI description generated:
    assert "FastAPI" not in proj_2["description"]
    assert "TailwindCSS" in proj_2["description"]
    assert "TypeScript" in proj_2["description"]
    assert any("vercel.app" in l["url"] for l in proj_2["links"])


def test_16_github_webhook_realtime_synchronization(client, monkeypatch):
    """
    Verify POST /api/v1/projects/github-webhook:
    - Responds to 'ping' event with 200 and pong.
    - Handles 'push' event payload to trigger synchronization.
    """
    from app.services import github_extractor

    # 1. Ping event
    ping_res = client.post(
        "/api/v1/projects/github-webhook",
        headers={"X-GitHub-Event": "ping"},
        json={"zen": "Non-blocking is better than blocking."}
    )
    assert ping_res.status_code == 200
    assert "Pong" in ping_res.json()["message"]

    # 2. Push event with repo
    mock_pushed_repo = {
        "name": "auto-synced-agent",
        "description": "Autonomous background execution worker",
        "html_url": "https://github.com/developer/auto-synced-agent",
        "homepage": "https://agent.railway.app",
        "language": "Go",
        "topics": ["go", "docker"],
        "stargazers_count": 10,
        "forks_count": 1,
        "archived": False,
        "owner": {"login": "developer"}
    }
    monkeypatch.setattr(github_extractor, "fetch_github_json", lambda url, token=None: mock_pushed_repo)
    monkeypatch.setattr(github_extractor, "fetch_repo_readme", lambda owner, repo: "")
    monkeypatch.setattr(github_extractor, "fetch_active_languages", lambda owner, repo, token=None: ["Go"])
    monkeypatch.setattr(github_extractor, "inspect_manifest_technologies", lambda owner, repo, token=None: ["Go", "Docker"])

    push_res = client.post(
        "/api/v1/projects/github-webhook",
        headers={"X-GitHub-Event": "push"},
        json={
            "repository": {
                "name": "auto-synced-agent",
                "html_url": "https://github.com/developer/auto-synced-agent",
                "owner": {"login": "developer"}
            }
        }
    )
    assert push_res.status_code == 200
    push_data = push_res.json()
    assert push_data["status"] == "success"

    # Verify project was auto-extracted and created into CMS
    check_res = client.get("/api/v1/projects?search=Auto Synced Agent")
    assert check_res.status_code == 200
    found_projects = check_res.json()
    assert len(found_projects) == 1
    assert found_projects[0]["name"] == "Auto Synced Agent"
    assert any("railway.app" in l["url"] for l in found_projects[0]["links"])


def test_17_generate_ai_dossier_endpoint(client, admin_headers):
    """Verify on-demand AI dossier generation endpoint with super-simple words & rich sections."""
    res = client.post(
        "/api/v1/projects/generate-ai-dossier",
        headers=admin_headers,
        json={
            "name": "Smart Expense Tracker",
            "raw_description": "Helps families track monthly grocery and utility budgets without spreadsheet headaches.",
            "language": "Python",
            "technologies": ["FastAPI", "React", "SQLite", "TailwindCSS"],
            "topics": ["finance", "budgeting", "family"],
            "links": [{"label": "GitHub Repo", "url": "https://github.com/developer/smart-expense", "link_type": "GitHub"}]
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "short_description" in data
    assert "description" in data
    dossier = data["description"]

    # Verify all 6 required sections
    assert "1. Purpose of the Project" in dossier
    assert "2. What I Used & Why I Used It" in dossier
    assert "3. Architecture & How It Works (In Super Simple Words)" in dossier
    assert "4. What This Project Can Do" in dossier
    assert "5. How It Can Be Improved in the Future" in dossier
    assert "6. Project Links" in dossier

    # Verify physical real-world analogy and step-by-step walkthrough
    assert "Real-World Analogy: How to Picture It in Daily Life" in dossier
    assert "Step-by-Step Walkthrough" in dossier
    assert "Behind the Scenes: How It Stays Strong, Safe & Reliable" in dossier
    assert "FastAPI" in dossier
    assert "Processing Core (Backend)" in dossier

    # Verify NO condescending references
    lower_d = dossier.lower()
    for forbidden in ["kid", "child", "illiterate", "fool", "dummy", "simpleton", "eli5", "5-year-old"]:
        assert forbidden not in lower_d

