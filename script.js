const profileStorageKey = "studentCourseDemoProfile";
const assignmentsStorageKey = "studentCourseDemoAssignments";
const completedLessonsStorageKey = "studentCourseDemoCompletedLessons";
const learnerIdStorageKey = "studentCourseLearnerId";
const legacyWebLessonSlugs = {
    "HTML Fundamentals": "html-fundamentals",
    "CSS & Responsive Design": "css-responsive-design",
    "JavaScript Basics": "javascript-basics",
    "Modern Website Development": "modern-website-development"
};

function readStoredJSON(key, fallback) {
    try {
        const storedValue = localStorage.getItem(key);
        return storedValue ? JSON.parse(storedValue) : fallback;
    } catch {
        return fallback;
    }
}

function updateProfileView(profile) {
    document.querySelectorAll("[data-profile-value]").forEach((valueElement) => {
        const fieldName = valueElement.dataset.profileValue;
        if (profile[fieldName] !== undefined) {
            valueElement.textContent = profile[fieldName];
        }
    });

    document.querySelectorAll("[data-profile-input]").forEach((input) => {
        const fieldName = input.dataset.profileInput;
        if (profile[fieldName] !== undefined) {
            input.value = profile[fieldName];
        }
    });

    const avatar = document.querySelector(".avatar");
    if (avatar && profile.name) {
        avatar.textContent = profile.name.trim().charAt(0).toUpperCase();
    }

    const studentName = document.querySelector(".student-name");
    if (studentName && profile.name) studentName.textContent = profile.name;
}

function toggleProfileEditing(isEditing) {
    document.querySelectorAll("[data-profile-value]").forEach((element) => {
        element.hidden = isEditing;
    });
    document.querySelectorAll("[data-profile-input]").forEach((element) => {
        element.hidden = !isEditing;
    });

    const editButton = document.querySelector(".edit-btn");
    const editActions = document.querySelector(".edit-actions");
    if (editButton) editButton.hidden = isEditing;
    if (editActions) editActions.hidden = !isEditing;
}

function initializePage() {
    const profile = readStoredJSON(profileStorageKey, {});
    updateProfileView(profile);

    const submittedAssignments = readStoredJSON(assignmentsStorageKey, []);
    document.querySelectorAll("[data-assignment]").forEach((button) => {
        if (submittedAssignments.includes(button.dataset.assignment)) {
            markAssignmentSubmitted(button);
        }
    });

    const completedLessons = readStoredJSON(completedLessonsStorageKey, []);
    document.querySelectorAll("[data-lesson-complete]").forEach((button) => {
        const lessonName = button.dataset.lessonComplete;
        if (completedLessons.includes(lessonName)) {
            renderLessonCompletion(button, lessonName);
        }
    });

}

async function getLearnerId() {
    const response = await fetch("/api/session", { headers: { "Accept": "application/json" } });
    const data = await response.json();
    if (!response.ok || !data.learner_id) {
        throw new Error(data.description || "Could not start a private demo session.");
    }
    localStorage.setItem(learnerIdStorageKey, data.learner_id);
    return data.learner_id;
}

function courseApiUrl(courseSlug, suffix = "") {
    return `/api/courses/${encodeURIComponent(courseSlug)}${suffix}`;
}

async function requestCourseApi(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.description || data.error || `Request failed (${response.status}).`);
    }
    return data;
}

function addLearnerIdToCourseLinks(learnerId) {
    document.querySelectorAll("[data-course-link]").forEach((link) => {
        const destination = new URL(link.href, window.location.href);
        destination.searchParams.set("learner_id", learnerId);
        link.href = destination.href;
    });
}

