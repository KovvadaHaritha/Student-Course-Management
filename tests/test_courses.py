from contextlib import closing
from copy import deepcopy
import tempfile
import unittest
import uuid
from pathlib import Path
from urllib.parse import urlparse

import app as backend
from course_catalog import COURSES, iter_course_lessons


class CoursePlatformTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_database_path = backend.DATABASE_PATH
        backend.DATABASE_PATH = Path(self.temporary_directory.name) / "courses.sqlite3"
        backend.initialize_database()
        self.client = backend.app.test_client()
        self.learner_id = self.client.get("/api/session").json["learner_id"]

    def tearDown(self):
        backend.DATABASE_PATH = self.original_database_path
        self.temporary_directory.cleanup()

    def test_curriculum_has_multiple_complete_lessons_per_module(self):
        expected_lesson_counts = {
            "web-development": 4,
            "python-programming": 24,
            "ui-ux-design": 24,
            "data-science": 28,
        }
        for course_slug, lesson_count in expected_lesson_counts.items():
            course = COURSES[course_slug]
            lessons = list(iter_course_lessons(course_slug))
            self.assertEqual(len(lessons), lesson_count)
            if course_slug != "web-development":
                self.assertTrue(all(len(module["lessons"]) >= 2 for module in course["modules"]))
            for lesson in lessons:
                for field in ("objectives", "explanation", "steps", "real_world", "example", "exercise", "quiz"):
                    self.assertTrue(lesson[field], f"{course_slug}/{lesson['slug']} missing {field}")
                self.assertTrue(all(question["explanation"] for question in lesson["quiz"]))

    def test_lesson_generation_accepts_nested_title_mappings(self):
        course = deepcopy(COURSES["python-programming"])
        course["modules"] = [course["modules"][0]]
        course["modules"][0]["lessons"] = [
            {"slug": "nested-title", "title": {"title": "Nested lesson title"}}
        ]
        COURSES["test-course"] = course
        try:
            lesson = next(iter_course_lessons("test-course"))
        finally:
            del COURSES["test-course"]

        self.assertEqual(lesson["title"], "Nested lesson title")
        self.assertIn("nested lesson title", lesson["objectives"][0])

    def test_web_development_uses_existing_lesson_records(self):
        with closing(backend.connect_database()) as connection:
            rows = connection.execute(
                """
                SELECT lessons.slug, lessons.title FROM lessons
                JOIN courses ON courses.id = lessons.course_id
                WHERE courses.slug = 'web-development'
                ORDER BY position
                """
            ).fetchall()
        self.assertEqual(
            [(row["slug"], row["title"]) for row in rows],
            [
                ("html-fundamentals", "HTML Fundamentals"),
                ("css-responsive-design", "CSS & Responsive Design"),
                ("javascript-basics", "JavaScript Basics"),
                ("modern-website-development", "Modern Website Development"),
            ],
        )

    def test_first_request_initializes_missing_tables_without_replacing_records(self):
        backend.DATABASE_PATH = Path(self.temporary_directory.name) / "legacy.sqlite3"
        with backend._database_initialization_lock:
            backend._database_initialized = False

        with closing(backend.connect_database()) as connection:
            connection.execute(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'student'
                        CHECK (role IN ('student', 'admin')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                INSERT INTO users (email, full_name, password_hash)
                VALUES ('existing@example.com', 'Existing Student', 'preserved')
                """
            )
            connection.commit()

        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

        with closing(backend.connect_database()) as connection:
            browser_progress_table = connection.execute(
                """
                SELECT 1 FROM sqlite_master
                WHERE type = 'table' AND name = 'browser_lesson_progress'
                """
            ).fetchone()
            existing_user = connection.execute(
                "SELECT full_name, password_hash FROM users WHERE email = ?",
                ("existing@example.com",),
            ).fetchone()
        self.assertIsNotNone(browser_progress_table)
        self.assertEqual(
            (existing_user["full_name"], existing_user["password_hash"]),
            ("Existing Student", "preserved"),
        )

    def test_course_cards_and_external_resources_are_complete_https_links(self):
        response = self.client.get("/courses.html")
        for course_slug in COURSES:
            self.assertIn(f'href="/courses/{course_slug}"'.encode(), response.data)

        for course_slug, course in COURSES.items():
            self.assertTrue(course["difficulty"])
            self.assertTrue(course["duration"])
            self.assertTrue(course["prerequisites"])
            self.assertTrue(course["documentation"])
            self.assertTrue(course["channels"])
            self.assertTrue(course["resources"])
            for label, href in (
                course["documentation"] + course["channels"] + course["resources"]
            ):
                parsed = urlparse(href)
                self.assertTrue(label)
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.netloc)

    def test_all_overview_and_lesson_routes_render(self):
        for course_slug in COURSES:
            overview = self.client.get(f"/courses/{course_slug}")
            self.assertEqual(overview.status_code, 200)
            self.assertIn(b"Final assessment", overview.data)
            self.assertIn(b"Course completion resources", overview.data)

            lessons = list(iter_course_lessons(course_slug))
            for index, lesson in enumerate(lessons):
                response = self.client.get(
                    f"/courses/{course_slug}/lessons/{lesson['slug']}"
                )
                self.assertEqual(response.status_code, 200, lesson["slug"])
                self.assertIn(b"Learning objectives", response.data)
                self.assertIn(b"Short quiz", response.data)
                self.assertIn(b"Mark Lesson Complete", response.data)
                if index:
                    self.assertIn(b"Previous lesson", response.data)
                if index + 1 < len(lessons):
                    self.assertIn(b"Next lesson", response.data)

    def test_quiz_grading_returns_feedback(self):
        for course_slug in COURSES:
            lesson = next(iter_course_lessons(course_slug))
            correct_answers = [question["answer"] for question in lesson["quiz"]]
            response = self.client.post(
                f"/api/courses/{course_slug}/lessons/{lesson['slug']}/quiz",
                json={"learner_id": self.learner_id, "answers": correct_answers},
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["passed"])
            self.assertTrue(all(result["explanation"] for result in response.json["results"]))

            incorrect_answers = [(answer + 1) % len(question["options"])
                                 for answer, question in zip(correct_answers, lesson["quiz"])]
            response = self.client.post(
                f"/api/courses/{course_slug}/lessons/{lesson['slug']}/quiz",
                json={"learner_id": self.learner_id, "answers": incorrect_answers},
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["passed"])

    def test_progress_persists_and_unlocks_only_after_every_lesson(self):
        course_slug = "ui-ux-design"
        lessons = list(iter_course_lessons(course_slug))
        complete_url = f"/api/courses/{course_slug}/lessons/{lessons[0]['slug']}/complete"
        response = self.client.post(complete_url, json={"learner_id": self.learner_id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json["resources_unlocked"])

        progress_url = f"/api/courses/{course_slug}/progress?learner_id={self.learner_id}"
        progress = self.client.get(progress_url).json
        self.assertEqual(progress["completed_count"], 1)
        self.assertFalse(progress["course_complete"])
        self.assertEqual(
            self.client.get(progress_url).json["completed_count"],
            1,
            "Progress must be available after reloading in the same signed browser session.",
        )
        self.assertEqual(
            self.client.post(complete_url, json={"learner_id": self.learner_id}).json["completed_count"],
            1,
            "Completing the same lesson twice must be idempotent.",
        )

        for lesson in lessons[1:]:
            response = self.client.post(
                f"/api/courses/{course_slug}/lessons/{lesson['slug']}/complete",
                json={"learner_id": self.learner_id},
            )
            self.assertEqual(response.status_code, 200)
        progress = self.client.get(progress_url).json
        self.assertEqual(progress["completed_count"], len(lessons))
        self.assertTrue(progress["course_complete"])
        self.assertTrue(progress["resources_unlocked"])
        overview = self.client.get(
            f"/courses/{course_slug}?learner_id={self.learner_id}"
        )
        self.assertIn(b'href="https://help.figma.com/hc/en-us"', overview.data)

        other_learner = str(uuid.uuid4())
        other_progress = self.client.get(
            f"/api/courses/{course_slug}/progress?learner_id={other_learner}"
        )
        self.assertEqual(other_progress.status_code, 403)

    def test_final_assessment_is_graded_and_stored(self):
        for course_slug, course in COURSES.items():
            questions = course["assessment"]
            incorrect_answers = [1 if question["answer"] == 0 else 0 for question in questions]
            response = self.client.post(
                f"/api/courses/{course_slug}/assessment",
                json={"learner_id": self.learner_id, "answers": incorrect_answers},
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["passed"])
            self.assertEqual(response.json["score"], 0)

            correct_answers = [question["answer"] for question in questions]
            boundary_answers = correct_answers.copy()
            last_question = questions[-1]
            boundary_answers[-1] = (last_question["answer"] + 1) % len(last_question["options"])
            response = self.client.post(
                f"/api/courses/{course_slug}/assessment",
                json={"learner_id": self.learner_id, "answers": boundary_answers},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["score"], 4)
            self.assertEqual(response.json["passing_score"], 4)
            self.assertTrue(response.json["passed"])

            response = self.client.post(
                f"/api/courses/{course_slug}/assessment",
                json={
                    "learner_id": self.learner_id,
                    "answers": correct_answers,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["passed"])
            self.assertEqual(response.json["score"], len(questions))

            progress = self.client.get(
                f"/api/courses/{course_slug}/progress?learner_id={self.learner_id}"
            ).json
            self.assertTrue(progress["latest_assessment"]["passed"])
            self.assertFalse(progress["course_complete"])
            self.assertFalse(progress["resources_unlocked"])

    def test_invalid_ids_and_nonexistent_lessons_are_rejected(self):
        response = self.client.get("/api/courses/python-programming/progress?learner_id=bad")
        self.assertEqual(response.status_code, 400)
        response = self.client.get("/courses/data-science/lessons/not-a-lesson")
        self.assertEqual(response.status_code, 404)
        response = self.client.post(
            "/api/courses/python-programming/lessons/not-a-lesson/complete",
            json={"learner_id": self.learner_id},
        )
        self.assertEqual(response.status_code, 404)

    def test_existing_portal_routes_and_legacy_course_urls_remain_available(self):
        for path in (
            "/", "/courses.html", "/dashboard.html", "/assignments.html",
            "/assessments.html", "/fees.html", "/profile.html",
        ):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            response.close()
        assessments = self.client.get("/assessments.html")
        self.assertIn(b"Review your course quizzes", assessments.data)
        assessments.close()
        assignments = self.client.get("/assignments.html")
        self.assertIn(b"submitAssignment('HTML & CSS Project')", assignments.data)
        assignments.close()
        assessment_items = self.client.get("/api/assessments").json["assessments"]
        detail = self.client.get(assessment_items[0]["url"])
        self.assertEqual(detail.status_code, 200)
        self.assertIn(b"assessmentWorkspace", detail.data)
        self.assertIn(assessment_items[0]["course_slug"].encode(), detail.data)
        self.assertIn(assessment_items[0]["slug"].encode(), detail.data)
        detail.close()
        for path in ("/python-programming.html", "/ui-ux-design.html", "/data-science.html"):
            self.assertEqual(self.client.get(path).status_code, 302, path)
        self.assertEqual(self.client.get("/api/health").status_code, 200)


if __name__ == "__main__":
    unittest.main()
