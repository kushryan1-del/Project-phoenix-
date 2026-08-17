# Project Phoenix — RHI App v0.1

A responsive operating-system foundation for **Remarkable Home Improvement** (PA151285).

## What works now
- Dashboard
- Customer creation/register
- Lead creation/register
- Project creation/register/detail
- Automatic Phoenix IDs
- Estimate Studio
- Corrected 30% / 35% / 40% gross-margin pricing
- 6% Pennsylvania material sales tax input rule
- Mobile responsive layout

## Run locally
Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

The SQLite database is created automatically at `data/phoenix.db` and is excluded from Git.

## Important
This is the **foundation build**, not the finished production release. It intentionally leaves document generation, photos/file storage, field time tracking, scheduling, authentication, cloud database, backups and production deployment for the next milestones.
