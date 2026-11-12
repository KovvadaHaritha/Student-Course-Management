RUBRIC = [
    {"criterion": "Functionality", "weight_percent": 30, "description": "Required behavior and interactions work as specified."},
    {"criterion": "Correctness", "weight_percent": 25, "description": "The solution follows the task and handles relevant cases."},
    {"criterion": "Code or design quality", "weight_percent": 15, "description": "Structure, accessibility, consistency and maintainability."},
    {"criterion": "Creativity", "weight_percent": 10, "description": "Thoughtful choices that improve the solution."},
    {"criterion": "Documentation", "weight_percent": 10, "description": "Clear notes explain decisions and how to use the work."},
    {"criterion": "Testing and presentation", "weight_percent": 10, "description": "Evidence, testing and a clear presentation of the result."},
]


def question(prompt, options, correct, explanation, marks=1):
    return {
        "prompt": prompt,
        "options": options,
        "correct": correct,
        "explanation": explanation,
        "marks": marks,
    }


def mcq(slug, title, description, lesson_position, questions, time_limit=20):
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "assessment_type": "mcq",
        "lesson_position": lesson_position,
        "objectives": ["Apply the core concepts from the related lesson.", "Explain the choice using evidence from the topic."],
        "instructions": "Answer every question. Your answers are saved in this browser session as you work. Submit only when ready; the score and explanations appear after submission.",
        "maximum_marks": sum(item["marks"] for item in questions),
        "passing_marks": (sum(item["marks"] for item in questions) * 70 + 99) // 100,
        "time_limit_minutes": time_limit,
        "attempt_limit": 3,
        "deadline": None,
        "rubric": [{"criterion": "Correct answers", "weight_percent": 100, "description": "Automatically scored from the submitted answer key."}],
        "questions": questions,
    }


def practical(slug, title, description, assessment_type, lesson_position, task):
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "assessment_type": assessment_type,
        "lesson_position": lesson_position,
        "objectives": ["Build and explain a solution to the task.", "Include enough evidence for an instructor to review your decisions."],
        "instructions": (
            f"{task} Write a concise explanation of your approach in the submission field and attach your work if appropriate. "
            "This submission is not automatically graded; its status remains Awaiting instructor review until an evaluator records a result."
        ),
        "maximum_marks": 100,
        "passing_marks": 70,
        "time_limit_minutes": None,
        "attempt_limit": 3,
        "deadline": None,
        "rubric": RUBRIC,
        "questions": [{
            "prompt": "Describe your approach, key decisions and how you tested or reviewed the work.",
            "options": [],
            "correct": None,
            "explanation": "",
            "marks": 100,
        }],
    }


