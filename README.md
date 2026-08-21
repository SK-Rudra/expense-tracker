# Expense Tracker

[![Automated tests](https://github.com/SK-Rudra/expense-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/SK-Rudra/expense-tracker/actions/workflows/tests.yml)

A full-stack expense management web application built with Python and Flask.

This project was created to practise the complete software-development lifecycle, including frontend development, backend development, database management, automated testing, version control, continuous integration, deployment and maintenance.

## Live Application

[Open Expense Tracker](https://sk-rudra-expense-tracker.onrender.com)

The free Render service may take approximately one minute to start after a period of inactivity.

## Features

- Secure user registration, login and logout
- Password hashing using Werkzeug
- Remember-me login sessions
- CSRF-protected forms
- User-specific income and expense records
- Transaction creation, viewing, editing and deletion
- Custom income and expense categories
- Default categories for newly registered users
- Monthly income, expense and balance calculations
- Recent transaction dashboard
- Responsive frontend design
- Secure user-data ownership checks
- Database schema migrations
- Automated tests and coverage checks
- GitHub Actions continuous integration
- Automatic deployment after tests pass

## Technology Stack

### Backend

- Python 3.14
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Flask-Migrate
- Alembic
- Flask-Login
- Flask-WTF
- WTForms
- Gunicorn
- Psycopg 3

### Frontend

- HTML
- CSS
- Jinja templates

### Databases

- SQLite for local development
- Neon PostgreSQL for production

### Testing and Deployment

- pytest
- Coverage.py
- GitHub Actions
- Render
- GitHub

## Project Structure

```text
expense-tracker/
├── .github/
│   └── workflows/
│       └── tests.yml
├── app/
│   ├── auth/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── transactions/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   └── routes.py
├── migrations/
├── tests/
├── .coveragerc
├── .env.example
├── .gitignore
├── .python-version
├── config.py
├── render.yaml
├── requirements-dev.txt
├── requirements.txt
└── run.py
```

## Running Locally

### 1. Clone the repository

```powershell
git clone https://github.com/SK-Rudra/expense-tracker.git
cd expense-tracker
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

Activate it in Windows Command Prompt:

```text
.venv\Scripts\activate
```

### 3. Install development dependencies

```powershell
python -m pip install -r requirements-dev.txt
```

### 4. Apply database migrations

```powershell
python -m flask --app run.py db upgrade
```

### 5. Start the development server

```powershell
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

The local application uses SQLite by default.

## Environment Variables

Production uses the following environment variables:

| Variable | Purpose |
|---|---|
| `APP_ENV` | Enables production configuration |
| `SECRET_KEY` | Secures sessions and CSRF tokens |
| `DATABASE_URL` | PostgreSQL connection string |

Never commit real secret keys or database connection strings.

See `.env.example` for safe example values.

## Database Migrations

Create a migration after changing a database model:

```powershell
python -m flask --app run.py db migrate -m "Describe the schema change"
```

Apply migrations:

```powershell
python -m flask --app run.py db upgrade
```

Check for model changes that do not have a migration:

```powershell
python -m flask --app run.py db check
```

## Automated Tests

Run all tests:

```powershell
python -m pytest -v
```

Run tests with coverage:

```powershell
python -m coverage erase
python -m coverage run -m pytest
python -m coverage report
```

The project currently requires at least 85% application-code coverage.

## Continuous Integration

GitHub Actions automatically performs the following checks for pushes and pull requests:

1. Sets up Python.
2. Installs development dependencies.
3. Checks dependency compatibility.
4. Runs all automated tests.
5. Enforces the minimum coverage requirement.

Render deploys changes from `main` only after the GitHub checks pass.

## Production Deployment

The production application uses:

- Render for Flask and Gunicorn
- Neon for persistent PostgreSQL storage
- GitHub Actions as the deployment quality gate
- HTTPS and secure production cookies
- Alembic migrations during application startup

Deployment settings are stored safely in `render.yaml`. Secret values are configured directly in Render and are not stored in GitHub.

## Future Improvements

- Transaction searching and filtering
- Date and category filters
- Pagination
- Spending charts
- Monthly budgets
- CSV export
- Password reset
- Email verification