# Task Manager Monorepo

A full-stack Task Management application built with a **Next.js** frontend, a **Flask** REST API backend, and **Supabase** (PostgreSQL + Auth + RLS).

---

## 📁 Repository Structure

```text
TASKMANGER/
├── migrations/
│   └── 001_initial_schema.sql       # PostgreSQL schema, triggers, and RLS policies
├── taskmanager-backend/             # Flask REST API backend
│   ├── routes/                      # API endpoint blueprints
│   │   ├── __init__.py
│   │   └── tasks.py                 # Task management & user routes (/api/tasks, /api/users)
│   ├── utils/                       # Backend utilities
│   │   ├── auth.py                  # JWT authentication decorator via Supabase JWKS
│   │   ├── email.py                 # Gmail SMTP email notifications
│   │   └── supabase_client.py       # Supabase service role client
│   ├── app.py                       # Flask entry point & CORS configuration
│   ├── requirements.txt             # Python backend dependencies
│   └── .env.example                 # Backend environment variable template
├── taskmanager-frontend/            # Next.js (TypeScript + Tailwind CSS) frontend
│   ├── src/
│   │   ├── app/                     # Next.js App Router pages & API routes
│   │   ├── components/              # Shared UI components
│   │   └── utils/                   # Frontend API fetcher & Supabase client helpers
│   ├── package.json                 # Node.js dependencies
│   └── .env.example                 # Frontend environment variable template
├── requirements.txt                 # Monorepo root requirements file
└── README.md                        # Project documentation
```

---

## 🗄️ Database Schema & RLS Policies

The database is powered by Supabase PostgreSQL. Schema definition can be found in `migrations/001_initial_schema.sql`.

### Tables

1. **`profiles`**
   - Linked to `auth.users(id)` with cascading deletion.
   - Stores `id`, `email`, `full_name`, `avatar_url`, `created_at`.
   - **Automated Trigger**: `on_auth_user_created` runs `handle_new_user()` to populate `profiles` automatically upon Google OAuth or email sign-up.

2. **`tasks`**
   - Enum `task_status`: `'todo'`, `'in_progress'`, `'done'`.
   - Columns: `id` (UUID), `title`, `description`, `status`, `created_by` (FK -> `profiles.id`), `assigned_to` (FK -> `profiles.id`), `created_at`, `completed_at`.

### Row Level Security (RLS)

- **Profiles Policy**: Viewable by any authenticated user (used for user selection in task assignment).
- **Tasks Select Policy**: Users can view tasks where `auth.uid() == created_by` OR `auth.uid() == assigned_to`.
- **Tasks Insert Policy**: Authenticated users can insert tasks setting `auth.uid() == created_by`.
- **Tasks Update Policy**: Both the **task creator** (`created_by`) and the **assignee** (`assigned_to`) can update task details or status.

---

## ⚙️ Environment Variables

### Backend (`taskmanager-backend/.env`)

| Variable Name | Description |
| --- | --- |
| `SUPABASE_URL` | Base URL for your Supabase project (e.g. `https://xxx.supabase.co`). *(Fallback: `SUPABASE_PROJECT_URL`)* |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for admin-level database operations |
| `EMAIL_ADDRESS` | Sender Gmail address for notification emails |
| `EMAIL_APP_PASSWORD` | App Password for Gmail SMTP authentication |

### Frontend (`taskmanager-frontend/.env.local`)

| Variable Name | Description |
| --- | --- |
| `NEXT_PUBLIC_SUPABASE_URL` | Public Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public Supabase anonymous API key |
| `NEXT_PUBLIC_API_URL` | URL of the Flask backend API (default: `http://localhost:5000`) |

---

## 🌐 Allowed CORS Origins

Configured in `taskmanager-backend/app.py`:
- `http://localhost:3000` (Frontend origin)


---

## 🚀 API Endpoints & Behavior

All `/api/*` endpoints require a valid Supabase JWT sent in the `Authorization: Bearer <token>` header. JWT verification is performed dynamically using Supabase's JWKS endpoint (`/auth/v1/.well-known/jwks.json`) supporting `ES256` and `RS256` algorithms.

| Method | Endpoint | Auth Required | Description & Behavior |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Health check returning `{"status": "ok"}` |
| `GET` | `/api/tasks` | Yes | Retrieves tasks where current user is creator or assignee |
| `GET` | `/api/users` | Yes | Retrieves profile list (`id`, `email`, `full_name`) for assignment |
| `POST` | `/api/tasks` | Yes | Creates task. Automatically sends assignment email to the **assignee** if `assigned_to` is provided. |
| `PATCH` | `/api/tasks/<task_id>` | Yes | Updates task. Allowed for task **creator** or **assignee**. Sets `completed_at` when status becomes `done`. Sends completion email to **task creator**. |

### 📧 Email Notification Logic

- **Task Assignment Email**: When a task is created with an `assigned_to` profile, an email is sent to the **assignee's email address**.
- **Task Completion Email**: When a task's status is changed to `done`, an email notification is sent to the **task creator's email address** (`created_by`).

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Supabase Project with `migrations/001_initial_schema.sql` applied

### 2. Backend Setup (`taskmanager-backend`)

```bash
# Navigate to backend directory
cd taskmanager-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template & populate real credentials
cp .env.example .env

# Start Flask dev server (runs on http://localhost:5000)
python app.py
```

### 3. Frontend Setup (`taskmanager-frontend`)

```bash
# Navigate to frontend directory
cd taskmanager-frontend

# Install dependencies
npm install

# Copy environment template & populate real credentials
cp .env.example .env.local

# Start Next.js dev server (runs on http://localhost:3000)
npm run dev
```

---

## 📄 License

This repository is submitted as a take-home assignment.