ASSESSMENTS = {
    "web-development": [
        mcq("html-structure-quiz", "HTML Structure Quiz", "Check semantic HTML structure and accessible document basics.", 1, [
            question("Which element represents the main content of a page?", ["<main>", "<aside>", "<footer>"], 0, "<main> identifies the dominant content and should be used once per page."),
            question("What should a label's for value match?", ["The input id", "The input name only", "The form action"], 0, "A matching id programmatically associates the label with its control."),
            question("Which heading order is best for a page with one main topic and two sections?", ["h1, then h2 headings", "Several h1 headings for styling", "Start at h4"], 0, "Heading levels express document hierarchy, not visual size."),
        ]),
        mcq("css-selectors-layout-quiz", "CSS Selectors and Layouts Quiz", "Practice selector specificity, box sizing and layout choices.", 2, [
            question("Which selector targets an element with id=\"notice\"?", [".notice", "#notice", "notice"], 1, "The # prefix selects an element by id."),
            question("Which layout tool is suited to arranging items in one dimension?", ["Flexbox", "CSS Grid only", "The float property"], 0, "Flexbox is designed for one-dimensional row or column layouts."),
            question("What does box-sizing: border-box do?", ["Includes padding and border in the declared size", "Removes padding", "Sets all elements to fixed width"], 0, "The declared width includes content, padding and border."),
        ]),
        mcq("javascript-fundamentals-quiz", "JavaScript Fundamentals Quiz", "Check variables, functions and browser events.", 3, [
            question("Which declaration can be reassigned but is block scoped?", ["let", "const", "class"], 0, "let creates a block-scoped binding that can be reassigned."),
            question("What does addEventListener do?", ["Registers a handler for an event", "Loads a CSS file", "Creates a database table"], 0, "It attaches a callback to an event target."),
            question("Which value represents an explicitly absent value?", ["null", "false", "0"], 0, "null is the intentional absence of a value."),
        ]),
        practical("responsive-website-practical", "Responsive Website Practical", "Create and explain a responsive page layout.", "practical", 2, "Build a small accessible page that works at mobile and desktop widths."),
        practical("final-portfolio-website", "Final Portfolio Website Project", "Submit a finished responsive portfolio website.", "final", 4, "Create a multi-section portfolio with semantic HTML, responsive CSS, useful interactions, testing notes and setup instructions."),
    ],
    "python-programming": [
        mcq("variables-data-types-quiz", "Variables and Data Types Quiz", "Check assignment, types, input and conversion.", 2, [
            question("What type does input() return?", ["str", "int", "bool"], 0, "input() returns text; convert it explicitly before numeric calculations."),
            question("Which value is immutable?", ["tuple", "list", "set"], 0, "A tuple cannot be changed after it is created."),
            question("What does int(\"12\") return?", ["12", "\"12\"", "12.0"], 0, "int converts a valid integer string to the integer value 12."),
        ]),
        mcq("conditions-loops-quiz", "Conditions and Loops Quiz", "Practice branching and iteration.", 3, [
            question("Which keyword begins an alternative branch after if?", ["elif", "loop", "switch"], 0, "elif adds another condition to an if/else chain."),
            question("What does range(3) produce?", ["0, 1, 2", "1, 2, 3", "0, 1, 2, 3"], 0, "The stop value is excluded, so range(3) yields 0 through 2."),
            question("Which loop is useful when the number of items is known?", ["for", "while", "try"], 0, "A for loop iterates over a sequence or iterable."),
        ]),
        mcq("functions-data-structures-quiz", "Functions and Data Structures Quiz", "Review reusable functions and collection behavior.", 5, [
            question("What does return do in a function?", ["Sends a result to the caller", "Prints automatically", "Repeats the function"], 0, "return passes a value back to the caller and ends that function call."),
            question("Which collection stores unique values?", ["set", "list", "tuple"], 0, "A set contains distinct hashable values."),
            question("What does a dictionary store?", ["Key-value pairs", "Only ordered numbers", "Unique positions without values"], 0, "Dictionaries map keys to values."),
        ]),
        practical("file-exceptions-exercise", "File Handling and Exceptions Exercise", "Build a safe file-processing utility.", "coding", 7, "Write a small program that reads structured text, handles a missing or malformed file with a helpful message, and documents how to run it."),
        practical("final-python-application", "Final Python Application Project", "Submit a documented Python application.", "final", 12, "Build a useful application such as a student manager or expense tracker with validation, persistent file data, tests and a clear README."),
    ],
    "ui-ux-design": [
        mcq("design-principles-quiz", "Design Principles Quiz", "Review hierarchy, consistency and accessible design choices.", 7, [
            question("What does visual hierarchy help a user do?", ["Notice important content in a useful order", "Use more colors", "Avoid all whitespace"], 0, "Hierarchy guides attention to the most important information."),
            question("Why check color contrast?", ["To keep text readable for more people", "To make every color identical", "To remove typography"], 0, "Sufficient contrast supports readable interfaces, including for low-vision users."),
            question("What is a reusable design component?", ["A documented interface part used consistently", "A screenshot with no structure", "A one-time decoration"], 0, "Reusable components improve consistency and make changes easier."),
        ]),
        practical("color-typography-task", "Color and Typography Task", "Create an accessible visual style sample.", "practical", 7, "Present a small type scale and color palette with contrast checks and short rationale."),
        practical("wireframe-creation", "Wireframe Creation", "Create and explain a task-focused wireframe.", "practical", 5, "Wireframe a student task flow, label the key states and explain how the layout supports the user's goal."),
        practical("figma-components-autolayout", "Figma Components and Auto Layout Practical", "Demonstrate reusable interface components.", "practical", 6, "Create a small component set with clear variants and responsive auto-layout behavior."),
        practical("prototype-interaction", "Prototype Interaction Submission", "Submit an interactive flow for review.", "project", 9, "Prototype a complete user flow with meaningful transitions, feedback and an accessible path through the primary task."),
        practical("final-mobile-app-design", "Final Mobile Application Design", "Submit a complete mobile app design project.", "final", 12, "Design a mobile learning app with research-backed flows, wireframes, reusable components, a clickable prototype and usability findings."),
    ],
    "data-science": [
        mcq("python-data-analysis-quiz", "Python and Data Analysis Quiz", "Review data types and basic analysis concepts.", 3, [
            question("What is a NumPy array primarily designed for?", ["Efficient numerical operations", "Styling web pages", "Managing browser cookies"], 0, "NumPy arrays support efficient vectorized numerical computations."),
            question("What is a Pandas DataFrame?", ["A labeled two-dimensional table", "A chart-only object", "A database server"], 0, "A DataFrame organizes labeled rows and columns."),
            question("Why inspect data before analysis?", ["To understand structure, types and quality", "To remove all rows", "To guarantee a prediction"], 0, "Initial inspection reveals columns, types, missing values and possible issues."),
        ]),
        practical("pandas-data-cleaning-task", "Pandas Data-Cleaning Task", "Clean a small dataset and explain decisions.", "practical", 5, "Document how you handled missing values, duplicates and suspicious values; include before/after checks."),
        practical("data-visualization-assignment", "Data Visualization Assignment", "Create a clear chart with an evidence-based interpretation.", "practical", 9, "Choose an appropriate chart, label it clearly and explain what the data supports and what it does not prove."),
        mcq("statistics-fundamentals-assessment", "Statistics Fundamentals Assessment", "Check probability, summary statistics and interpretation.", 2, [
            question("What does the median describe?", ["The middle value after ordering", "The most frequent value", "The total of all values"], 0, "The median is the central ordered value and is less sensitive to extreme values than the mean."),
            question("What does a probability of 0 mean?", ["The event is impossible in the model", "The event is certain", "The sample is incomplete"], 0, "A probability of zero represents an impossible event under the model."),
            question("Does correlation alone establish causation?", ["No", "Yes, always", "Only with a bar chart"], 0, "Association alone does not establish that one variable causes another."),
        ]),
        practical("machine-learning-model-practical", "Machine Learning Model Practical", "Build and evaluate a simple model for instructor review.", "coding", 11, "Describe the target, train/test split, baseline, chosen metrics and limitations. Do not include private or sensitive data."),
        practical("final-data-analysis-project", "Final Data Analysis Project", "Submit an end-to-end data analysis project.", "final", 14, "Analyze a suitable dataset, document cleaning and exploratory steps, create interpretable charts, evaluate a model if appropriate, and state limitations."),
    ],
}
