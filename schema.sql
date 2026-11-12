PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enrollments (
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id)
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    position INTEGER NOT NULL,
    UNIQUE (course_id, slug),
    UNIQUE (course_id, position)
);

CREATE TABLE IF NOT EXISTS lesson_progress (
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS browser_lesson_progress (
    learner_id TEXT NOT NULL,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (learner_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS course_assessment_attempts (
    id INTEGER PRIMARY KEY,
    learner_id TEXT NOT NULL,
    course_slug TEXT NOT NULL REFERENCES courses(slug) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    question_count INTEGER NOT NULL,
    passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
    attempted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fee_accounts (
    learner_id TEXT PRIMARY KEY,
    total_paise INTEGER NOT NULL CHECK (total_paise >= 0),
    due_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY,
    learner_id TEXT NOT NULL REFERENCES fee_accounts(learner_id) ON DELETE CASCADE,
    amount_paise INTEGER NOT NULL CHECK (amount_paise > 0),
    method TEXT NOT NULL CHECK (method IN ('demo')),
    status TEXT NOT NULL CHECK (status IN ('pending', 'failed', 'cancelled', 'paid', 'refunded')),
    idempotency_key TEXT NOT NULL,
    transaction_reference TEXT UNIQUE,
    student_name TEXT,
    student_id TEXT,
    course_name TEXT,
    semester TEXT,
    payment_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (learner_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS payment_receipts (
    id INTEGER PRIMARY KEY,
    payment_id INTEGER NOT NULL UNIQUE REFERENCES payments(id) ON DELETE CASCADE,
    receipt_reference TEXT NOT NULL UNIQUE,
    issued_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY,
    course_slug TEXT NOT NULL REFERENCES courses(slug) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    assessment_type TEXT NOT NULL CHECK (
        assessment_type IN ('mcq', 'coding', 'practical', 'project', 'final')
    ),
    lesson_slug TEXT,
    objectives_json TEXT NOT NULL,
    instructions TEXT NOT NULL,
    maximum_marks INTEGER NOT NULL CHECK (maximum_marks > 0),
    passing_marks INTEGER NOT NULL CHECK (passing_marks >= 0 AND passing_marks <= maximum_marks),
    time_limit_minutes INTEGER CHECK (time_limit_minutes IS NULL OR time_limit_minutes > 0),
    attempt_limit INTEGER NOT NULL CHECK (attempt_limit > 0),
    deadline TEXT,
    rubric_json TEXT NOT NULL,
    position INTEGER NOT NULL,
    UNIQUE (course_slug, slug),
    UNIQUE (course_slug, position)
);

CREATE TABLE IF NOT EXISTS assessment_questions (
    id INTEGER PRIMARY KEY,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    options_json TEXT NOT NULL DEFAULT '[]',
    correct_option INTEGER,
    explanation TEXT NOT NULL DEFAULT '',
    marks INTEGER NOT NULL CHECK (marks > 0),
    UNIQUE (assessment_id, position)
);

CREATE TABLE IF NOT EXISTS assessment_attempts (
    id INTEGER PRIMARY KEY,
    learner_id TEXT NOT NULL,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    status TEXT NOT NULL CHECK (
        status IN ('draft', 'submitted', 'awaiting_review', 'passed', 'failed', 'reviewed')
    ),
    marks_obtained INTEGER CHECK (marks_obtained IS NULL OR marks_obtained >= 0),
    maximum_marks INTEGER NOT NULL CHECK (maximum_marks > 0),
    percentage REAL CHECK (percentage IS NULL OR (percentage >= 0 AND percentage <= 100)),
    passed INTEGER CHECK (passed IS NULL OR passed IN (0, 1)),
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submitted_at TEXT,
    UNIQUE (learner_id, assessment_id, attempt_number)
);

CREATE TABLE IF NOT EXISTS assessment_answers (
    id INTEGER PRIMARY KEY,
    attempt_id INTEGER NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES assessment_questions(id) ON DELETE CASCADE,
    selected_option INTEGER,
    answer_text TEXT NOT NULL DEFAULT '',
    attachment_key TEXT,
    UNIQUE (attempt_id, question_id)
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY,
    learner_id TEXT NOT NULL,
    category TEXT NOT NULL CHECK (
        category IN ('course_access', 'lesson_link', 'project_submission', 'payment', 'assessment', 'other')
    ),
    description TEXT NOT NULL CHECK (length(description) BETWEEN 10 AND 3000),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    due_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'submitted'
        CHECK (status IN ('submitted', 'reviewed', 'returned')),
    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (assignment_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_lessons_course_position ON lessons(course_id, position);
CREATE INDEX IF NOT EXISTS idx_progress_student_id ON lesson_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_browser_progress_learner ON browser_lesson_progress(learner_id);
CREATE INDEX IF NOT EXISTS idx_assessment_learner_course
    ON course_assessment_attempts(learner_id, course_slug, attempted_at);
CREATE INDEX IF NOT EXISTS idx_payments_learner_created
    ON payments(learner_id, created_at);
CREATE INDEX IF NOT EXISTS idx_assessment_course_position
    ON assessments(course_slug, position);
CREATE INDEX IF NOT EXISTS idx_attempts_learner_assessment
    ON assessment_attempts(learner_id, assessment_id, attempt_number);
CREATE INDEX IF NOT EXISTS idx_support_learner_created
    ON support_tickets(learner_id, created_at);
CREATE INDEX IF NOT EXISTS idx_assignments_course_id ON assignments(course_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student_id ON submissions(student_id);

INSERT OR IGNORE INTO courses (slug, title, description) VALUES
    ('web-development', 'Web Development', 'Learn HTML, CSS, JavaScript, and build modern websites.'),
    ('python-programming', 'Python Programming', 'Learn Python programming, functions, and problem solving.'),
    ('ui-ux-design', 'UI/UX Design', 'Learn user interface design, wireframes, and prototypes.'),
    ('data-science', 'Data Science', 'Learn data analysis, visualization, and basic machine learning.');

INSERT OR IGNORE INTO lessons (course_id, slug, title, position)
SELECT id, 'html-fundamentals', 'HTML Fundamentals', 1
FROM courses WHERE slug = 'web-development';

INSERT OR IGNORE INTO lessons (course_id, slug, title, position)
SELECT id, 'css-responsive-design', 'CSS & Responsive Design', 2
FROM courses WHERE slug = 'web-development';

INSERT OR IGNORE INTO lessons (course_id, slug, title, position)
SELECT id, 'javascript-basics', 'JavaScript Basics', 3
FROM courses WHERE slug = 'web-development';

INSERT OR IGNORE INTO lessons (course_id, slug, title, position)
SELECT id, 'modern-website-development', 'Modern Website Development', 4
FROM courses WHERE slug = 'web-development';