function renderCourseProgress(courseSlug, progress) {
    const courseRoot = document.querySelector(`[data-course-slug="${courseSlug}"]`);
    if (courseRoot) {
        const progressText = courseRoot.querySelector("[data-course-progress-text]");
        if (progressText) {
            progressText.textContent = `${progress.completed_count} / ${progress.total} lessons · ${progress.percent}%`;
        }

        const progressBar = courseRoot.querySelector("[data-course-progress-bar]");
        if (progressBar) {
            progressBar.setAttribute("aria-valuenow", progress.percent);
            const fill = progressBar.querySelector(".progress-fill");
            if (fill) fill.style.width = `${progress.percent}%`;
        }

        const completeLabel = courseRoot.querySelector("[data-course-complete-label]");
        if (completeLabel) completeLabel.hidden = !progress.course_complete;

        const lockedResources = courseRoot.querySelector("[data-resources-locked]");
        const unlockedResources = courseRoot.querySelector("[data-resources-unlocked]");
        if (lockedResources) lockedResources.hidden = progress.resources_unlocked;
        if (unlockedResources) unlockedResources.hidden = !progress.resources_unlocked;

        const completionLink = courseRoot.querySelector("[data-course-complete-link]");
        if (completionLink) completionLink.hidden = !progress.course_complete;

        courseRoot.querySelectorAll("[data-lesson-slug]").forEach((link) => {
            const isComplete = progress.completed_lessons.includes(link.dataset.lessonSlug);
            link.classList.toggle("is-complete", isComplete);
            const status = link.querySelector(".lesson-status-text");
            if (status) status.textContent = isComplete ? "Complete" : "Not started";
        });

        const latestAssessment = courseRoot.querySelector("[data-assessment-history]");
        if (latestAssessment && progress.latest_assessment) {
            const attempt = progress.latest_assessment;
            latestAssessment.hidden = false;
            latestAssessment.textContent =
                `Latest attempt: ${attempt.score}/${attempt.question_count}` +
                (attempt.passed ? " — Passed" : " — Keep practicing");
        }
    }

    const cardProgress = [...document.querySelectorAll("[data-card-progress]")]
        .find((element) => element.dataset.cardProgress === courseSlug);
    if (cardProgress) {
        cardProgress.textContent = `${progress.percent}%`;
        const card = cardProgress.closest(".course-box");
        const bar = card?.querySelector(".progress-bar");
        if (bar) {
            bar.setAttribute("aria-valuenow", progress.percent);
            const fill = bar.querySelector(".progress-fill");
            if (fill) fill.style.width = `${progress.percent}%`;
        }
    }
}

function renderQuizFeedback(container, results, fieldsets) {
    container.replaceChildren();
    results.forEach((result, index) => {
        const message = document.createElement("p");
        const answerText = fieldsets[index]
            ?.querySelectorAll(".choice-label span")[result.answer]?.textContent.trim();
        message.textContent =
            `${result.correct ? "Correct. " : `Review: ${answerText}. `}${result.explanation}`;
        message.classList.toggle("quiz-answer-correct", result.correct);
        message.classList.toggle("quiz-answer-review", !result.correct);
        container.append(message);
    });
}

async function refreshCourseProgress(courseSlug, learnerId) {
    const progress = await requestCourseApi(
        `${courseApiUrl(courseSlug, "/progress")}?learner_id=${encodeURIComponent(learnerId)}`
    );
    renderCourseProgress(courseSlug, progress);
}

async function migrateLegacyWebProgress(learnerId) {
    const storedLessons = readStoredJSON(completedLessonsStorageKey, []);
    if (!Array.isArray(storedLessons)) return;
    const legacyLessons = storedLessons.filter((name) => legacyWebLessonSlugs[name]);
    for (const lessonName of legacyLessons) {
        await requestCourseApi(
            `${courseApiUrl("web-development")}/lessons/${legacyWebLessonSlugs[lessonName]}/complete`,
            {
                method: "POST",
                body: JSON.stringify({ learner_id: learnerId })
            }
        );
    }
}

function showCourseError(error) {
    const errorMessage = error instanceof Error ? error.message : "The course request could not be completed.";
    document.querySelectorAll("[data-course-error]").forEach((element) => {
        element.textContent = errorMessage;
        element.hidden = false;
    });
}

