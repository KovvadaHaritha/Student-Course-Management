# Student Course Management

## Features

- Demo login and sign-up with required-field and email validation. No password is requested, stored, or sent to a service.
- Dashboard navigation to courses, assignments, fees, and profile pages.
- Existing Web Development lessons for HTML, CSS and responsive design, JavaScript basics, and modern website development.
- Structured Web Development course with 4 modules and 4 guided lessons.
- Structured Python Programming course with 12 modules and 24 guided lessons.
- Structured UI/UX Design course with 12 modules and 24 guided lessons.
- Structured Data Science course with 14 modules and 28 guided lessons.
- Each guided lesson includes learning objectives, an explanation, teaching steps, a real-world example, a practical example, an exercise, and a graded quiz with explanations.
- Course overview pages include level, estimated duration, prerequisites, expandable modules, a final assessment, capstone project, documentation, and video-channel references.
- Guided-course lesson progress and final-assessment attempts are stored in SQLite. A stable anonymous browser ID separates progress between browser profiles; the demo login is not an authenticated account.
- Existing Web Development lesson completions saved in browser `localStorage` are migrated into the guided-course progress record when the course is opened.
- Assignment submission, profile edits, and demo fee status continue to use browser `localStorage`.
- Simulated payment only. The site does not collect payment details or process real payments.
- Shared responsive styling and behavior across the pages.

## Technologies

- HTML
- CSS
- Vanilla JavaScript
- Flask and SQLite for the guided-course API and persistent progress
- Browser `localStorage` for existing demo portal state and anonymous learner ID

Install dependencies from `requirements.txt` before starting the Flask application.

## Run Locally

From the project directory, install dependencies and start Flask:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. The first app startup initializes the SQLite schema and seeds the guided-course lessons. Do not open the course pages with `file://`; the guided-course pages require the Flask API.

The guided course routes are `/courses/web-development`, `/courses/python-programming`, `/courses/ui-ux-design`, and `/courses/data-science`. The previous `.html` course overview URLs redirect to their new overviews. Existing Web Development lesson pages remain available.

## Render Deployment (Demo)

This project can be deployed to Render for demonstration, but it is **not ready for real student accounts, enrollment records, or real payments**:

- Sign-in and sign-up create an anonymous demo session; they do not authenticate an account. The `users` and `enrollments` schema tables are not backed by production account/enrollment routes.
- Payment is simulation-only. No payment gateway or verified payment webhook is configured. A demo receipt is not evidence of a real payment.
- Before storing real student data or accepting money, implement authenticated accounts and authorization, integrate a payment provider with server-side verification, and migrate to a managed PostgreSQL database.

### Render service settings

Create a Python web service and set:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `flask --app app init-db && gunicorn --bind 0.0.0.0:$PORT app:app`

The explicit initialization command is needed because Gunicorn imports `app:app` and does not execute the `if __name__ == "__main__"` block. `init-db` creates missing tables and seeds missing course/assessment rows using the existing idempotent schema. It does not delete the database or perform schema migrations. Back up existing data before deployment and before any future schema changes.

Configure these Render environment variables:

| Variable | Value |
|---|---|
| `STUDENT_COURSE_ENV` | `production` |
| `STUDENT_COURSE_SECRET_KEY` | A newly generated, private random value; never commit it |
| `STUDENT_COURSE_SECURE_COOKIE` | `1` |
| `STUDENT_COURSE_DB` | `/var/data/student-course.sqlite3` when using a persistent disk |
| `DEMO_PAYMENTS_ENABLED` | `1` to expose the clearly labeled demo flow, or `0` to disable it |

Generate a secret locally with `python -c "import secrets; print(secrets.token_urlsafe(48))"` and enter the output directly in Render's environment settings. Do not put the generated value in source control or this README.

The default SQLite file is `instance/student-course.sqlite3`; Render's ordinary service filesystem is not a durable database location. If keeping SQLite for a demo, attach persistent storage mounted at `/var/data`, set the database path above, use one web-service instance, and arrange regular off-service backups with restore checks. A persistent disk is still a single-instance SQLite setup, not a suitable multi-instance production database. Managed PostgreSQL is recommended for real accounts, payments, and enrollments; migrating the existing SQLite database requires a separate, backed-up migration plan.

The app requires `STUDENT_COURSE_SECRET_KEY` when `STUDENT_COURSE_ENV=production`, forces secure session cookies in production, and disables Flask debug mode in production. For local development, the secret-file fallback remains available; debug mode can be explicitly enabled with `FLASK_DEBUG=1`.

## Guided Course Structure

| Course | Modules | Lessons | Capstone |
|---|---:|---:|---|
| Web Development | 4 | 4 | Responsive Learning Portal |
| Python Programming | 12 | 24 | Student Management System |
| UI/UX Design | 12 | 24 | Student Learning Dashboard |
| Data Science | 14 | 28 | Student Performance Analysis and Sales Prediction |

Module sequence:

- **Web Development:** HTML foundations and accessible structure; CSS, layouts, responsive design and accessibility; JavaScript and browser behavior; modern websites, testing, performance and deployment.
- **Python Programming:** Introduction and installation; variables and data types; conditionals; loops; strings and collections; functions and recursion; modules and exceptions; object-oriented programming; text, CSV, and JSON files; NumPy and Pandas; Matplotlib visualization; practical projects.
- **UI/UX Design:** UI, UX, and design process; UX research; user journeys and flows; information architecture; wireframing; Figma basics; visual design principles; design systems; interactive prototyping; usability testing; responsive design; portfolio projects.
- **Data Science:** Introduction and applications; mathematics, statistics, and probability; Python fundamentals; NumPy; Pandas; data collection and imports; data cleaning; exploratory analysis; visualization; SQL; machine learning; model evaluation; analytics types; practical projects.

Course resources unlock only when all required lessons in that course are marked complete. Final assessments are graded by Flask and require at least 70% to pass. Lesson completion and assessment results are independent; passing the assessment does not mark lessons complete.

## Testing Performed

Run the focused automated course tests with:

```powershell
python -m unittest discover -s tests -v
```

The tests cover all guided lesson routes, quiz and final-assessment grading, SQLite progress persistence, completion gating, and existing portal routes. Browser-based layout checks are not a substitute for testing on physical devices or a cross-browser test matrix.
