from datetime import date, datetime, timedelta, timezone
from io import BytesIO
import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import secrets
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, send_from_directory, session, url_for

from assessment_catalog import ASSESSMENTS
from course_catalog import COURSES, iter_course_lessons


PROJECT_DIR = Path(__file__).resolve().parent
IS_PRODUCTION = os.environ.get("STUDENT_COURSE_ENV", "").strip().lower() == "production"
DATABASE_SETTING = os.environ.get("STUDENT_COURSE_DB")
DATABASE_PATH = Path(DATABASE_SETTING) if DATABASE_SETTING else PROJECT_DIR / "instance" / "student-course.sqlite3"
if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = PROJECT_DIR / DATABASE_PATH

PUBLIC_FILES = {
    "assignments.html",
    "courses.html",
    "dashboard.html",
    "fees.html",
    "html-fundamentals.html",
    "html-lesson.html",
    "index.html",
    "payment-success.html",
    "profile.html",
    "python-programming.html",
    "script.js",
    "signup.html",
    "style.css",
    "ui-ux-design.html",
    "data-science.html",
    "web-development.html",
    "web-learning.html",
}

configured_secret_key = os.environ.get("STUDENT_COURSE_SECRET_KEY", "").strip()
if IS_PRODUCTION and not configured_secret_key:
    raise RuntimeError(
        "STUDENT_COURSE_SECRET_KEY must be configured when STUDENT_COURSE_ENV=production."
    )

app = Flask(__name__)
app.template_folder = str(PROJECT_DIR)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=(
        IS_PRODUCTION or os.environ.get("STUDENT_COURSE_SECURE_COOKIE") == "1"
    ),
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
)


def _load_session_secret():
    secret_path = PROJECT_DIR / "instance" / ".session-secret"
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        return secret_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        secret = secrets.token_urlsafe(48)
        try:
            with secret_path.open("x", encoding="utf-8") as secret_file:
                secret_file.write(secret)
        except FileExistsError:
            return secret_path.read_text(encoding="utf-8").strip()
        return secret


app.secret_key = configured_secret_key or _load_session_secret()


def get_session_learner_id():
    learner_id = session.get("learner_id")
    try:
        learner_id = str(uuid.UUID(learner_id))
    except (AttributeError, TypeError, ValueError):
        learner_id = str(uuid.uuid4())
        session["learner_id"] = learner_id
    session.permanent = True
    return learner_id


@app.before_request
def ensure_demo_learner_session():
    get_session_learner_id()


def connect_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    schema = (PROJECT_DIR / "schema.sql").read_text(encoding="utf-8")
    with closing(connect_database()) as connection:
        connection.executescript(schema)
        for course_slug, course in COURSES.items():
            course_id = connection.execute(
                "SELECT id FROM courses WHERE slug = ?", (course_slug,)
            ).fetchone()["id"]
            for position, lesson in enumerate(iter_course_lessons(course_slug), start=1):
                connection.execute(
                    """
                    INSERT OR IGNORE INTO lessons (course_id, slug, title, position)
                    VALUES (?, ?, ?, ?)
                    """,
                    (course_id, lesson["slug"], lesson["title"], position),
                )
            lesson_slugs = [
                lesson["slug"] for lesson in iter_course_lessons(course_slug)
            ]
            for position, assessment in enumerate(ASSESSMENTS[course_slug], start=1):
                lesson_position = assessment["lesson_position"]
                lesson_slug = (
                    lesson_slugs[lesson_position - 1]
                    if 1 <= lesson_position <= len(lesson_slugs)
                    else None
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO assessments
                        (course_slug, slug, title, description, assessment_type,
                         lesson_slug, objectives_json, instructions, maximum_marks,
                         passing_marks, time_limit_minutes, attempt_limit, deadline,
                         rubric_json, position)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        course_slug, assessment["slug"], assessment["title"],
                        assessment["description"], assessment["assessment_type"],
                        lesson_slug, json.dumps(assessment["objectives"]),
                        assessment["instructions"], assessment["maximum_marks"],
                        assessment["passing_marks"], assessment["time_limit_minutes"],
                        assessment["attempt_limit"], assessment["deadline"],
                        json.dumps(assessment["rubric"]), position,
                    ),
                )
                assessment_id = connection.execute(
                    "SELECT id FROM assessments WHERE course_slug = ? AND slug = ?",
                    (course_slug, assessment["slug"]),
                ).fetchone()["id"]
                for question_position, item in enumerate(assessment["questions"], start=1):
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO assessment_questions
                            (assessment_id, position, prompt, options_json,
                             correct_option, explanation, marks)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            assessment_id, question_position, item["prompt"],
                            json.dumps(item["options"]), item["correct"],
                            item["explanation"], item["marks"],
                        ),
                    )
        connection.commit()


def get_course(course_slug):
    course = COURSES.get(course_slug)
    if course is None:
        abort(404)
    return course


def get_learner_id(value, *, required):
    if not value:
        if required:
            abort(400, description="A learner_id is required.")
        return get_session_learner_id()
    try:
        learner_id = str(uuid.UUID(value))
    except (AttributeError, TypeError, ValueError):
        abort(400, description="learner_id must be a valid UUID.")
    if learner_id != get_session_learner_id():
        abort(403, description="This learner record is not available in the current browser session.")
    return learner_id


def request_json_object():
    payload = request.get_json()
    if not isinstance(payload, dict):
        abort(400, description="A JSON object is required.")
    return payload


def get_completed_lessons(course_slug, learner_id):
    if not learner_id:
        return set()
    with closing(connect_database()) as connection:
        rows = connection.execute(
            """
            SELECT lessons.slug
            FROM browser_lesson_progress
            JOIN lessons ON lessons.id = browser_lesson_progress.lesson_id
            JOIN courses ON courses.id = lessons.course_id
            WHERE browser_lesson_progress.learner_id = ?
              AND courses.slug = ?
            """,
            (learner_id, course_slug),
        ).fetchall()
    return {row["slug"] for row in rows}