async function initializeCourseLearning() {
    if (!document.querySelector("main[data-course-slug], [data-card-progress]")) return;

    let learnerId;
    try {
        learnerId = await getLearnerId();
    } catch (error) {
        showCourseError(error);
        return;
    }
    addLearnerIdToCourseLinks(learnerId);

    const courseRoot = document.querySelector("main[data-course-slug]");
    const cardSlugs = [...document.querySelectorAll("[data-card-progress]")]
        .map((element) => element.dataset.cardProgress)
        .filter((courseSlug) => courseSlug !== "web-development");
    const courseSlugs = new Set(cardSlugs);
    if (courseRoot) courseSlugs.add(courseRoot.dataset.courseSlug);

    courseSlugs.forEach((courseSlug) => {
        const syncLegacy = courseSlug === "web-development"
            ? migrateLegacyWebProgress(learnerId)
            : Promise.resolve();
        syncLegacy
            .then(() => refreshCourseProgress(courseSlug, learnerId))
            .catch(showCourseError);
    });

    document.querySelectorAll("[data-complete-lesson]").forEach((button) => {
        button.addEventListener("click", async () => {
            button.disabled = true;
            const message = button.closest(".lesson-finish-panel")
                ?.querySelector("[data-completion-message]");
            try {
                const result = await requestCourseApi(
                    `${courseApiUrl(button.dataset.courseSlug)}/lessons/${encodeURIComponent(button.dataset.lessonSlug)}/complete`,
                    {
                        method: "POST",
                        body: JSON.stringify({ learner_id: learnerId })
                    }
                );
                button.textContent = "Lesson Complete";
                if (message) message.textContent = "Lesson progress saved.";
                await refreshCourseProgress(button.dataset.courseSlug, learnerId);
                if (result.course_complete && message) {
                    message.textContent = "All required lessons are complete. Course resources are now unlocked.";
                }
            } catch (error) {
                button.disabled = false;
                if (message) message.textContent = `Could not save lesson progress: ${error.message}`;
            }
        });
    });

    document.querySelectorAll("[data-quiz-form]").forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const fieldsets = [...form.querySelectorAll("fieldset")];
            const answers = fieldsets.map((fieldset) => Number(
                fieldset.querySelector('input[type="radio"]:checked')?.value
            ));
            const resultMessage = form.querySelector("[data-quiz-result]");
            const feedback = form.querySelector("[data-quiz-feedback]");
            try {
                const result = await requestCourseApi(
                    `${courseApiUrl(form.dataset.courseSlug)}/lessons/${encodeURIComponent(form.dataset.lessonSlug)}/quiz`,
                    {
                        method: "POST",
                        body: JSON.stringify({ learner_id: learnerId, answers })
                    }
                );
                resultMessage.textContent = `You answered ${result.correct_count} of ${result.question_count} correctly.`;
                renderQuizFeedback(feedback, result.results, fieldsets);
            } catch (error) {
                resultMessage.textContent = `Could not check the quiz: ${error.message}`;
            }
        });
    });

    document.querySelectorAll("[data-assessment-form]").forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const fieldsets = [...form.querySelectorAll("fieldset")];
            const answers = fieldsets.map((fieldset) => Number(
                fieldset.querySelector('input[type="radio"]:checked')?.value
            ));
            const resultMessage = form.querySelector("[data-assessment-result]");
            const feedback = form.querySelector("[data-assessment-feedback]");
            try {
                const result = await requestCourseApi(
                    `${courseApiUrl(form.dataset.courseSlug)}/assessment`,
                    {
                        method: "POST",
                        body: JSON.stringify({ learner_id: learnerId, answers })
                    }
                );
                resultMessage.textContent = result.passed
                    ? `Passed: ${result.score}/${result.question_count}.`
                    : `Not passed yet: ${result.score}/${result.question_count}. ${result.passing_score} correct answers are needed.`;
                renderQuizFeedback(feedback, result.results, fieldsets);
                await refreshCourseProgress(form.dataset.courseSlug, learnerId);
            } catch (error) {
                resultMessage.textContent = `Could not submit the assessment: ${error.message}`;
            }
        });
    });
}

function markAssignmentSubmitted(button) {
    const assignment = button.closest(".assignment");
    const status = assignment?.querySelector(".status");
    if (status) {
        status.textContent = "Submitted";
        status.classList.remove("pending");
        status.classList.add("completed");
    }
    button.textContent = "Submitted";
    button.disabled = true;
}

function renderFeeStatus(isPaid) {
    const status = document.querySelector("[data-fee-status]");
    const payButton = document.querySelector("[data-pay-fee]");
    if (status) {
        status.textContent = isPaid ? "Paid" : "Pending";
        status.classList.toggle("paid", isPaid);
        status.classList.toggle("pending", !isPaid);
    }
    if (payButton) {
        payButton.textContent = isPaid ? "Paid" : "Pay ₹5,000 (Demo)";
        payButton.disabled = isPaid;
    }

    const paidAmount = document.querySelector("[data-paid-amount]");
    const pendingAmount = document.querySelector("[data-pending-amount]");
    if (paidAmount) paidAmount.textContent = isPaid ? "₹25,000" : "₹20,000";
    if (pendingAmount) pendingAmount.textContent = isPaid ? "₹0" : "₹5,000";
}

function formatRupees(paise) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(paise / 100);
}

function appendCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value;
    row.append(cell);
    return cell;
}

