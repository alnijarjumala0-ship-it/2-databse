"""Web UI views and dashboard routes."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(tags=["UI"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard UI at root domain."""
    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request,
        "app_name": "FastAPI MVC",
        "version": "1.0.0",
    })


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page."""
    return templates.TemplateResponse(request, "login.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page."""
    return templates.TemplateResponse(request, "register.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Serve the user profile page (auth handled client-side via JS)."""
    return templates.TemplateResponse(request, "profile.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Serve the admin dashboard page (auth handled client-side via JS)."""
    return templates.TemplateResponse(request, "admin.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/admin/register", response_class=HTMLResponse)
async def admin_register_page(request: Request):
    """Serve the admin registration page."""
    return templates.TemplateResponse(request, "admin_register.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Serve the about page."""
    return templates.TemplateResponse(request, "about.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Serve the contact page."""
    return templates.TemplateResponse(request, "contact.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    """Serve the products page."""
    return templates.TemplateResponse(request, "products.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    """Serve the users management page (auth handled client-side via JS)."""
    return templates.TemplateResponse(request, "users.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    """Serve the activity logs page (auth handled client-side via JS)."""
    return templates.TemplateResponse(request, "logs.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Serve the settings page (auth handled client-side via JS)."""
    return templates.TemplateResponse(request, "settings.html", {
        "request": request,
        "app_name": "FastAPI MVC",
    })
