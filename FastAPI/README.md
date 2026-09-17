# FastAPI MVC Backend

A complete FastAPI backend project following strict MVC architecture with dual database support (PostgreSQL + MongoDB), JWT authentication, and SQLAdmin dashboard UI.

## Features

- **Architecture**: MVC (Models, Views, Controllers/Routers)
- **Databases**: PostgreSQL (SQLAlchemy) + MongoDB (Motor/PyPyo)
- **Admin Dashboard**: SQLAdmin for visual CRUD operations
- **JWT Authentication**: Secure token-based auth with refresh tokens
- **20+ API Routes**: Grouped across Auth, User, Product, and Mongo Log controllers

## Project Structure

```
app/
├── controllers/       # API Route logic
├── models/            # SQLAlchemy & Pydantic models
├── views/             # Admin Dashboard UI (SQLAdmin)
├── core/              # Security, Configs, DB connections
├── schemas.py         # Pydantic schemas
main.py               # Application entry point
.env                  # Environment variables
.env.example          # Environment template
.gitignore            # Git ignore rules
requirements.txt      # Python dependencies
run.py                # Startup script
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the server**:
   ```bash
   python run.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access**:
   - API Docs: http://localhost:8000/docs
   - Admin Dashboard: http://localhost:8000/admin
   - Health Check: http://localhost:8000/health

## API Routes

### Auth Controller (5 routes)
- POST /auth/register - Register new user
- POST /auth/login - User login
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Logout
- GET /auth/profile - Get current user profile

### User Controller (5 routes)
- GET /users/all - Get all users (Admin)
- GET /users/{id} - Get user by ID (Admin)
- PUT /users/{id} - Update user (Admin)
- DELETE /users/{id} - Delete user (Admin)
- PATCH /users/{id}/toggle-admin - Toggle admin status (Admin)

### Product Controller (5 routes)
- GET /products/list - List all products
- POST /products/create - Create product
- GET /products/{id} - Get product details
- PUT /products/{id} - Update product
- DELETE /products/{id} - Delete product

### Mongo Log Controller (5 routes)
- POST /logs/create - Create activity log (Admin)
- GET /logs/view - View logs with filters (Admin)
- GET /logs/filter/user/{user_id} - Filter logs by user (Admin)
- GET /logs/health - MongoDB health check (Admin)
- DELETE /logs/clear-old - Clear old logs (Admin)

## Deployment

### Git Setup
```bash
git add .
git commit -m "Initial commit: FastAPI MVC backend"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Docker Compose (Optional)
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
  web:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
      - mongo
```

## Security Notes

- Store all secrets in `.env` file (never commit this file)
- Change `SECRET_KEY` in production
- Use HTTPS in production
- Validate all user inputs