function renderPaymentHistory(history) {
    const body = document.querySelector("[data-payment-history]");
    if (!body) return;
    body.replaceChildren();
    if (!history.length) {
        const row = body.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 5;
        cell.textContent = "No payment attempts have been recorded.";
        return;
    }

    history.forEach((payment) => {
        const row = body.insertRow();
        appendCell(row, payment.created_at);
        appendCell(row, formatRupees(payment.amount_paise));
        appendCell(row, payment.transaction_reference || "Not assigned");
        appendCell(row, payment.status === "paid" ? "Paid — Demo (no real money)" : payment.status);
        const receiptCell = row.insertCell();
        if (payment.status === "paid" && payment.receipt_reference) {
            const receipt = document.createElement("a");
            receipt.href = `/api/payments/${encodeURIComponent(payment.id)}/receipt`;
            receipt.textContent = "Download receipt";
            receiptCell.append(receipt);
        } else {
            receiptCell.textContent = "Unavailable until successful";
        }
    });
}

async function loadFeeSummary() {
    const summary = await requestCourseApi("/api/fees");
    document.querySelector("[data-total-fee]").textContent = formatRupees(summary.total_paise);
    document.querySelector("[data-paid-fee]").textContent = formatRupees(summary.paid_paise);
    document.querySelector("[data-pending-fee]").textContent = formatRupees(summary.pending_paise);
    document.querySelector("[data-fee-due-date]").textContent =
        new Date(`${summary.due_date}T00:00:00`).toLocaleDateString();
    const daysRemaining = Math.ceil(
        (new Date(`${summary.due_date}T00:00:00`).getTime() - new Date().setHours(0, 0, 0, 0))
        / 86400000
    );
    const reminder = document.querySelector("[data-fee-reminder]");
    reminder.textContent = summary.pending_paise === 0
        ? "No balance is currently due."
        : daysRemaining < 0
            ? "The listed due date has passed. Contact the administrator for next steps."
            : daysRemaining <= 7
                ? `Reminder: payment is due in ${daysRemaining} day(s).`
                : `Payment is due in ${daysRemaining} day(s).`;

    const select = document.getElementById("paymentMethod");
    const button = document.getElementById("payNow");
    select.replaceChildren();
    summary.payment_methods.forEach((method) => {
        const option = document.createElement("option");
        option.value = method;
        option.textContent = method === "demo"
            ? "Demo payment — NO REAL MONEY IS CHARGED"
            : method;
        select.append(option);
    });
    select.disabled = !summary.payment_methods.length || summary.pending_paise === 0;
    button.disabled = select.disabled;
    button.textContent = summary.pending_paise === 0 ? "No balance due" : "Pay Now (Demo)";
    renderPaymentHistory(summary.history);
    return summary;
}

function initializeFeeManagement() {
    const button = document.getElementById("payNow");
    if (!button) return;
    const message = document.getElementById("feeMessage");
    let activeRequestKey = null;
    loadFeeSummary().catch((error) => {
        message.textContent = `Fees could not be loaded. Refresh the page or contact support. ${error.message}`;
    });

    button.addEventListener("click", async () => {
        if (button.disabled) return;
        button.disabled = true;
        activeRequestKey ||= crypto.randomUUID();
        message.textContent = "Submitting a demo payment request…";
        try {
            const result = await requestCourseApi("/api/payments", {
                method: "POST",
                body: JSON.stringify({
                    method: document.getElementById("paymentMethod").value,
                    idempotency_key: activeRequestKey
                })
            });
            activeRequestKey = null;
            const status = result.payment.status;
            message.textContent = status === "paid"
                ? "DEMO — NO REAL MONEY IS CHARGED. The server recorded this demo payment as successful."
                : `Demo payment status: ${status}. No real payment was made. Check history before retrying.`;
            await loadFeeSummary();
        } catch (error) {
            message.textContent = `Payment was not confirmed. Check payment history before retrying. ${error.message}`;
            try {
                await loadFeeSummary();
            } catch {
                button.disabled = true;
            }
        }
    });
}

function renderSupportTickets(tickets) {
    const body = document.querySelector("[data-support-history]");
    if (!body) return;
    body.replaceChildren();
    if (!tickets.length) {
        const row = body.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 5;
        cell.textContent = "No support requests yet.";
        return;
    }
    tickets.forEach((ticket) => {
        const row = body.insertRow();
        appendCell(row, `#${ticket.id}`);
        appendCell(row, ticket.category.replaceAll("_", " "));
        appendCell(row, ticket.created_at);
        appendCell(row, ticket.status);
        appendCell(row, ticket.description);
    });
}

