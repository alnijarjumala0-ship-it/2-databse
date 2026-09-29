"""Web UI views - admin dashboard only (single-admin system)."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(tags=["UI"])


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard_root(request: Request):
    """Serve the admin dashboard (with login overlay) at root domain."""
    return templates.TemplateResponse(request, "admin.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


# --- Everything else redirects to the single admin dashboard ---
@router.get("/users", include_in_schema=False)
async def users_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/products", include_in_schema=False)
async def products_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/logs", include_in_schema=False)
async def logs_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/settings", include_in_schema=False)
async def settings_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/login", include_in_schema=False)
async def login_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/register", include_in_schema=False)
async def register_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/profile", include_in_schema=False)
async def profile_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/about", include_in_schema=False)
async def about_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/contact", include_in_schema=False)
async def contact_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/dashboard", include_in_schema=False)
async def dashboard_removed():
    return RedirectResponse(url="/", status_code=302)


@router.get("/admin/register", include_in_schema=False)
async def admin_register_removed():
    return RedirectResponse(url="/", status_code=302)