def get_course_progress(course_slug, learner_id):
    lessons = list(iter_course_lessons(course_slug))
    completed = get_completed_lessons(course_slug, learner_id)
    completed_count = sum(lesson["slug"] in completed for lesson in lessons)
    total = len(lessons)
    return {
        "completed": completed,
        "completed_count": completed_count,
        "total": total,
        "percent": round(completed_count * 100 / total) if total else 0,
        "is_complete": total > 0 and completed_count == total,
    }


def get_course_modules(course_slug):
    modules = []
    for module_index, module in enumerate(COURSES[course_slug]["modules"], start=1):
        module_lessons = [
            lesson for lesson in iter_course_lessons(course_slug)
            if lesson["module_index"] == module_index
        ]
        modules.append({"title": module["title"], "lessons": module_lessons})
    return modules


def latest_assessment(course_slug, learner_id):
    if not learner_id:
        return None
    with closing(connect_database()) as connection:
        row = connection.execute(
            """
            SELECT score, question_count, passed, attempted_at
            FROM course_assessment_attempts
            WHERE learner_id = ? AND course_slug = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (learner_id, course_slug),
        ).fetchone()
    return dict(row) if row else None


@app.cli.command("init-db")
def init_db_command():
    """Create the database tables and seed the existing courses and lessons."""
    initialize_database()
    print(f"Database initialized at {DATABASE_PATH}")


@app.get("/api/session")
def learner_session():
    return jsonify({
        "learner_id": get_session_learner_id(),
        "demo_account": True,
        "authenticated": False,
    })


@app.post("/api/demo-session")
def start_demo_session():
    payload = request_json_object()
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    if not email or len(email) > 254 or "@" not in email:
        abort(400, description="Enter a valid email address for this demo session.")
    if name and len(name) > 120:
        abort(400, description="Name must be 120 characters or fewer.")
    session["demo_email"] = email
    if name:
        session["demo_name"] = name
    return jsonify({
        "learner_id": get_session_learner_id(),
        "demo_account": True,
        "message": "Demo session ready. This is not authenticated account access.",
    })


def demo_payments_enabled():
    return os.environ.get("DEMO_PAYMENTS_ENABLED", "1").strip().lower() in {"1", "true", "yes"}


def ensure_fee_account(connection, learner_id):
    total_rupees = int(os.environ.get("COURSE_FEE_RUPEES", "25000"))
    due_days = int(os.environ.get("COURSE_FEE_DUE_DAYS", "30"))
    if total_rupees < 0 or due_days < 0:
        raise ValueError("Fee configuration must be non-negative.")
    due_date = (date.today() + timedelta(days=due_days)).isoformat()
    connection.execute(
        """
        INSERT OR IGNORE INTO fee_accounts (learner_id, total_paise, due_date)
        VALUES (?, ?, ?)
        """,
        (learner_id, total_rupees * 100, due_date),
    )


def payment_record(connection, payment_id, learner_id):
    row = connection.execute(
        """
        SELECT payments.id, payments.amount_paise, payments.status,
               payments.transaction_reference, payments.created_at,
               payment_receipts.receipt_reference
        FROM payments
        LEFT JOIN payment_receipts ON payment_receipts.payment_id = payments.id
        WHERE payments.id = ? AND payments.learner_id = ?
        """,
        (payment_id, learner_id),
    ).fetchone()
    return dict(row) if row else None


@app.get("/fees.html")
def fees_page():
    return render_template("fees.html")


@app.get("/api/fees")
def fee_summary():
    learner_id = get_session_learner_id()
    with closing(connect_database()) as connection:
        ensure_fee_account(connection, learner_id)
        connection.commit()
        account = connection.execute(
            "SELECT total_paise, due_date FROM fee_accounts WHERE learner_id = ?",
            (learner_id,),
        ).fetchone()
        paid_paise = connection.execute(
            "SELECT COALESCE(SUM(amount_paise), 0) FROM payments WHERE learner_id = ? AND status = 'paid'",
            (learner_id,),
        ).fetchone()[0]
        history = connection.execute(
            """
            SELECT payments.id, payments.amount_paise, payments.status,
                   payments.transaction_reference, payments.created_at,
                   payment_receipts.receipt_reference
            FROM payments
            LEFT JOIN payment_receipts ON payment_receipts.payment_id = payments.id
            WHERE payments.learner_id = ?
            ORDER BY payments.id DESC
            """,
            (learner_id,),
        ).fetchall()
    total_paise = account["total_paise"]
    return jsonify({
        "currency": "INR",
        "total_paise": total_paise,
        "paid_paise": paid_paise,
        "pending_paise": max(0, total_paise - paid_paise),
        "due_date": account["due_date"],
        "status": "paid" if total_paise <= paid_paise else "pending",
        "payment_methods": ["demo"] if demo_payments_enabled() else [],
        "demo_notice": "DEMO — NO REAL MONEY IS CHARGED.",
        "real_payments_enabled": False,
        "history": [dict(row) for row in history],
    })


@app.post("/api/payments")
def initiate_payment():
    if not demo_payments_enabled():
        return jsonify({"error": "Demo payments are disabled; no real payment gateway is configured."}), 503
    result_setting = os.environ.get("DEMO_PAYMENT_RESULT", "success").strip().lower()
    allowed_results = {"success", "failed", "pending", "cancelled"}
    if result_setting not in allowed_results:
        app.logger.error("Invalid DEMO_PAYMENT_RESULT configuration: %s", result_setting)
        return jsonify({"error": "Payment demo is unavailable because its outcome configuration is invalid."}), 503

    payload = request_json_object()
    method = payload.get("method")
    idempotency_key = payload.get("idempotency_key")
    if method != "demo":
        abort(400, description="Select an available payment method.")
    try:
        idempotency_key = str(uuid.UUID(idempotency_key))
    except (AttributeError, TypeError, ValueError):
        abort(400, description="A valid payment request key is required.")

    learner_id = get_session_learner_id()
    with closing(connect_database()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        ensure_fee_account(connection, learner_id)
        existing = connection.execute(
            "SELECT id, status FROM payments WHERE learner_id = ? AND idempotency_key = ?",
            (learner_id, idempotency_key),
        ).fetchone()
        if existing:
            result = payment_record(connection, existing["id"], learner_id)
            connection.commit()
            return jsonify({
                "payment": result,
                "reused": True,
                "demo": True,
                "message": "This request was already processed; it was not charged again.",
            })

        pending_row = connection.execute(
            """
            SELECT COALESCE(SUM(amount_paise), 0) FROM payments
            WHERE learner_id = ? AND status = 'paid'
            """,
            (learner_id,),
        ).fetchone()
        paid_paise = pending_row[0]
        account = connection.execute(
            "SELECT total_paise FROM fee_accounts WHERE learner_id = ?",
            (learner_id,),
        ).fetchone()
        remaining_paise = max(0, account["total_paise"] - paid_paise)
        if remaining_paise == 0:
            connection.rollback()
            return jsonify({"error": "No fee balance is due."}), 409
        in_flight = connection.execute(
            "SELECT id FROM payments WHERE learner_id = ? AND status = 'pending' LIMIT 1",
            (learner_id,),
        ).fetchone()
        if in_flight:
            connection.rollback()
            return jsonify({"error": "A payment is already pending. Check its status before trying again."}), 409

        transaction_reference = f"DEMO-{uuid.uuid4().hex[:16].upper()}"
        student_name = str(session.get("demo_name") or "Student").strip() or "Student"
        student_id = session.get("student_id") or learner_id[:8].upper()
        course_name = str(payload.get("course_name") or "Student Course Management").strip() or "Student Course Management"
        semester = str(payload.get("semester") or "Semester 1").strip() or "Semester 1"
        cursor = connection.execute(
            """
            INSERT INTO payments
                (learner_id, amount_paise, method, status, idempotency_key, transaction_reference,
                 student_name, student_id, course_name, semester, payment_date)
            VALUES (?, ?, 'demo', 'pending', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                learner_id, remaining_paise, idempotency_key, transaction_reference,
                student_name, student_id, course_name, semester, date.today().isoformat(),
            ),
        )
        payment_id = cursor.lastrowid
        status = {
            "success": "paid",
            "failed": "failed",
            "pending": "pending",
            "cancelled": "cancelled",
        }[result_setting]
        connection.execute(
            "UPDATE payments SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, payment_id),
        )
        if status == "paid":
            connection.execute(
                "INSERT INTO payment_receipts (payment_id, receipt_reference) VALUES (?, ?)",
                (payment_id, f"RCP-{uuid.uuid4().hex[:12].upper()}"),
            )
        result = payment_record(connection, payment_id, learner_id)
        connection.commit()
    return jsonify({
        "payment": result,
        "reused": False,
        "demo": True,
        "message": "DEMO — NO REAL MONEY IS CHARGED.",
    }), 201