async function loadSupportTickets() {
    const result = await requestCourseApi("/api/support");
    renderSupportTickets(result.tickets);
}

function initializeSupportCenter() {
    const form = document.querySelector("[data-support-form]");
    if (!form) return;
    const message = form.querySelector("[data-support-message]");
    loadSupportTickets().catch((error) => {
        message.textContent = `Support requests could not be loaded. Refresh this page. ${error.message}`;
    });
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const data = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        try {
            const result = await requestCourseApi("/api/support", {
                method: "POST",
                body: JSON.stringify({
                    category: data.get("category"),
                    description: data.get("description")
                })
            });
            message.textContent = `Request #${result.ticket_id} submitted. Status: ${result.status}.`;
            form.reset();
            await loadSupportTickets();
        } catch (error) {
            message.textContent = `Request not submitted. Check the description and try again. ${error.message}`;
        } finally {
            submitButton.disabled = false;
        }
    });
}

function logout() {
    window.location.href = "/logout";
}

function goDashboard() {
    window.location.href = "dashboard.html";
}

function showPasswordHelp() {
    const message = document.getElementById("loginMessage");
    if (message) message.textContent = "Password recovery is not enabled in this demo.";
}

function submitAssignment(name) {
    const button = [...document.querySelectorAll("[data-assignment]")]
        .find((item) => item.dataset.assignment === name);
    if (!button) return;

    markAssignmentSubmitted(button);
    const submittedAssignments = readStoredJSON(assignmentsStorageKey, []);
    if (!submittedAssignments.includes(name)) submittedAssignments.push(name);
    localStorage.setItem(assignmentsStorageKey, JSON.stringify(submittedAssignments));
}

function editProfile() {
    toggleProfileEditing(true);
}

function saveProfile() {
    const inputs = [...document.querySelectorAll("[data-profile-input]")];
    inputs.forEach((input) => {
        input.value = input.value.trim();
    });
    if (inputs.some((input) => !input.reportValidity())) return;

    const profile = Object.fromEntries(inputs.map((input) => [
        input.dataset.profileInput,
        input.value.trim()
    ]));
    localStorage.setItem(profileStorageKey, JSON.stringify(profile));
    updateProfileView(profile);
    toggleProfileEditing(false);
}

function cancelProfileEdit() {
    const displayedValues = Object.fromEntries(
        [...document.querySelectorAll("[data-profile-value]")].map((element) => [
            element.dataset.profileValue,
            element.textContent.trim()
        ])
    );
    updateProfileView({
        ...displayedValues,
        ...readStoredJSON(profileStorageKey, {})
    });
    toggleProfileEditing(false);
}

function renderLessonCompletion(button, name) {
    button.disabled = true;
    button.textContent = "Lesson Complete";
    const message = button.closest(".lesson-card")?.querySelector(".lesson-message")
        || document.getElementById("lessonMessage");
    if (message) message.textContent = `${name} marked complete.`;
}

function completeLesson(name) {
    const button = [...document.querySelectorAll("[data-lesson-complete]")]
        .find((item) => item.dataset.lessonComplete === name);
    if (!button) return;

    const completedLessons = readStoredJSON(completedLessonsStorageKey, []);
    if (!completedLessons.includes(name)) completedLessons.push(name);
    localStorage.setItem(completedLessonsStorageKey, JSON.stringify(completedLessons));
    renderLessonCompletion(button, name);
}

document.addEventListener("DOMContentLoaded", () => {
    initializePage();
    initializeCourseLearning();
    initializeFeeManagement();
    initializeSupportCenter();

    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const message = document.getElementById("loginMessage");
            try {
                await requestCourseApi("/api/demo-session", {
                    method: "POST",
                    body: JSON.stringify({ email: document.getElementById("email").value })
                });
                window.location.href = "dashboard.html";
            } catch (error) {
                if (message) message.textContent = error.message;
            }
        });
    }

    const signupForm = document.getElementById("signupForm");
    if (signupForm) {
        signupForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const profile = readStoredJSON(profileStorageKey, {});
            profile.name = document.getElementById("name").value.trim();
            profile.email = document.getElementById("email").value.trim();
            try {
                await requestCourseApi("/api/demo-session", {
                    method: "POST",
                    body: JSON.stringify(profile)
                });
                localStorage.setItem(profileStorageKey, JSON.stringify(profile));
                window.location.href = "dashboard.html";
            } catch (error) {
                const message = document.getElementById("signupMessage");
                if (message) message.textContent = error.message;
            }
        });
    }
});