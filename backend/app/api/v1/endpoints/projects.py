from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectPatch,
    ProjectOut,
    ProjectReorderItem,
    ProjectLinkCreate,
    ProjectLinkUpdate,
    ProjectLinkPatch,
    ProjectLinkOut,
    ProjectLinkReorderItem,
    ProjectCategoriesOut,
    GitHubExtractionRequest,
    GitHubExtractionResponse,
    ProjectBulkImportRequest,
    GitHubAccountLinkCreate,
    GitHubAccountLinkUpdate,
    GitHubAccountLinkOut,
    GitHubSyncResultOut,
    ProjectAiDossierGenerateRequest,
    ProjectAiDossierGenerateResponse
)
from app.api.deps import require_pin_verification, require_admin
from app.services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.get("/categories", response_model=ProjectCategoriesOut)
def get_project_metadata(service: ProjectService = Depends(get_project_service)):
    """
    Retrieve project metadata taxonomy:
    Statuses, Supported Link Types, and Technology Categories.
    """
    return service.get_categories()


@router.get("", response_model=List[ProjectOut])
def list_projects(
    include_hidden: bool = Query(False, description="Include private/draft projects (requires admin context)"),
    search: Optional[str] = Query(None, description="Search query across project name or description"),
    status: Optional[str] = Query(None, description="Filter by project status (e.g. Completed, In Progress)"),
    technology: Optional[str] = Query(None, description="Filter by technology used (e.g. Python, React)"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured flag"),
    sort_by: Optional[str] = Query("order", description="Sort by: 'order', 'name', 'updated', or 'start_date'"),
    service: ProjectService = Depends(get_project_service)
):
    """
    Retrieve project portfolio with deterministic ordering.
    Public view strictly excludes private projects and private deployment links without leaking unpublished data.
    """
    return service.list_projects(
        include_hidden=include_hidden,
        search=search,
        status=status,
        technology=technology,
        is_featured=is_featured,
        sort_by=sort_by or "order"
    )


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Create a new portfolio project with multiple deployment links and tech stack.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.create_project(project_data, current_user, client_ip)


# Reorder placed BEFORE /{project_id} to prevent path parameter collision
@router.patch("/reorder", response_model=List[ProjectOut], status_code=status.HTTP_200_OK)
def patch_reorder_projects(
    items: List[ProjectReorderItem],
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Reorder projects in bulk (PATCH convention).
    Executes transactionally and verifies all IDs.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.reorder_projects(items, current_user, client_ip)


@router.post("/reorder", response_model=List[ProjectOut], status_code=status.HTTP_200_OK)
def post_reorder_projects(
    items: List[ProjectReorderItem],
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """Reorder projects in bulk (POST convention for client compatibility)."""
    client_ip = request.client.host if request.client else "unknown"
    return service.reorder_projects(items, current_user, client_ip)


@router.post("/extract-github", response_model=GitHubExtractionResponse)
def extract_github_projects_endpoint(
    request_data: GitHubExtractionRequest,
    service: ProjectService = Depends(get_project_service)
):
    """
    Extract repositories, tech stacks, links, and synthesized AI dossiers from a GitHub URL or username.
    Supports user profile URLs (all public repos) or individual repository URLs.
    """
    return service.extract_from_github(
        github_url=request_data.github_url,
        custom_token=request_data.custom_token
    )


@router.post("/generate-ai-dossier", response_model=ProjectAiDossierGenerateResponse)
def generate_ai_dossier_endpoint(
    request_data: ProjectAiDossierGenerateRequest,
    current_user: User = Depends(require_admin),
    service: ProjectService = Depends(get_project_service)
):
    """
    Generate a massively big, advancedly detailed AI project dossier in super simple,
    jargon-free language using everyday physical analogies and zero condescending references.
    """
    return service.generate_project_ai_dossier(request_data)



@router.post("/bulk-import", response_model=List[ProjectOut], status_code=status.HTTP_201_CREATED)
def bulk_import_projects_endpoint(
    import_data: ProjectBulkImportRequest,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Bulk import extracted projects into portfolio transactionally with PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.bulk_import_projects(import_data.projects, current_user, client_ip)


@router.get("/github-link", response_model=Optional[GitHubAccountLinkOut])
def get_github_link_endpoint(
    current_user: User = Depends(require_admin),
    service: ProjectService = Depends(get_project_service)
):
    """Retrieve linked GitHub account configuration for the portfolio."""
    return service.get_github_link()


@router.post("/github-link", response_model=GitHubAccountLinkOut)
def save_github_link_endpoint(
    data: GitHubAccountLinkCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Link a GitHub account to automatically track repositories, tech stack changes,
    and generate synchronized AI project dossiers.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.save_github_link(data, current_user, client_ip)


@router.delete("/github-link", status_code=status.HTTP_200_OK)
def delete_github_link_endpoint(
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """Unlink the connected GitHub account."""
    client_ip = request.client.host if request.client else "unknown"
    return service.unlink_github_account(current_user, client_ip)


@router.post("/sync-github", response_model=GitHubSyncResultOut)
def sync_github_projects_endpoint(
    request: Request,
    github_url: Optional[str] = Query(None, description="Optional override repository or profile URL to sync"),
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Synchronize repositories with GitHub on-demand:
    - Adds newly created repositories to the portfolio.
    - Updates modified repositories, updating the tech stack (clearing removed tech) and re-synthesizing AI dossiers.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.sync_github_account(custom_url=github_url, current_user=current_user, client_ip=client_ip)


@router.post("/github-webhook", status_code=status.HTTP_200_OK)
async def github_webhook_endpoint(
    request: Request,
    service: ProjectService = Depends(get_project_service)
):
    """
    GitHub Webhook receiver for automatic real-time synchronization.
    Triggered when repositories are created, edited, pushed, or publicized.
    """
    event_type = request.headers.get("x-github-event") or request.headers.get("X-GitHub-Event") or "push"
    signature = request.headers.get("x-hub-signature-256") or request.headers.get("X-Hub-Signature-256")

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    try:
        raw_body = await request.body()
    except Exception:
        raw_body = json.dumps(payload).encode("utf-8") if payload else b""

    return service.handle_github_webhook(
        payload=payload,
        event_type=event_type,
        signature=signature,
        raw_body=raw_body
    )





@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    include_hidden: bool = Query(False, description="Allow retrieving hidden project if admin"),
    service: ProjectService = Depends(get_project_service)
):
    """Retrieve a single project by ID with nested technologies and links."""
    return service.get_project(project_id, include_hidden=include_hidden)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Full update of an existing project.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.update_project(project_id, project_data, current_user, client_ip)


@router.patch("/{project_id}", response_model=ProjectOut)
def patch_project(
    project_id: int,
    project_data: ProjectPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Partial update of an existing project.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_project(project_id, project_data, current_user, client_ip)


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Delete a project safely.
    Requires administrative authentication and PIN verification.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_project(project_id, current_user, client_ip)


# -----------------------------------------------------------------------------
# Dedicated Project Link Endpoints
# -----------------------------------------------------------------------------

@router.post("/{project_id}/links", response_model=ProjectLinkOut, status_code=status.HTTP_201_CREATED)
def add_project_link(
    project_id: int,
    link_data: ProjectLinkCreate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """
    Add a deployment/demo link to a project.
    Supports multiple links per project and maintains primary link integrity.
    """
    client_ip = request.client.host if request.client else "unknown"
    return service.add_project_link(project_id, link_data, current_user, client_ip)


@router.patch("/{project_id}/links/reorder", response_model=List[ProjectLinkOut])
def patch_reorder_project_links(
    project_id: int,
    items: List[ProjectLinkReorderItem],
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """Reorder project links in bulk (PATCH convention)."""
    client_ip = request.client.host if request.client else "unknown"
    return service.reorder_project_links(project_id, items, current_user, client_ip)


@router.post("/{project_id}/links/reorder", response_model=List[ProjectLinkOut])
def post_reorder_project_links(
    project_id: int,
    items: List[ProjectLinkReorderItem],
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """Reorder project links in bulk (POST convention for client compatibility)."""
    client_ip = request.client.host if request.client else "unknown"
    return service.reorder_project_links(project_id, items, current_user, client_ip)


@router.put("/{project_id}/links/{link_id}", response_model=ProjectLinkOut)
def update_project_link(
    project_id: int,
    link_id: int,
    link_data: ProjectLinkUpdate,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """Update an existing deployment link."""
    client_ip = request.client.host if request.client else "unknown"
    return service.update_project_link(project_id, link_id, link_data, current_user, client_ip)


@router.patch("/{project_id}/links/{link_id}", response_model=ProjectLinkOut)
def patch_project_link(
    project_id: int,
    link_id: int,
    link_data: ProjectLinkPatch,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """Partially update an existing deployment link."""
    client_ip = request.client.host if request.client else "unknown"
    return service.patch_project_link(project_id, link_id, link_data, current_user, client_ip)


@router.delete("/{project_id}/links/{link_id}", status_code=status.HTTP_200_OK)
def delete_project_link(
    project_id: int,
    link_id: int,
    request: Request,
    current_user: User = Depends(require_pin_verification),
    service: ProjectService = Depends(get_project_service)
):
    """Delete a deployment link from a project."""
    client_ip = request.client.host if request.client else "unknown"
    return service.delete_project_link(project_id, link_id, current_user, client_ip)