@app.get("/api/payments/<int:payment_id>/receipt")
def download_payment_receipt(payment_id):
    learner_id = get_session_learner_id()
    with closing(connect_database()) as connection:
        row = connection.execute(
            """
            SELECT payments.id, payments.amount_paise, payments.status,
                   payments.transaction_reference, payments.created_at,
                   payment_receipts.receipt_reference
            FROM payments
            JOIN payment_receipts ON payment_receipts.payment_id = payments.id
            WHERE payments.id = ? AND payments.learner_id = ?
            """,
            (payment_id, learner_id),
        ).fetchone()
    if row is None:
        abort(404, description="No verified receipt is available for this payment.")
    if row["status"] != "paid":
        abort(409, description="A receipt is available only for a verified successful payment.")
    with closing(connect_database()) as connection:
        payment_data = connection.execute(
            """
            SELECT student_name, student_id, course_name, semester,
                   amount_paise, payment_date, transaction_reference, status
            FROM payments
            WHERE id = ? AND learner_id = ?
            """,
            (payment_id, learner_id),
        ).fetchone()
    if payment_data is None:
        abort(404, description="No verified payment record exists for this receipt.")

    receipt_buffer = BytesIO()
    doc = SimpleDocTemplate(
        receipt_buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReceiptTitle", parent=styles["Title"], fontSize=18, leading=24, textColor=colors.HexColor("#0f172a"), alignment=1)
    heading_style = ParagraphStyle("ReceiptHeading", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#0f172a"), leading=18)
    normal_style = ParagraphStyle("ReceiptNormal", parent=styles["BodyText"], fontSize=10, leading=14)
    table_data = [
        [Paragraph("Student Course Management", title_style)],
        [Paragraph("DEMO PAYMENT RECEIPT — NO REAL MONEY IS CHARGED", heading_style)],
        [Paragraph(f"Receipt Number: {row['receipt_reference']}", normal_style)],
        [
            Table(
                [
                    [Paragraph("Student Name", normal_style), Paragraph(str(payment_data["student_name"] or "Student"), normal_style)],
                    [Paragraph("Student ID", normal_style), Paragraph(str(payment_data["student_id"] or learner_id[:8].upper()), normal_style)],
                    [Paragraph("Course Name", normal_style), Paragraph(str(payment_data["course_name"] or "Student Course Management"), normal_style)],
                    [Paragraph("Semester", normal_style), Paragraph(str(payment_data["semester"] or "Semester 1"), normal_style)],
                    [Paragraph("Amount Paid", normal_style), Paragraph(f"INR {payment_data['amount_paise'] / 100:.2f}", normal_style)],
                    [Paragraph("Payment Date", normal_style), Paragraph(str(payment_data["payment_date"] or row['created_at']), normal_style)],
                    [Paragraph("Transaction ID", normal_style), Paragraph(str(payment_data["transaction_reference"]), normal_style)],
                    [Paragraph("Payment Status", normal_style), Paragraph(str(payment_data["status"]).upper() + " (DEMO)", normal_style)],
                ],
                colWidths=[2.2 * inch, 3.1 * inch],
            )
        ],
    ]
    table = Table(table_data, colWidths=[5.7 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("GRID", (0, 1), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    content = [
        Paragraph("Student Course Management", title_style),
        Spacer(1, 0.2 * inch),
        Paragraph("DEMO PAYMENT RECEIPT — NO REAL MONEY IS CHARGED", heading_style),
        Spacer(1, 0.2 * inch),
        Paragraph(f"Receipt Number: {row['receipt_reference']}", normal_style),
        Spacer(1, 0.3 * inch),
        Table(
            [
                [Paragraph("Student Name", normal_style), Paragraph(str(payment_data["student_name"] or "Student"), normal_style)],
                [Paragraph("Student ID", normal_style), Paragraph(str(payment_data["student_id"] or learner_id[:8].upper()), normal_style)],
                [Paragraph("Course Name", normal_style), Paragraph(str(payment_data["course_name"] or "Student Course Management"), normal_style)],
                [Paragraph("Semester", normal_style), Paragraph(str(payment_data["semester"] or "Semester 1"), normal_style)],
                [Paragraph("Amount Paid", normal_style), Paragraph(f"INR {payment_data['amount_paise'] / 100:.2f}", normal_style)],
                [Paragraph("Payment Date", normal_style), Paragraph(str(payment_data["payment_date"] or row['created_at']), normal_style)],
                [Paragraph("Transaction ID", normal_style), Paragraph(str(payment_data["transaction_reference"]), normal_style)],
                [Paragraph("Payment Status", normal_style), Paragraph(str(payment_data["status"]).upper() + " (DEMO)", normal_style)],
            ],
            colWidths=[2.2 * inch, 3.1 * inch],
        ),
        Spacer(1, 0.3 * inch),
        Paragraph("Issued by Student Course Management. This is a demo transaction and no real funds were transferred.", normal_style),
    ]
    doc.build(content)
    receipt_buffer.seek(0)
    return send_file(
        receipt_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"receipt-{row['receipt_reference']}.pdf",
    )


@app.get("/support.html")
def support_page():
    return render_template("support.html")


@app.route("/api/support", methods=["GET", "POST"])
def support_requests():
    learner_id = get_session_learner_id()
    if request.method == "POST":
        payload = request_json_object()
        category = payload.get("category")
        description = str(payload.get("description", "")).strip()
        categories = {
            "course_access", "lesson_link", "project_submission",
            "payment", "assessment", "other",
        }
        if category not in categories:
            abort(400, description="Choose a valid support category.")
        if not 10 <= len(description) <= 3000:
            abort(400, description="Describe the issue in 10 to 3,000 characters.")
        with closing(connect_database()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO support_tickets (learner_id, category, description)
                VALUES (?, ?, ?)
                """,
                (learner_id, category, description),
            )
            ticket_id = cursor.lastrowid
            connection.commit()
        return jsonify({
            "ticket_id": ticket_id,
            "status": "open",
            "created_at": date.today().isoformat(),
            "message": "Support request submitted. Keep the ticket number for follow-up.",
        }), 201
    with closing(connect_database()) as connection:
        rows = connection.execute(
            """
            SELECT id, category, description, status, created_at, updated_at
            FROM support_tickets WHERE learner_id = ? ORDER BY id DESC
            """,
            (learner_id,),
        ).fetchall()
    return jsonify({"tickets": [dict(row) for row in rows]})


def assessment_query(connection, course_slug, assessment_slug):
    row = connection.execute(
        """
        SELECT assessments.*, courses.title AS course_title, lessons.title AS lesson_title
        FROM assessments
        JOIN courses ON courses.slug = assessments.course_slug
        LEFT JOIN lessons ON lessons.slug = assessments.lesson_slug
            AND lessons.course_id = courses.id
        WHERE assessments.course_slug = ? AND assessments.slug = ?
        """,
        (course_slug, assessment_slug),
    ).fetchone()
    if row is None:
        abort(404, description="Assessment not found.")
    return row


def assessment_payload(connection, row, learner_id):
    questions = connection.execute(
        """
        SELECT id, position, prompt, options_json, marks
        FROM assessment_questions WHERE assessment_id = ? ORDER BY position
        """,
        (row["id"],),
    ).fetchall()
    attempts = connection.execute(
        """
        SELECT id, attempt_number, status, marks_obtained, maximum_marks,
               percentage, passed, started_at, submitted_at
        FROM assessment_attempts
        WHERE assessment_id = ? AND learner_id = ?
        ORDER BY attempt_number DESC
        """,
        (row["id"], learner_id),
    ).fetchall()
    attempt_items = []
    for attempt in attempts:
        answers = connection.execute(
            """
            SELECT assessment_questions.position, assessment_answers.selected_option,
                   assessment_answers.answer_text,
                   assessment_answers.attachment_key IS NOT NULL AS has_attachment
            FROM assessment_answers
            JOIN assessment_questions
                ON assessment_questions.id = assessment_answers.question_id
            WHERE assessment_answers.attempt_id = ?
            """,
            (attempt["id"],),
        ).fetchall()
        attempt_items.append({
            **dict(attempt),
            "answers": {
                str(answer["position"]): {
                    "selected_option": answer["selected_option"],
                    "answer_text": answer["answer_text"],
                    "has_attachment": bool(answer["has_attachment"]),
                }
                for answer in answers
            },
        })
    return {
        "id": row["id"],
        "course_slug": row["course_slug"],
        "course_title": row["course_title"],
        "slug": row["slug"],
        "title": row["title"],
        "description": row["description"],
        "assessment_type": row["assessment_type"],
        "lesson_slug": row["lesson_slug"],
        "lesson_title": row["lesson_title"] or "Course-wide",
        "objectives": json.loads(row["objectives_json"]),
        "instructions": row["instructions"],
        "maximum_marks": row["maximum_marks"],
        "passing_marks": row["passing_marks"],
        "time_limit_minutes": row["time_limit_minutes"],
        "attempt_limit": row["attempt_limit"],
        "deadline": row["deadline"],
        "rubric": json.loads(row["rubric_json"]),
        "questions": [
            {
                "id": question["id"],
                "position": question["position"],
                "prompt": question["prompt"],
                "options": json.loads(question["options_json"]),
                "marks": question["marks"],
            }
            for question in questions
        ],
        "attempts": attempt_items,
        "attempts_used": len(attempt_items),
        "attempts_remaining": max(0, row["attempt_limit"] - len(attempt_items)),
    }


@app.get("/assessments.html")
def assessments_page():
    return render_template("assessments.html")


@app.get("/assessments/<course_slug>/<assessment_slug>")
def assessment_page(course_slug, assessment_slug):
    get_course(course_slug)
    with closing(connect_database()) as connection:
        assessment_query(connection, course_slug, assessment_slug)
    return render_template(
        "assessments.html",
        course_slug=course_slug,
        assessment_slug=assessment_slug,
    )


@app.get("/api/assessments")
def list_assessments():
    learner_id = get_session_learner_id()
    with closing(connect_database()) as connection:
        rows = connection.execute(
            "SELECT * FROM assessments ORDER BY course_slug, position"
        ).fetchall()
        results = []
        for row in rows:
            course = connection.execute(
                "SELECT title FROM courses WHERE slug = ?", (row["course_slug"],)
            ).fetchone()
            lesson = connection.execute(
                """
                SELECT lessons.title FROM lessons
                JOIN courses ON courses.id = lessons.course_id
                WHERE courses.slug = ? AND lessons.slug = ?
                """,
                (row["course_slug"], row["lesson_slug"]),
            ).fetchone() if row["lesson_slug"] else None
            attempts = connection.execute(
                """
                SELECT status, marks_obtained, maximum_marks, percentage, passed,
                       attempt_number, submitted_at
                FROM assessment_attempts
                WHERE assessment_id = ? AND learner_id = ?
                ORDER BY attempt_number DESC
                """,
                (row["id"], learner_id),
            ).fetchall()
            results.append({
                "course_slug": row["course_slug"],
                "course_title": course["title"],
                "slug": row["slug"],
                "title": row["title"],
                "description": row["description"],
                "assessment_type": row["assessment_type"],
                "lesson_title": lesson["title"] if lesson else "Course-wide",
                "maximum_marks": row["maximum_marks"],
                "passing_marks": row["passing_marks"],
                "attempt_limit": row["attempt_limit"],
                "attempts_used": len(attempts),
                "attempts": [dict(attempt) for attempt in attempts],
                "url": url_for(
                    "assessment_page",
                    course_slug=row["course_slug"],
                    assessment_slug=row["slug"],
                ),
            })
    return jsonify({"assessments": results})


@app.get("/api/assessments/<course_slug>/<assessment_slug>")
def assessment_detail(course_slug, assessment_slug):
    get_course(course_slug)
    learner_id = get_session_learner_id()
    with closing(connect_database()) as connection:
        row = assessment_query(connection, course_slug, assessment_slug)
        return jsonify(assessment_payload(connection, row, learner_id))


@app.post("/api/assessments/<course_slug>/<assessment_slug>/attempts")
def start_assessment_attempt(course_slug, assessment_slug):
    get_course(course_slug)
    learner_id = get_session_learner_id()
    with closing(connect_database()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = assessment_query(connection, course_slug, assessment_slug)
        if row["deadline"] and date.today() > date.fromisoformat(row["deadline"][:10]):
            connection.rollback()
            return jsonify({"error": "The assessment deadline has passed. Contact support if you need help."}), 409
        draft = connection.execute(
            """
            SELECT id FROM assessment_attempts
            WHERE assessment_id = ? AND learner_id = ? AND status = 'draft'
            ORDER BY attempt_number DESC LIMIT 1
            """,
            (row["id"], learner_id),
        ).fetchone()
        if draft:
            connection.commit()
            return jsonify({"attempt_id": draft["id"], "resumed": True})
        used_count = connection.execute(
            "SELECT COUNT(*) FROM assessment_attempts WHERE assessment_id = ? AND learner_id = ?",
            (row["id"], learner_id),
        ).fetchone()[0]
        if used_count >= row["attempt_limit"]:
            connection.rollback()
            return jsonify({"error": "No attempts remain. Contact support if you believe this is incorrect."}), 409
        attempt_number = used_count + 1
        cursor = connection.execute(
            """
            INSERT INTO assessment_attempts
                (learner_id, assessment_id, attempt_number, status, maximum_marks, started_at)
            VALUES (?, ?, ?, 'draft', ?, ?)
            """,
            (
                learner_id, row["id"], attempt_number, row["maximum_marks"],
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        attempt_id = cursor.lastrowid
        connection.commit()
    return jsonify({"attempt_id": attempt_id, "resumed": False}), 201


def get_owned_attempt(connection, assessment_id, attempt_id, learner_id):
    attempt = connection.execute(
        """
        SELECT * FROM assessment_attempts
        WHERE id = ? AND assessment_id = ? AND learner_id = ?
        """,
        (attempt_id, assessment_id, learner_id),
    ).fetchone()
    if attempt is None:
        abort(404, description="Assessment attempt not found.")
    return attempt


def attempt_time_expired(attempt, time_limit_minutes):
    if not time_limit_minutes:
        return False
    started_at = datetime.fromisoformat(attempt["started_at"].replace("Z", "+00:00"))
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= started_at + timedelta(minutes=time_limit_minutes)


@app.put("/api/assessments/<course_slug>/<assessment_slug>/attempts/<int:attempt_id>/answers")
def save_assessment_answers(course_slug, assessment_slug, attempt_id):
    get_course(course_slug)
    learner_id = get_session_learner_id()
    payload = request_json_object()
    with closing(connect_database()) as connection:
        assessment = assessment_query(connection, course_slug, assessment_slug)
        attempt = get_owned_attempt(connection, assessment["id"], attempt_id, learner_id)
        if attempt["status"] != "draft":
            return jsonify({"error": "This attempt is already submitted and can no longer be changed."}), 409
        if attempt_time_expired(attempt, assessment["time_limit_minutes"]):
            return jsonify({"error": "The time limit has elapsed. Submit the saved answers to receive a result."}), 409
        questions = connection.execute(
            "SELECT id, position, options_json FROM assessment_questions WHERE assessment_id = ?",
            (assessment["id"],),
        ).fetchall()
        question_by_position = {str(question["position"]): question for question in questions}
        if assessment["assessment_type"] == "mcq":
            answers = payload.get("answers")
            if not isinstance(answers, dict):
                abort(400, description="Answers must be provided as a question-position map.")
            if any(key not in question_by_position for key in answers):
                abort(400, description="An answer refers to an unknown question.")
            for position, selected_option in answers.items():
                options = json.loads(question_by_position[position]["options_json"])
                if type(selected_option) is not int or not 0 <= selected_option < len(options):
                    abort(400, description="A selected option is not valid for its question.")
                connection.execute(
                    """
                    INSERT INTO assessment_answers (attempt_id, question_id, selected_option)
                    VALUES (?, ?, ?)
                    ON CONFLICT(attempt_id, question_id)
                    DO UPDATE SET selected_option = excluded.selected_option
                    """,
                    (attempt_id, question_by_position[position]["id"], selected_option),
                )
        else:
            answer_text = payload.get("answer_text", "")
            if not isinstance(answer_text, str) or len(answer_text) > 10000:
                abort(400, description="Submission text must be 10,000 characters or fewer.")
            question = questions[0]
            connection.execute(
                """
                INSERT INTO assessment_answers (attempt_id, question_id, answer_text)
                VALUES (?, ?, ?)
                ON CONFLICT(attempt_id, question_id)
                DO UPDATE SET answer_text = excluded.answer_text
                """,
                (attempt_id, question["id"], answer_text),
            )
        connection.commit()
    return jsonify({"saved": True, "message": "Draft answers saved in this browser session."})


ALLOWED_SUBMISSION_EXTENSIONS = {".csv", ".jpeg", ".jpg", ".pdf", ".png", ".txt", ".zip"}


@app.post("/api/assessments/<course_slug>/<assessment_slug>/attempts/<int:attempt_id>/attachment")
def upload_assessment_attachment(course_slug, assessment_slug, attempt_id):
    get_course(course_slug)
    learner_id = get_session_learner_id()
    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        abort(400, description="Choose a file to upload.")
    extension = Path(uploaded_file.filename).suffix.lower()
    if extension not in ALLOWED_SUBMISSION_EXTENSIONS:
        abort(400, description="File type not allowed. Use PDF, ZIP, PNG, JPEG, TXT or CSV.")
    content = uploaded_file.stream.read(5 * 1024 * 1024 + 1)
    if not content:
        abort(400, description="The selected file is empty.")
    if len(content) > 5 * 1024 * 1024:
        abort(413, description="File is larger than the 5 MB upload limit.")
    with closing(connect_database()) as connection:
        assessment = assessment_query(connection, course_slug, assessment_slug)
        attempt = get_owned_attempt(connection, assessment["id"], attempt_id, learner_id)
        if attempt["status"] != "draft":
            abort(409, description="This attempt has already been submitted.")
        question = connection.execute(
            "SELECT id FROM assessment_questions WHERE assessment_id = ? ORDER BY position LIMIT 1",
            (assessment["id"],),
        ).fetchone()
        stored_name = f"{uuid.uuid4().hex}{extension}"
        private_directory = PROJECT_DIR / "instance" / "submissions" / learner_id
        private_directory.mkdir(parents=True, exist_ok=True)
        stored_path = private_directory / stored_name
        stored_path.write_bytes(content)
        try:
            connection.execute(
                """
                INSERT INTO assessment_answers (attempt_id, question_id, attachment_key)
                VALUES (?, ?, ?)
                ON CONFLICT(attempt_id, question_id)
                DO UPDATE SET attachment_key = excluded.attachment_key
                """,
                (attempt_id, question["id"], stored_name),
            )
            connection.commit()
        except sqlite3.Error:
            stored_path.unlink(missing_ok=True)
            app.logger.exception("Unable to record assessment attachment.")
            return jsonify({"error": "The file could not be saved. Please try again."}), 503
    return jsonify({"uploaded": True, "message": "Attachment saved privately for this attempt."})


@app.get("/api/assessments/<course_slug>/<assessment_slug>/attempts/<int:attempt_id>/attachment")
def download_assessment_attachment(course_slug, assessment_slug, attempt_id):
    learner_id = get_session_learner_id()
    with closing(connect_database()) as connection:
        assessment = assessment_query(connection, course_slug, assessment_slug)
        get_owned_attempt(connection, assessment["id"], attempt_id, learner_id)
        row = connection.execute(
            "SELECT attachment_key FROM assessment_answers WHERE attempt_id = ? AND attachment_key IS NOT NULL",
            (attempt_id,),
        ).fetchone()
    if row is None:
        abort(404, description="No submission attachment is available.")
    private_path = PROJECT_DIR / "instance" / "submissions" / learner_id / row["attachment_key"]
    if not private_path.is_file():
        abort(404, description="The stored submission file is unavailable. Upload it again or contact support.")
    return send_file(private_path, as_attachment=True, download_name=f"submission-{assessment_slug}{private_path.suffix}")


@app.post("/api/assessments/<course_slug>/<assessment_slug>/attempts/<int:attempt_id>/submit")
def submit_assessment_attempt(course_slug, assessment_slug, attempt_id):
    get_course(course_slug)
    learner_id = get_session_learner_id()
    payload = request_json_object()
    with closing(connect_database()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        assessment = assessment_query(connection, course_slug, assessment_slug)
        attempt = get_owned_attempt(connection, assessment["id"], attempt_id, learner_id)
        if attempt["status"] != "draft":
            connection.rollback()
            return jsonify({"error": "This attempt has already been submitted."}), 409
        timed_out = attempt_time_expired(attempt, assessment["time_limit_minutes"])
        questions = connection.execute(
            "SELECT id, position, correct_option, explanation, marks, prompt FROM assessment_questions WHERE assessment_id = ? ORDER BY position",
            (assessment["id"],),
        ).fetchall()
        answers = connection.execute(
            "SELECT question_id, selected_option, answer_text, attachment_key FROM assessment_answers WHERE attempt_id = ?",
            (attempt_id,),
        ).fetchall()
        answer_by_question = {answer["question_id"]: answer for answer in answers}
        if assessment["assessment_type"] == "mcq":
            if not timed_out and any(question["id"] not in answer_by_question for question in questions):
                connection.rollback()
                abort(400, description="Answer every question before submitting.")
            score = sum(
                question["marks"]
                for question in questions
                if question["id"] in answer_by_question
                and answer_by_question[question["id"]]["selected_option"] == question["correct_option"]
            )
            percentage = round(score * 100 / assessment["maximum_marks"], 1)
            passed = score >= assessment["passing_marks"]
            status = "passed" if passed else "failed"
            feedback = []
            for question in questions:
                options = json.loads(connection.execute(
                    "SELECT options_json FROM assessment_questions WHERE id = ?",
                    (question["id"],),
                ).fetchone()["options_json"])
                answer = answer_by_question.get(question["id"])
                selected_option = answer["selected_option"] if answer else None
                feedback.append({
                    "position": question["position"],
                    "prompt": question["prompt"],
                    "correct": selected_option == question["correct_option"],
                    "selected_option": selected_option,
                    "correct_option": question["correct_option"],
                    "correct_answer": options[question["correct_option"]],
                    "explanation": question["explanation"],
                })
        else:
            answer = answer_by_question.get(questions[0]["id"])
            if not answer or (
                len(answer["answer_text"].strip()) < 20 and not answer["attachment_key"]
            ):
                connection.rollback()
                abort(400, description="Add a substantive explanation or an attachment before submitting.")
            score = percentage = passed = None
            status = "awaiting_review"
            feedback = []
        connection.execute(
            """
            UPDATE assessment_attempts
            SET status = ?, marks_obtained = ?, percentage = ?, passed = ?,
                submitted_at = ?
            WHERE id = ?
            """,
            (
                status, score, percentage, int(passed) if passed is not None else None,
                datetime.now(timezone.utc).isoformat(timespec="seconds"), attempt_id,
            ),
        )
        connection.commit()
    return jsonify({
        "attempt_id": attempt_id,
        "status": status,
        "marks_obtained": score,
        "maximum_marks": assessment["maximum_marks"],
        "percentage": percentage,
        "passed": passed,
        "timed_out": timed_out,
        "manual_review": status == "awaiting_review",
        "feedback": feedback,
        "message": (
            "Submission received. It is awaiting manual instructor review; no marks have been assigned."
            if status == "awaiting_review"
            else f"Automatically scored: {score}/{assessment['maximum_marks']}."
        ),
    })


@app.get("/logout")
def logout():
    learner_id = get_session_learner_id()
    session.clear()
    session["learner_id"] = learner_id
    return redirect(url_for("home"))


@app.get("/")
def home():
    return send_from_directory(PROJECT_DIR, "index.html")


@app.get("/courses.html")
def courses_page():
    learner_id = get_session_learner_id()
    course_cards = [{
        "slug": slug,
        **course,
        "progress": get_course_progress(slug, learner_id),
        "url": url_for("course_overview", course_slug=slug),
    } for slug, course in COURSES.items()]
    return render_template("courses.html", course_cards=course_cards)


@app.get("/courses/<course_slug>")
def course_overview(course_slug):
    course = get_course(course_slug)
    learner_id = get_session_learner_id()
    progress = get_course_progress(course_slug, learner_id)
    assessment = latest_assessment(course_slug, learner_id)
    return render_template(
        "_course_overview.html",
        course_slug=course_slug,
        course=course,
        modules=get_course_modules(course_slug),
        progress=progress,
        assessment=assessment,
        learner_id=learner_id,
        first_lesson=next(iter_course_lessons(course_slug))["slug"],
    )


@app.get("/api/courses/<course_slug>/progress")
def course_progress(course_slug):
    course = get_course(course_slug)
    learner_id = get_learner_id(request.args.get("learner_id"), required=False)
    progress = get_course_progress(course_slug, learner_id)
    return jsonify({
        "course_slug": course_slug,
        "completed_lessons": sorted(progress["completed"]),
        "completed_count": progress["completed_count"],
        "total": progress["total"],
        "percent": progress["percent"],
        "course_complete": progress["is_complete"],
        "resources_unlocked": progress["is_complete"],
        "latest_assessment": latest_assessment(course_slug, learner_id),
        "title": course["title"],
    })


@app.get("/courses/<course_slug>/lessons/<lesson_slug>")
def course_lesson(course_slug, lesson_slug):
    course = get_course(course_slug)
    lessons = list(iter_course_lessons(course_slug))
    lesson_index = next(
        (index for index, lesson in enumerate(lessons) if lesson["slug"] == lesson_slug),
        None,
    )
    if lesson_index is None:
        abort(404)
    learner_id = get_session_learner_id()
    progress = get_course_progress(course_slug, learner_id)
    lesson = lessons[lesson_index]
    return render_template(
        "_course_lesson.html",
        course_slug=course_slug,
        course=course,
        lesson=lesson,
        modules=get_course_modules(course_slug),
        lessons=lessons,
        previous_lesson=lessons[lesson_index - 1] if lesson_index > 0 else None,
        next_lesson=lessons[lesson_index + 1] if lesson_index + 1 < len(lessons) else None,
        progress=progress,
        learner_id=learner_id,
    )


@app.post("/api/courses/<course_slug>/lessons/<lesson_slug>/complete")
def complete_course_lesson(course_slug, lesson_slug):
    get_course(course_slug)
    payload = request_json_object()
    learner_id = get_learner_id(payload.get("learner_id"), required=True)
    lesson = next(
        (lesson for lesson in iter_course_lessons(course_slug) if lesson["slug"] == lesson_slug),
        None,
    )
    if lesson is None:
        abort(404)
    with closing(connect_database()) as connection:
        row = connection.execute(
            """
            SELECT lessons.id
            FROM lessons
            JOIN courses ON courses.id = lessons.course_id
            WHERE courses.slug = ? AND lessons.slug = ?
            """,
            (course_slug, lesson_slug),
        ).fetchone()
        if row is None:
            abort(404)
        connection.execute(
            """
            INSERT OR IGNORE INTO browser_lesson_progress (learner_id, lesson_id)
            VALUES (?, ?)
            """,
            (learner_id, row["id"]),
        )
        connection.commit()
    progress = get_course_progress(course_slug, learner_id)
    return jsonify({
        "status": "ok",
        "lesson_slug": lesson_slug,
        "completed_count": progress["completed_count"],
        "total": progress["total"],
        "percent": progress["percent"],
        "course_complete": progress["is_complete"],
        "resources_unlocked": progress["is_complete"],
    })


@app.post("/api/courses/<course_slug>/lessons/<lesson_slug>/quiz")
def check_lesson_quiz(course_slug, lesson_slug):
    get_course(course_slug)
    payload = request_json_object()
    learner_id = get_learner_id(payload.get("learner_id"), required=True)
    lesson = next(
        (lesson for lesson in iter_course_lessons(course_slug) if lesson["slug"] == lesson_slug),
        None,
    )
    if lesson is None:
        abort(404)
    answers = payload.get("answers")
    questions = lesson["quiz"]
    if not isinstance(answers, list) or len(answers) != len(questions):
        abort(400, description="Submit one answer for every quiz question.")
    if any(type(answer) is not int or answer < 0 for answer in answers):
        abort(400, description="Quiz answers must be non-negative option indexes.")
    results = []
    for question, answer in zip(questions, answers):
        if answer >= len(question["options"]):
            abort(400, description="A quiz answer is outside the available options.")
        results.append({
            "correct": answer == question["answer"],
            "answer": question["answer"],
            "explanation": question["explanation"],
        })
    return jsonify({
        "correct_count": sum(result["correct"] for result in results),
        "question_count": len(results),
        "passed": all(result["correct"] for result in results),
        "results": results,
    })


@app.post("/api/courses/<course_slug>/assessment")
def submit_course_assessment(course_slug):
    course = get_course(course_slug)
    payload = request_json_object()
    learner_id = get_learner_id(payload.get("learner_id"), required=True)
    answers = payload.get("answers")
    questions = course["assessment"]
    if not isinstance(answers, list) or len(answers) != len(questions):
        abort(400, description="Submit one answer for every assessment question.")
    if any(type(answer) is not int or answer < 0 for answer in answers):
        abort(400, description="Assessment answers must be non-negative option indexes.")
    if any(answer >= len(question["options"]) for answer, question in zip(answers, questions)):
        abort(400, description="An assessment answer is outside the available options.")
    score = sum(answer == question["answer"] for answer, question in zip(answers, questions))
    passing_score = (len(questions) * 70 + 99) // 100
    passed = score >= passing_score
    with closing(connect_database()) as connection:
        connection.execute(
            """
            INSERT INTO course_assessment_attempts
                (learner_id, course_slug, score, question_count, passed)
            VALUES (?, ?, ?, ?, ?)
            """,
            (learner_id, course_slug, score, len(questions), int(passed)),
        )
        connection.commit()
    return jsonify({
        "score": score,
        "question_count": len(questions),
        "passing_score": passing_score,
        "passed": passed,
        "results": [
            {
                "correct": answer == question["answer"],
                "answer": question["answer"],
                "explanation": question["explanation"],
            }
            for answer, question in zip(answers, questions)
        ],
    })


@app.get("/python-programming.html")
def legacy_python_course():
    return redirect(url_for("course_overview", course_slug="python-programming"))


@app.get("/ui-ux-design.html")
def legacy_uiux_course():
    return redirect(url_for("course_overview", course_slug="ui-ux-design"))


@app.get("/data-science.html")
def legacy_data_science_course():
    return redirect(url_for("course_overview", course_slug="data-science"))


@app.get("/web-development.html")
def legacy_web_development_course():
    return redirect(url_for("course_overview", course_slug="web-development"))


@app.get("/<path:filename>")
def serve_public_file(filename):
    if filename not in PUBLIC_FILES:
        abort(404)
    return send_from_directory(PROJECT_DIR, filename)


@app.get("/api/health")
def health():
    try:
        with closing(connect_database()) as connection:
            initialized = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'users'"
            ).fetchone()
    except sqlite3.Error:
        return jsonify({"status": "error", "database": "unavailable"}), 503

    if initialized is None:
        return jsonify({"status": "error", "database": "not initialized"}), 503

    return jsonify({"status": "ok", "database": "ready"})


@app.get("/api/courses")
def list_courses():
    try:
        with closing(connect_database()) as connection:
            rows = connection.execute(
                """
                SELECT courses.slug, courses.title, courses.description,
                       COUNT(lessons.id) AS lesson_count
                FROM courses
                LEFT JOIN lessons ON lessons.course_id = courses.id
                GROUP BY courses.id
                ORDER BY courses.id
                """
            ).fetchall()
    except sqlite3.Error:
        return jsonify({"error": "Database is unavailable or not initialized."}), 503

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    initialize_database()
    debug_enabled = (
        not IS_PRODUCTION
        and os.environ.get("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes"}
    )
    app.run(debug=debug_enabled, port=int(os.environ.get("PORT", "5000")))