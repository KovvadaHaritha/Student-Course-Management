"""Structured course material for the guided learning routes."""


def quiz(question, options, answer, explanation):
    rotation = sum(map(ord, question)) % len(options)
    options = options[rotation:] + options[:rotation]
    return {
        "question": question,
        "options": options,
        "answer": (answer - rotation) % len(options),
        "explanation": explanation,
    }


PYTHON_MODULES = [
    {
        "title": "Introduction to Python and installation",
        "lessons": ["What Python is used for", "Install Python and run your first program"],
        "objectives": ["Describe where Python is useful", "Run a script and use the interactive prompt"],
        "explanation": "Python is a general-purpose language whose readable syntax is useful for automation, web services, analysis, and education. A Python installation includes an interpreter that reads and runs your instructions.",
        "steps": ["Choose a supported Python 3 installation for your operating system.", "Check the installation with `python --version` (or `python3 --version`).", "Save `print('Hello, world!')` in a `.py` file and run it from a terminal."],
        "real_world": "A small Python script can rename a folder of photos or produce a daily report without repeating the work by hand.",
        "example": "print('Hello, world!')\nprint(2 + 3)",
        "exercise": "Install or open Python, run the two-line example, then change it to print your name and one goal for learning Python.",
        "quiz": [
            quiz("What runs a Python source file?", ["A Python interpreter", "A spreadsheet", "A CSS selector"], 0, "The interpreter reads Python statements and executes them."),
            quiz("Which command commonly checks the installed Python 3 version?", ["python --version", "python --remove", "python --format"], 0, "The version flag reports which interpreter the command starts."),
        ],
    },
    {
        "title": "Variables, data types, input/output and operators",
        "lessons": ["Names, values, and core data types", "Input, output, conversion, and operators"],
        "objectives": ["Choose strings, numbers, and booleans for data", "Read user input and calculate with operators"],
        "explanation": "A variable is a name that refers to a value. Python commonly uses `str` for text, `int` for whole numbers, `float` for decimals, and `bool` for true/false values. `input()` returns text, so numeric input needs conversion.",
        "steps": ["Assign values with `=` and use clear names.", "Use `type(value)` while learning to inspect a value's type.", "Convert input with `int()` or `float()` before arithmetic, then display results with `print()` or an f-string."],
        "real_world": "A checkout tool reads a quantity and price, multiplies them, and displays the total.",
        "example": "item = input('Item: ')\nquantity = int(input('Quantity: '))\nprice = 2.50\ntotal = quantity * price\nprint(f'{quantity} {item}(s): ${total:.2f}')",
        "exercise": "Ask for two numbers, convert them to floats, and print their sum, difference, product, and quotient. Decide how to handle a zero divisor.",
        "quiz": [
            quiz("What type does `input()` return before conversion?", ["str", "int", "bool"], 0, "`input()` returns the characters entered as a string."),
            quiz("Which operator calculates a remainder?", ["%", "**", "//"], 0, "The modulo operator `%` gives the remainder after division."),
        ],
    },
    {
        "title": "Conditional statements",
        "lessons": ["Boolean comparisons and if/elif/else", "Combining conditions and validating input"],
        "objectives": ["Select a branch with comparisons", "Combine conditions and handle boundary cases"],
        "explanation": "A conditional lets a program choose a path. Python evaluates an `if` condition as true or false, checks `elif` branches in order, and uses `else` when none matched. Indentation defines each block.",
        "steps": ["Write the condition after `if` and finish it with a colon.", "Indent the statements that belong to that branch.", "Order ranges carefully, then test values below, at, and above each boundary."],
        "real_world": "A shop may apply free delivery when an order reaches a minimum amount and otherwise show the remaining amount.",
        "example": "total = 42\nif total >= 50:\n    print('Free delivery')\nelse:\n    print(f'Add ${50 - total:.2f} for free delivery')",
        "exercise": "Write a score classifier with pass, merit, and distinction ranges. Test the exact boundary values and reject scores outside 0–100.",
        "quiz": [
            quiz("Which keyword handles a condition after an earlier `if` was false?", ["elif", "repeat", "define"], 0, "`elif` checks another condition in the same decision chain."),
            quiz("Why test values exactly at range boundaries?", ["To find off-by-one errors", "To make Python run faster", "To change a string into a number"], 0, "Boundary tests reveal missing or overlapping comparisons."),
        ],
    },
    {
        "title": "Loops",
        "lessons": ["Repeat over sequences with for", "Use while loops and control repetition"],
        "objectives": ["Choose `for` or `while` for a task", "Avoid accidental infinite loops"],
        "explanation": "A `for` loop visits each item in an iterable. A `while` loop repeats as long as a condition is true. `break` exits a loop and `continue` skips to its next iteration.",
        "steps": ["Use `for item in items` when the values are already available.", "Use `range()` for a known number of repetitions.", "For `while`, update the state that controls the condition and include a clear stopping case."],
        "real_world": "A program can process every transaction in a day's list and add only the transactions that meet a rule.",
        "example": "prices = [3.50, 2.00, 4.25]\ntotal = 0\nfor price in prices:\n    total += price\nprint(f'Total: ${total:.2f}')",
        "exercise": "Use a loop to find the largest number in a list without calling `max()`. Then explain how your loop behaves for an empty list.",
        "quiz": [
            quiz("When is a `for` loop a natural choice?", ["Visiting each item in a collection", "Defining a class", "Catching an exception"], 0, "`for` iterates through items in an iterable."),
            quiz("What must a `while` loop eventually do to avoid an infinite loop?", ["Make its condition false or exit", "Change every value to a string", "Import a package"], 0, "The loop needs progress toward a stopping condition or an explicit exit."),
        ],
    },
    {
        "title": "Strings and data structures: lists, tuples, sets and dictionaries",
        "lessons": ["Work with strings, lists, and tuples", "Use sets and dictionaries to organize data"],
        "objectives": ["Select a collection based on its behavior", "Read, update, and iterate over collection values"],
        "explanation": "Strings hold text. Lists are ordered and changeable; tuples are ordered and fixed after creation; sets keep unique values; dictionaries map unique keys to values. Choosing a fitting structure makes later operations simpler.",
        "steps": ["Create a collection that matches the data and whether it should change.", "Access sequence items by index or dictionary items by key.", "Use loops and methods such as `append`, `get`, or `add` to process values."],
        "real_world": "An inventory can use a dictionary from product name to stock count and a set of unique category names.",
        "example": "stock = {'notebook': 12, 'pen': 30}\nstock['pen'] -= 1\ncategories = {'stationery', 'sale', 'stationery'}\nprint(stock['pen'], categories)",
        "exercise": "Count the words in a sentence with a dictionary. Use a set to report how many different words appear.",
        "quiz": [
            quiz("Which collection removes duplicate values?", ["set", "list", "tuple"], 0, "A set contains unique hashable values."),
            quiz("Which structure maps keys to values?", ["dict", "tuple", "str"], 0, "A dictionary stores key/value associations."),
        ],
    },
    {
        "title": "Functions, parameters, return values and recursion",
        "lessons": ["Design reusable functions", "Understand recursion and its base case"],
        "objectives": ["Separate a task into functions with inputs and outputs", "Explain why recursion needs a base case"],
        "explanation": "A function names a reusable operation. Parameters receive input, and `return` sends a result back to the caller. A recursive function calls itself on a smaller problem and must have a base case that stops the calls.",
        "steps": ["Choose one responsibility and give the function a clear name.", "Pass changing data through parameters instead of relying on hidden state.", "Return computed results; for recursion, define and test the smallest case first."],
        "real_world": "A gradebook can reuse one function to calculate an average for every student's score list.",
        "example": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))",
        "exercise": "Write a function that converts minutes to hours and remaining minutes. Then write a recursive countdown with a zero stopping case.",
        "quiz": [
            quiz("What does `return` do in a function?", ["Sends a result to the caller", "Repeats the function forever", "Imports a module"], 0, "`return` ends the current function call and provides its result."),
            quiz("What prevents a recursive function from calling itself forever?", ["A base case", "A global variable", "A print statement"], 0, "The base case returns without making another recursive call."),
        ],
    },
    {
        "title": "Modules, packages and exception handling",
        "lessons": ["Import and organize reusable modules", "Handle expected errors clearly"],
        "objectives": ["Import standard-library and project modules", "Catch specific exceptions and preserve useful feedback"],
        "explanation": "A module is a Python file that can be imported. Packages group modules. Exceptions represent errors during execution; `try/except` lets a program respond to expected failures without hiding unrelated bugs.",
        "steps": ["Import only the names or module you need.", "Keep related code in modules with clear responsibilities.", "Wrap the smallest risky operation in `try`, catch a specific exception, and give the user a helpful response."],
        "real_world": "A file import screen can catch a missing-file error and ask the user to choose another file.",
        "example": "try:\n    age = int(input('Age: '))\nexcept ValueError:\n    print('Enter a whole number, such as 18.')\nelse:\n    print(f'Next year you will be {age + 1}.')",
        "exercise": "Import `statistics` to calculate a mean. Add input validation for an empty list and a list containing non-numeric values.",
        "quiz": [
            quiz("Why should code catch a specific exception rather than every possible exception?", ["Unexpected bugs should remain visible", "Specific catches remove all errors", "Python requires one catch per line"], 0, "Narrow handling avoids disguising programming errors as normal input problems."),
            quiz("What is a Python module?", ["A Python file that can be imported", "A loop condition", "A database row"], 0, "A module is a file containing Python definitions and statements."),
        ],
    },
    {
        "title": "Object-oriented programming: classes, objects, inheritance and polymorphism",
        "lessons": ["Create classes, objects, and methods", "Use inheritance and polymorphic behavior carefully"],
        "objectives": ["Model related data and behavior with a class", "Override a method while preserving a clear interface"],
        "explanation": "A class describes a kind of object; an instance stores its own state. Methods are functions attached to a class. Inheritance can share or specialize behavior, while polymorphism lets different objects respond to the same operation in their own way.",
        "steps": ["Identify the data and actions that belong together.", "Initialize instance state with `__init__` and `self`.", "Use inheritance only for a true 'is a' relationship; override behavior behind a consistent method."],
        "real_world": "A school system can model `Course` and specialized course types that share a title and expose a common `summary()` method.",
        "example": "class Course:\n    def __init__(self, title):\n        self.title = title\n\n    def summary(self):\n        return f'Course: {self.title}'\n\ncourse = Course('Python')\nprint(course.summary())",
        "exercise": "Create a `BankAccount` class with a balance and a deposit method that rejects non-positive amounts. Add a subclass only if it represents a genuine specialized account.",
        "quiz": [
            quiz("What is an instance?", ["An object created from a class", "A Python package", "A comparison operator"], 0, "An instance is a concrete object with state described by its class."),
            quiz("What does polymorphism allow?", ["Different object types to support the same operation", "A list to contain only integers", "A module to import itself"], 0, "Polymorphism allows callers to use a shared interface with type-specific behavior."),
        ],
    },
    {
        "title": "File handling: text, CSV and JSON",
        "lessons": ["Read and write text files safely", "Parse CSV and JSON data"],
        "objectives": ["Use context managers for file lifetime", "Choose CSV or JSON for a data exchange task"],
        "explanation": "Files preserve information after a program exits. The `with open(...)` pattern closes a file reliably. CSV stores rows and columns; JSON represents nested data with familiar objects, arrays, strings, numbers, and booleans.",
        "steps": ["Choose a path and an explicit text encoding such as UTF-8.", "Open with the correct mode and use `with` so cleanup is automatic.", "Use the `csv` or `json` standard-library module to parse structured formats."],
        "real_world": "An expense tracker can save transactions to CSV for spreadsheets and export settings or nested records to JSON.",
        "example": "import json\nrecord = {'item': 'Notebook', 'amount': 4.5}\nwith open('expense.json', 'w', encoding='utf-8') as file:\n    json.dump(record, file, indent=2)",
        "exercise": "Write three expense records to a CSV file and read them back. Handle a missing file with a clear message.",
        "quiz": [
            quiz("What benefit does `with open(...)` provide?", ["It closes the file when the block ends", "It encrypts the file", "It converts CSV to JSON"], 0, "The context manager handles closing even if an exception occurs."),
            quiz("Which standard-library module writes JSON?", ["json", "csv", "pathlib"], 0, "`json.dump` and `json.dumps` serialize Python values as JSON."),
        ],
    },
    {
        "title": "NumPy and Pandas",
        "lessons": ["Use NumPy arrays for numerical work", "Explore tabular data with Pandas"],
        "objectives": ["Explain vectorized array operations", "Select and summarize DataFrame columns"],
        "explanation": "NumPy arrays support efficient numerical operations across many values. Pandas builds labeled `Series` and table-like `DataFrame` objects on top of common data tools, making filtering and summarizing datasets easier.",
        "steps": ["Install packages in the active environment and import them by convention.", "Create an array or DataFrame from known values.", "Inspect shape, columns, and missing values before filtering or calculating."],
        "real_world": "A school analyst can compare scores across subjects and calculate a class average from a CSV dataset.",
        "example": "import numpy as np\nimport pandas as pd\nscores = pd.DataFrame({'student': ['Asha', 'Ben'], 'score': [88, 74]})\nprint(scores['score'].mean())\nprint(np.array([1, 2, 3]) * 2)",
        "exercise": "Load a small CSV into a DataFrame, display its shape and summary, then filter rows above the score average.",
        "quiz": [
            quiz("What is a Pandas DataFrame?", ["A labeled two-dimensional table", "A Python exception", "A chart title"], 0, "A DataFrame holds tabular data with labeled rows and columns."),
            quiz("What is vectorization useful for?", ["Applying numerical operations to arrays efficiently", "Naming variables automatically", "Opening a browser tab"], 0, "Array operations work over collections without writing a Python loop for every element."),
        ],
    },
    {
        "title": "Matplotlib and basic data visualization",
        "lessons": ["Choose a chart and encode data clearly", "Build, label, and interpret a Matplotlib chart"],
        "objectives": ["Match chart types to questions", "Add labels and avoid misleading visual choices"],
        "explanation": "A chart communicates a pattern using visual marks. A bar chart compares categories, a line chart shows change across ordered time, and a scatter plot shows relationships between two numeric variables. Labels and honest scales provide context.",
        "steps": ["State the comparison or trend the reader should see.", "Choose a chart type that matches the data and question.", "Label axes, units, and title; inspect the chart for misleading scales or clutter."],
        "real_world": "A teacher can use a bar chart to compare average marks by subject and a line chart to show attendance over a term.",
        "example": "import matplotlib.pyplot as plt\nsubjects = ['Math', 'Science', 'English']\nmeans = [78, 84, 81]\nplt.bar(subjects, means)\nplt.ylabel('Average score')\nplt.title('Average scores by subject')\nplt.show()",
        "exercise": "Plot monthly study hours as a line chart. Add a title, labeled axes, and a short written observation about one trend.",
        "quiz": [
            quiz("Which chart is usually suitable for change over time?", ["Line chart", "Pie chart with one slice", "Unlabeled scatter plot"], 0, "A line chart connects ordered time points to make trends visible."),
            quiz("Why should an axis include units?", ["Readers need to know what values mean", "Units increase the number of data points", "Matplotlib requires currency"], 0, "Units make the scale interpretable and prevent ambiguity."),
        ],
    },
    {
        "title": "Practical projects: calculator, expense tracker and student management system",
        "lessons": ["Plan and build a safe command-line calculator", "Design persistent expense and student records"],
        "objectives": ["Break a project into small functions and test cases", "Select data structures and persistence for a small app"],
        "explanation": "A practical program combines input, decisions, reusable functions, collections, and error handling. Start with a small working version, keep data separate from interface code, and test normal and invalid cases.",
        "steps": ["Write down the user tasks and the data each task needs.", "Implement one action at a time as a small function.", "Validate input, save data in a suitable format, and test expected and error cases."],
        "real_world": "A student management tool can add a student, update a course, and list records without editing a spreadsheet manually.",
        "example": "def calculate(left, operator, right):\n    if operator == '+':\n        return left + right\n    if operator == '*':\n        return left * right\n    raise ValueError('Choose + or *')\n\nprint(calculate(4, '+', 3))",
        "exercise": "Sketch the menu and data model for an expense tracker. Implement adding and listing expenses, then add a CSV export and tests for invalid amounts.",
        "quiz": [
            quiz("What is a good first step before implementing a project?", ["List user tasks and required data", "Write one very long function", "Ignore invalid input"], 0, "Clear requirements give the project a testable scope."),
            quiz("Why test invalid input?", ["It checks the program's failure behavior", "It makes every feature unnecessary", "It replaces documentation"], 0, "Real users make mistakes; predictable validation keeps the program understandable."),
        ],
    },
]


UI_UX_MODULES = [
    {
        "title": "Introduction to UI, UX and the design process",
        "lessons": ["Distinguish interface design from user experience", "Run a user-centered design cycle"],
        "objectives": ["Explain UI and UX in plain language", "Use research, design, test, and iteration as a cycle"],
        "explanation": "User interface (UI) is the surface people interact with; user experience (UX) includes the complete experience of trying to reach a goal. Good design balances user needs, business goals, and technical constraints.",
        "steps": ["Describe the user and task without jumping to a visual solution.", "Explore the problem with research and rough alternatives.", "Prototype a promising direction, test it, and revise using evidence."],
        "real_world": "A transit app is not successful only because its buttons look polished; riders must also be able to find a route and understand delays.",
        "example": "Goal: buy a ticket. Measure task success, time, and user confusion before and after a checkout redesign.",
        "exercise": "Choose a familiar app and write its user goal, one interface element, and one experience outcome you would measure.",
        "quiz": [
            quiz("Which statement best describes UX?", ["The whole experience while pursuing a goal", "Only the color of buttons", "The code used to compile an app"], 0, "UX includes how useful, clear, and effective the overall experience is."),
            quiz("What should happen after a prototype test?", ["Use evidence to improve the design", "Assume all users agree", "Stop collecting feedback"], 0, "Testing is part of an iterative cycle, not a final ceremony."),
        ],
    },
    {
        "title": "UX research: interviews, surveys and user personas",
        "lessons": ["Plan interviews and neutral survey questions", "Synthesize observations into evidence-based personas"],
        "objectives": ["Ask open, non-leading research questions", "Separate observed evidence from assumptions"],
        "explanation": "Research helps designers understand what people do and need. Interviews provide depth; surveys can gather structured responses from more people. A persona summarizes a useful user pattern and must be grounded in research, not stereotypes.",
        "steps": ["Define the question and recruit people relevant to the task.", "Ask about recent real behavior before asking for opinions.", "Group repeated needs and quote evidence when describing a persona."],
        "real_world": "A learning platform team can interview students about how they choose a lesson instead of assuming they follow the course order.",
        "example": "Neutral prompt: “Tell me about the last time you could not find a course lesson. What did you try next?”",
        "exercise": "Draft five interview questions about submitting an assignment. Remove any question that suggests a preferred answer.",
        "quiz": [
            quiz("Which interview prompt is least leading?", ["Tell me about the last time you used this feature", "You like this layout, right?", "Wouldn't a blue button be better?"], 0, "A recent-behavior prompt asks for evidence without suggesting a response."),
            quiz("What should a persona represent?", ["A research-supported user pattern", "A designer's favorite fictional character", "Every possible user at once"], 0, "Personas summarize common research findings and should not rely on stereotypes."),
        ],
    },
    {
        "title": "User journeys, user flows and problem identification",
        "lessons": ["Map a journey across stages and touchpoints", "Draw a task flow and identify friction"],
        "objectives": ["Show user actions and pain points over time", "Use a flow to make decision points visible"],
        "explanation": "A journey map describes a person's broader experience across stages and channels. A user flow focuses on the steps and decisions inside a particular task. Both help locate friction before designing a fix.",
        "steps": ["Choose one user, goal, and starting point.", "List actions, questions, emotions, and touchpoints in order.", "Mark obstacles and validate them with research rather than guessing."],
        "real_world": "A journey map can reveal that course registration is confusing before and after the enrollment form, not just inside it.",
        "example": "Open course → compare prerequisites → select a section → confirm enrollment → receive confirmation.",
        "exercise": "Map the flow for finding and opening a lesson. Mark one point where the user may need reassurance or a clear status.",
        "quiz": [
            quiz("What does a user flow emphasize?", ["Steps and decisions for one task", "A brand's entire history", "The CSS grid implementation"], 0, "A flow makes the task path and decision points clear."),
            quiz("How should a suspected pain point be treated?", ["A hypothesis to validate", "A proven fact without research", "A reason to skip user testing"], 0, "Design observations need evidence before they are treated as user needs."),
        ],
    },
    {
        "title": "Information architecture and navigation",
        "lessons": ["Group content with user-centered labels", "Design navigation and test findability"],
        "objectives": ["Create a hierarchy that reflects user mental models", "Check whether users can find important content"],
        "explanation": "Information architecture organizes and labels content so people can find it. Navigation exposes that structure. Clear categories use words users recognize and avoid making people memorize where things live.",
        "steps": ["Inventory the content and the tasks people need to complete.", "Group related items and name groups with plain language.", "Test labels and paths with representative findability tasks."],
        "real_world": "A student portal should make courses, assignments, fees, and profile areas easy to distinguish.",
        "example": "Student Portal: Learn (Courses, Lessons), Work (Assignments), Account (Profile, Fees).",
        "exercise": "Group ten features for a small learning app into a navigation structure. Ask a classmate to find a specific assignment using your labels.",
        "quiz": [
            quiz("What is a useful navigation label?", ["A familiar word that describes its destination", "An internal database identifier", "A clever label whose meaning is hidden"], 0, "Labels should help people predict where a link will take them."),
            quiz("What does a tree test help evaluate?", ["Whether people can find items in a hierarchy", "Whether a button animation is smooth", "Whether a server stores a password"], 0, "Tree testing evaluates labels and information hierarchy without visual styling."),
        ],
    },
    {
        "title": "Wireframing: low-fidelity and high-fidelity",
        "lessons": ["Sketch low-fidelity layouts quickly", "Refine a wireframe into a detailed screen plan"],
        "objectives": ["Choose fidelity to match the design question", "Show hierarchy and content before decoration"],
        "explanation": "A wireframe maps the structure and priority of a screen. Low-fidelity sketches are quick to change; high-fidelity wireframes specify more detail. Neither needs to look finished before the underlying task works.",
        "steps": ["Write the screen's primary user task.", "Place the most important information and action first.", "Check the layout with a user task before adding visual polish."],
        "real_world": "A rough checkout wireframe can expose missing delivery choices before a team spends time styling it.",
        "example": "Screen blocks: progress indicator → order summary → delivery choice → payment fields → review button.",
        "exercise": "Sketch a course lesson page with title, objectives, example, quiz, and next lesson. Ask someone to point to where they would start.",
        "quiz": [
            quiz("When is a low-fidelity wireframe especially useful?", ["Exploring layout ideas cheaply", "Proving final color contrast", "Measuring production performance"], 0, "Simple sketches are quick to change while structure is still uncertain."),
            quiz("What should a wireframe make clear?", ["Content hierarchy and task actions", "Final photography licensing", "Database indexes"], 0, "Wireframes focus on screen structure and the relationships between content."),
        ],
    },
    {
        "title": "Figma basics: frames, layers, shapes and components",
        "lessons": ["Organize a screen with frames and layers", "Build reusable components and variants"],
        "objectives": ["Use frames to represent screens and layers to organize parts", "Reuse a component and name it for its purpose"],
        "explanation": "In Figma, frames can represent screens or containers, layers describe the objects inside them, and components are reusable design elements. Clear names and a sensible hierarchy make a file easier to edit and share.",
        "steps": ["Create a frame for the target device or screen.", "Add and name layers in a meaningful order.", "Turn repeated controls into components and use variants for real states."],
        "real_world": "A shared button component helps a team keep primary actions consistent across sign-up and checkout screens.",
        "example": "Component set: Button / Primary with variants for Default, Hover, Focus, and Disabled.",
        "exercise": "Build a sign-in screen from a frame, text, fields, and a button. Convert the button into a component and add a disabled state.",
        "quiz": [
            quiz("What is a component useful for?", ["Reusing a consistent design element", "Replacing user research", "Automatically writing database queries"], 0, "Components allow repeated UI to share one reusable source design."),
            quiz("Why name layers clearly?", ["To make the file easier to understand and edit", "To increase frame size", "To hide all objects from collaborators"], 0, "Meaningful names help collaborators find and maintain design elements."),
        ],
    },
    {
        "title": "UI design principles: color, typography, spacing and grids",
        "lessons": ["Use color and typography to establish hierarchy", "Apply spacing and grids consistently"],
        "objectives": ["Make text readable and actions distinguishable", "Use a repeatable spacing and alignment system"],
        "explanation": "Visual hierarchy guides attention. Typography, contrast, color, spacing, and alignment help people understand what matters and what is interactive. Consistent rules reduce visual noise and support accessibility.",
        "steps": ["Choose type sizes and weights for clear content roles.", "Use color for meaning only when contrast and another cue are present.", "Align content to a grid and use a spacing scale instead of arbitrary gaps."],
        "real_world": "A form with clear labels, consistent spacing, and visible error messages is easier to complete than a dense wall of fields.",
        "example": "Use an 8-point spacing rhythm (8, 16, 24), body text with readable line height, and a high-contrast primary action.",
        "exercise": "Review a screen for three hierarchy issues. Propose a typography, spacing, or contrast change and explain the user benefit.",
        "quiz": [
            quiz("Why should color not be the only way to show an error?", ["Some users cannot distinguish the color cue", "Color always slows a website", "Browsers do not display colors"], 0, "Icons or text labels provide an additional cue for users with color-vision differences."),
            quiz("What does a spacing scale improve?", ["Consistency and rhythm", "The number of user personas", "The file format"], 0, "A shared scale creates predictable relationships between elements."),
        ],
    },
    {
        "title": "Design systems and reusable components",
        "lessons": ["Define design tokens and component rules", "Document patterns and manage component states"],
        "objectives": ["Explain how tokens and components support consistency", "Document usage, accessibility, and states"],
        "explanation": "A design system combines reusable components, design decisions, and guidance for using them. Tokens name choices such as color and spacing. Documentation helps teams apply patterns consistently without removing thoughtful exceptions.",
        "steps": ["Identify repeated visual and interaction patterns.", "Name tokens by purpose rather than by a one-off screen.", "Document component use, states, accessibility expectations, and when not to use it."],
        "real_world": "A product team can update a shared error message pattern once and use it consistently in several forms.",
        "example": "Token: `color.text.primary`; component: TextField with label, hint, error, focus, and disabled states.",
        "exercise": "Create a small design-system entry for a primary button: purpose, spacing, contrast, focus state, and an example of when not to use it.",
        "quiz": [
            quiz("What is a design token?", ["A named reusable design decision", "A user password", "A screenshot export"], 0, "Tokens give shared names to values such as color, spacing, or typography."),
            quiz("Why document component states?", ["People need consistent behavior and feedback", "A component should never change", "Documentation replaces accessibility"], 0, "State guidance supports predictable interactions and accessible feedback."),
        ],
    },
    {
        "title": "Interactive prototyping and transitions",
        "lessons": ["Connect screens into a task prototype", "Use transitions to explain interaction state"],
        "objectives": ["Prototype a complete user task", "Use motion purposefully and respect reduced-motion needs"],
        "explanation": "A prototype simulates enough interaction to test an idea. A transition can show a state change or relationship, but motion should not distract, delay essential tasks, or create discomfort.",
        "steps": ["Choose the task and screens that need to be tested.", "Connect actions to outcomes and include success and error states.", "Keep transitions purposeful, test keyboard paths, and provide reduced-motion alternatives where appropriate."],
        "real_world": "A clickable enrollment prototype can test whether students understand prerequisites before the team builds the production flow.",
        "example": "Select course → show prerequisite summary → confirm enrollment → show a clear success state.",
        "exercise": "Prototype a password-reset flow with an invalid-email and success state. Test it with a keyboard-only user path.",
        "quiz": [
            quiz("What is the main purpose of a prototype?", ["Test an interaction or concept before full implementation", "Guarantee that the final product has no bugs", "Replace all production code"], 0, "Prototypes make a design idea testable while changes are still inexpensive."),
            quiz("When should motion be used?", ["When it clarifies a state or relationship", "Whenever a screen changes", "To hide a missing confirmation"], 0, "Purposeful motion can aid understanding, but unnecessary motion can distract or exclude."),
        ],
    },
    {
        "title": "Usability testing and design improvements",
        "lessons": ["Write realistic tasks and observe usability sessions", "Prioritize findings and validate improvements"],
        "objectives": ["Observe behavior without coaching the participant", "Turn patterns into specific design changes"],
        "explanation": "Usability testing observes people attempting realistic tasks. The goal is to find where the design helps or blocks them, not to test the participant. A useful finding describes evidence, impact, and a design opportunity.",
        "steps": ["Prepare a neutral scenario and a small set of tasks.", "Ask the participant to think aloud and avoid steering them.", "Record observed friction, prioritize by impact, and test the revised design."],
        "real_world": "Watching a learner try to resume a course can reveal whether progress labels and lesson links are understandable.",
        "example": "Evidence: three participants searched the menu for the assignment upload. Impact: submission was delayed. Opportunity: make the upload action visible in the assignment view.",
        "exercise": "Run a short test of a prototype with one person. Record exact actions and one question you would investigate with more participants.",
        "quiz": [
            quiz("What should a moderator do when a participant is stuck?", ["Observe and use a neutral prompt", "Immediately point to the correct button", "Tell them they are using it wrong"], 0, "Neutral prompts preserve useful evidence about the interface."),
            quiz("What makes a usability finding actionable?", ["Observed evidence and user impact", "A personal preference alone", "A vague statement that the page feels bad"], 0, "Evidence and impact help the team decide what change to test."),
        ],
    },
    {
        "title": "Responsive design for mobile, tablet and desktop",
        "lessons": ["Design mobile-first layouts that adapt", "Check content, input, and accessibility across breakpoints"],
        "objectives": ["Adapt layout to available space rather than device names", "Preserve task completion and readable content at every size"],
        "explanation": "Responsive design lets content adapt to its container and viewport. A mobile-first approach starts with essential content and adds layout complexity where space allows. Test real tasks, not just whether a screenshot fits.",
        "steps": ["Start with the narrow layout and prioritize content.", "Use flexible grids, fluid widths, and breakpoints when the content needs them.", "Check tap targets, text wrapping, keyboard access, and overflow at several widths."],
        "real_world": "A course sidebar may become a collapsible module list on a phone while lesson content remains readable.",
        "example": "Desktop: two-column lesson/sidebar layout. Narrow screen: one column with a clear module disclosure control.",
        "exercise": "Adapt a three-column course card layout to phone width. Note what should stack, what can hide, and what must remain available.",
        "quiz": [
            quiz("What should determine a responsive breakpoint?", ["Where the content or layout needs to change", "A fixed list of device brands", "The current year"], 0, "Breakpoints should respond to the design's content and available space."),
            quiz("What is a mobile-first approach?", ["Start with essential content at narrow widths", "Remove all keyboard support", "Design only for one phone model"], 0, "Mobile-first design prioritizes essential tasks before expanding the layout."),
        ],
    },
    {
        "title": "Portfolio projects: login app, shopping app and student dashboard",
        "lessons": ["Design an accessible login and recovery experience", "Design shopping and student dashboard workflows"],
        "objectives": ["Show a problem, design process, and tested outcome", "Explain decisions with user evidence and accessibility considerations"],
        "explanation": "A portfolio project should show how a design decision follows from a user problem. Present the goal, research, sketches, prototype, test findings, iterations, and outcome rather than only polished final screens.",
        "steps": ["Define a specific audience and task for the project.", "Show iterations and explain why the design changed.", "Include accessibility checks, prototype evidence, and what you would improve next."],
        "real_world": "A student dashboard project can demonstrate that a learner can find courses, understand progress, and return to the next lesson.",
        "example": "Case study outline: challenge → research → user flow → wireframes → prototype → test findings → final design → reflection.",
        "exercise": "Create a small portfolio case study for a login flow. Include empty, invalid, and success states plus one usability observation.",
        "quiz": [
            quiz("What makes a portfolio case study convincing?", ["Evidence and reasoning behind design decisions", "Only decorative mockups", "A list of software tools"], 0, "A case study explains the problem, decisions, testing, and learning."),
            quiz("Why show iterations?", ["They reveal how feedback shaped the result", "They prove the first design was perfect", "They replace a project goal"], 0, "Iterations show a thoughtful process and response to evidence."),
        ],
    },
]


DATA_SCIENCE_MODULES = [
    {
        "title": "Introduction to Data Science and real-world applications",
        "lessons": ["Ask a useful question with data", "Understand the data science workflow and limits"],
        "objectives": ["Describe the data science cycle", "Recognize privacy, bias, and uncertainty concerns"],
        "explanation": "Data science combines domain questions, data, computing, and communication to support decisions. A result is useful only when the data and method fit the question and limitations are explained.",
        "steps": ["Translate a real need into a measurable question.", "Collect and inspect relevant data with permission.", "Analyze, validate, communicate uncertainty, and consider who may be affected."],
        "real_world": "A school can study attendance patterns to plan support, but should not treat a pattern as proof about an individual student's ability.",
        "example": "Question: Which weeks have the highest missed classes? Define attendance, time period, and privacy protections before calculating.",
        "exercise": "Choose a public-interest question and list the data needed, possible bias, and one decision the analysis should not make.",
        "quiz": [
            quiz("What should guide a data science analysis?", ["A clear question and appropriate evidence", "The most complicated algorithm available", "A chart chosen before seeing the data"], 0, "The question determines what data and methods are appropriate."),
            quiz("Why discuss limitations?", ["Readers need context and uncertainty", "Every dataset is perfect", "Limitations make results more accurate automatically"], 0, "Limitations help people interpret what an analysis can and cannot support."),
        ],
    },
    {
        "title": "Mathematics, statistics and probability fundamentals",
        "lessons": ["Summarize distributions with statistics", "Reason about probability and sampling"],
        "objectives": ["Compare mean, median, spread, and outliers", "Explain how samples and chance affect conclusions"],
        "explanation": "Statistics describes patterns in data and helps reason from samples. The mean is sensitive to extreme values; the median is often more robust. Probability quantifies uncertainty under stated assumptions.",
        "steps": ["Inspect the distribution before choosing a summary.", "Compare center and spread rather than relying on one number.", "Ask how the sample was collected and whether chance variation could explain a pattern."],
        "real_world": "Median rent can describe a typical listing better than the mean when a small number of luxury listings are extremely expensive.",
        "example": "Values [10, 11, 12, 13, 100] have mean 29.2 but median 12; the outlier changes the mean substantially.",
        "exercise": "Calculate mean and median for a small set with one extreme value. Explain which better answers a question about a typical observation.",
        "quiz": [
            quiz("Which measure is usually less affected by an extreme value?", ["Median", "Mean", "Maximum"], 0, "The median depends on the middle rank rather than the magnitude of every value."),
            quiz("What does a sampling method affect?", ["How representative a sample may be", "The spelling of column names", "Whether a plot has a title"], 0, "A biased sample can produce conclusions that do not generalize."),
        ],
    },
    {
        "title": "Python fundamentals for data science",
        "lessons": ["Use Python types and collections for data tasks", "Write reusable analysis functions and handle errors"],
        "objectives": ["Process simple data with loops and collections", "Make analysis steps reusable and testable"],
        "explanation": "Data work benefits from the same Python basics used in other programs: clear values, collections, functions, loops, and safe input handling. Small functions make cleaning and calculations easier to test.",
        "steps": ["Represent records with lists or dictionaries while learning.", "Write a function for one transformation or calculation.", "Test normal, empty, and unexpected inputs before analyzing a larger dataset."],
        "real_world": "A function that normalizes course names can reduce inconsistent spellings before counting enrollments.",
        "example": "def clean_label(value):\n    return value.strip().casefold()\n\nlabels = [' Python ', 'PYTHON']\nprint([clean_label(label) for label in labels])",
        "exercise": "Write a function that converts a list of numeric strings into numbers and reports invalid values without stopping the whole analysis.",
        "quiz": [
            quiz("Why use a function for a repeated cleaning step?", ["It makes the step reusable and testable", "It removes the need to inspect data", "It guarantees clean source data"], 0, "A function centralizes logic and makes behavior easier to test."),
            quiz("Which input should a data helper test?", ["An empty or invalid case as well as normal input", "Only the largest expected dataset", "No inputs at all"], 0, "Edge-case tests reveal assumptions that normal examples can hide."),
        ],
    },
    {
        "title": "NumPy arrays and numerical operations",
        "lessons": ["Create arrays and inspect their shape", "Apply vectorized operations and understand broadcasting"],
        "objectives": ["Distinguish an array from a Python list", "Use element-wise operations with compatible shapes"],
        "explanation": "NumPy arrays store numerical data in a structured shape and support efficient vectorized calculations. Shape describes each dimension. Broadcasting allows operations across compatible shapes, but unexpected shapes can produce unintended results.",
        "steps": ["Create arrays from known values and inspect `shape` and `dtype`.", "Use element-wise operations rather than looping when appropriate.", "Check output shape and values, especially when broadcasting dimensions."],
        "real_world": "An array can scale all measurements from centimeters to meters in one clear operation.",
        "example": "import numpy as np\ncm = np.array([100, 150, 200])\nmeters = cm / 100\nprint(meters, meters.shape)",
        "exercise": "Create a 2-by-3 array of quiz scores. Calculate column averages and verify the output contains one value per quiz.",
        "quiz": [
            quiz("What does an array's `shape` describe?", ["Its dimensions", "Its file name", "Its plot color"], 0, "Shape records the size along each array dimension."),
            quiz("Why check broadcasted result shapes?", ["Compatible dimensions may still imply an unintended calculation", "NumPy never changes output shape", "Shape determines the operating system"], 0, "Shape checks help catch alignment mistakes in vectorized operations."),
        ],
    },
    {
        "title": "Pandas and DataFrames",
        "lessons": ["Inspect a DataFrame and select columns", "Filter, group, and summarize records"],
        "objectives": ["Inspect rows, columns, and data types", "Use selection and aggregation to answer a question"],
        "explanation": "A Pandas DataFrame is a labeled table. Inspect it before analysis, select columns by name, filter rows with conditions, and group records to calculate summaries. Labels make code readable and operations reproducible.",
        "steps": ["Review `head()`, `info()`, and column names.", "Select relevant columns and make the filter condition explicit.", "Group on a meaningful category, aggregate, and check the result."],
        "real_world": "A school can group assessment scores by subject to compare class-level patterns.",
        "example": "import pandas as pd\nscores = pd.DataFrame({'subject': ['Math', 'Math', 'Art'], 'score': [80, 90, 85]})\nprint(scores.groupby('subject')['score'].mean())",
        "exercise": "Build a small DataFrame with category, date, and amount. Group by category and verify the totals against the raw rows.",
        "quiz": [
            quiz("Why inspect `DataFrame.info()`?", ["To review columns, types, and missing-value counts", "To train a model automatically", "To draw a map"], 0, "`info()` gives a compact structural summary of a DataFrame."),
            quiz("What does `groupby` help do?", ["Summarize rows within categories", "Rename Python keywords", "Remove all duplicate rows automatically"], 0, "Grouping makes it possible to aggregate data by category."),
        ],
    },
    {
        "title": "Data collection and importing datasets",
        "lessons": ["Choose responsible and relevant data sources", "Import CSV and other common datasets"],
        "objectives": ["Check provenance, permissions, and scope", "Load data with explicit format and encoding assumptions"],
        "explanation": "Data quality begins before analysis. Record where data came from, when it was collected, what each row means, and whether its use is permitted. Importing correctly requires knowing delimiters, headers, encodings, and data types.",
        "steps": ["Define the population and fields needed for the question.", "Use a trusted source with appropriate permission and privacy safeguards.", "Load a small sample first, inspect parsing, and record provenance."],
        "real_world": "A public sales dataset may use one row per order line rather than one row per order; understanding the grain prevents incorrect totals.",
        "example": "import pandas as pd\norders = pd.read_csv('orders.csv', encoding='utf-8')\nprint(orders.head())\nprint(orders.dtypes)",
        "exercise": "Import a permitted public CSV. Record its source, row meaning, date range, and two assumptions that need checking.",
        "quiz": [
            quiz("What does data provenance describe?", ["Where data came from and how it was produced", "Only the chart style", "The order of Python imports"], 0, "Provenance records source, collection, and relevant transformations."),
            quiz("Why inspect a sample after importing?", ["To catch parsing and type problems early", "To guarantee there are no biases", "To avoid documenting the source"], 0, "A quick inspection reveals delimiter, header, and type assumptions."),
        ],
    },
    {
        "title": "Data cleaning: missing values, duplicates and outliers",
        "lessons": ["Identify missing and duplicate records", "Investigate outliers and document cleaning choices"],
        "objectives": ["Distinguish data errors from valid unusual observations", "Choose transparent handling for missing values"],
        "explanation": "Cleaning makes data more consistent, but every change encodes a decision. Missing values may mean unknown or not applicable. Duplicates may be errors or legitimate repeated events. Outliers require investigation rather than automatic deletion.",
        "steps": ["Measure missingness, duplicate rows, and suspicious ranges.", "Check definitions and source records before changing values.", "Apply a documented rule and compare analysis with and without uncertain cases."],
        "real_world": "A very high purchase may be a data-entry error or a genuine wholesale order; context determines whether it should remain.",
        "example": "missing_rate = df['score'].isna().mean()\nduplicate_rows = df.duplicated().sum()\nprint(missing_rate, duplicate_rows)",
        "exercise": "Create a small table with a missing value, a duplicate, and an extreme value. Propose a different treatment for each and explain the evidence needed.",
        "quiz": [
            quiz("Should every outlier be removed?", ["No; investigate whether it is valid", "Yes, without checking", "Only if it is the first row"], 0, "An unusual value may be valid and important to the question."),
            quiz("Why document a missing-value rule?", ["So the analysis is transparent and reproducible", "To hide incomplete data", "To guarantee a larger sample"], 0, "Documenting decisions makes their effects reviewable."),
        ],
    },
    {
        "title": "Exploratory Data Analysis",
        "lessons": ["Ask questions with summaries and distributions", "Investigate relationships without overclaiming"],
        "objectives": ["Use descriptive summaries and plots to understand data", "Separate association from causal claims"],
        "explanation": "Exploratory Data Analysis (EDA) uses summaries and visual checks to understand structure, distributions, unusual values, and possible relationships. EDA helps form hypotheses; it does not by itself prove a cause.",
        "steps": ["Check row meaning, ranges, and missing values.", "Summarize distributions and compare relevant subgroups.", "Investigate patterns with plots and follow up on surprises using domain context."],
        "real_world": "Comparing study hours with assessment scores may show an association, but other factors could influence both.",
        "example": "print(df.describe(include='all'))\nprint(df.isna().sum())\nprint(df.groupby('classroom')['score'].median())",
        "exercise": "Explore a small dataset with at least one numeric and one category column. Write two observations and one limitation.",
        "quiz": [
            quiz("What is a main purpose of EDA?", ["Understand structure and generate questions", "Prove causation from any pattern", "Replace data collection"], 0, "EDA helps describe and investigate data before formal conclusions."),
            quiz("Does correlation alone prove that one variable caused another?", ["No", "Yes, always", "Only when plotted"], 0, "Association can arise from confounding, coincidence, or other mechanisms."),
        ],
    },
    {
        "title": "Data visualization with Matplotlib and Seaborn",
        "lessons": ["Create clear Matplotlib charts", "Use Seaborn to compare distributions and relationships"],
        "objectives": ["Select visual encodings that fit the data", "Label and critique a chart for clarity and honesty"],
        "explanation": "Matplotlib provides control over charts; Seaborn offers higher-level statistical plots. Good visualization makes comparisons clear, labels units, and avoids visual choices that exaggerate a pattern.",
        "steps": ["Match the chart to the data type and question.", "Add a clear title, axis labels, units, and a useful legend.", "Check scale, color, clutter, and accessibility before sharing."],
        "real_world": "A box plot can compare score distributions across classes while showing spread and possible outliers.",
        "example": "import seaborn as sns\nimport matplotlib.pyplot as plt\nsns.boxplot(data=df, x='classroom', y='score')\nplt.xlabel('Classroom')\nplt.ylabel('Assessment score')\nplt.show()",
        "exercise": "Create a chart for a numeric trend or category comparison. Ask a reader to explain it and revise any confusing labels.",
        "quiz": [
            quiz("What is a box plot useful for?", ["Comparing distributions across groups", "Showing a website's navigation", "Displaying source code"], 0, "Box plots summarize distribution shape and spread for groups."),
            quiz("What should a chart label communicate?", ["What values and units represent", "Only the author's name", "A guarantee of causation"], 0, "Labels give readers context for interpreting visual values."),
        ],
    },
    {
        "title": "SQL fundamentals, joins and aggregation",
        "lessons": ["Select, filter, and sort records with SQL", "Join related tables and aggregate results"],
        "objectives": ["Write a query with filtering and ordering", "Choose join keys and group at the intended grain"],
        "explanation": "SQL retrieves and summarizes relational data. `SELECT` chooses columns, `WHERE` filters rows, and `GROUP BY` aggregates them. Joins combine tables using related keys; an incorrect join can duplicate records and inflate totals.",
        "steps": ["Understand table keys and what one row represents.", "Filter records before grouping when the question requires it.", "Join on the correct relationship and compare row counts before and after."],
        "real_world": "A school database can join student and enrollment tables to count students per course.",
        "example": "SELECT course_id, COUNT(*) AS enrollment_count\nFROM enrollments\nGROUP BY course_id\nORDER BY enrollment_count DESC;",
        "exercise": "Create two small related tables and write a join that returns each course with its enrollment count. Check that the count matches the source rows.",
        "quiz": [
            quiz("What does `GROUP BY` do?", ["Collects rows into groups for aggregation", "Deletes duplicate tables", "Sorts by a password"], 0, "Grouping defines which rows an aggregate summarizes together."),
            quiz("What can an incorrect join key cause?", ["Duplicated or missing matches", "Automatic correction of the source", "A different chart color"], 0, "Join relationships control which records pair up and may multiply rows."),
        ],
    },
    {
        "title": "Machine learning: supervised and unsupervised learning",
        "lessons": ["Frame a supervised learning problem", "Explore clustering and unsupervised learning"],
        "objectives": ["Distinguish labeled prediction from structure discovery", "Choose a baseline and avoid data leakage"],
        "explanation": "Supervised learning uses examples with known targets to predict a label or value. Unsupervised learning looks for structure without a target label. A model is a tool for a defined task, not a substitute for understanding data or consequences.",
        "steps": ["Define the target and what a prediction will be used for.", "Split data appropriately and compare against a simple baseline.", "Inspect errors, fairness, and whether information leaked from the future or target."],
        "real_world": "A support team might classify incoming requests by topic, while clustering could explore recurring groups without preassigned labels.",
        "example": "Supervised: features → known outcome → learned prediction. Unsupervised: features → groups or structure to inspect.",
        "exercise": "Describe one prediction task and one clustering task for a library. Name the target for the first and explain why the second has no target.",
        "quiz": [
            quiz("What distinguishes supervised learning?", ["Training examples include a target label or value", "It never uses data", "It only creates charts"], 0, "Supervised models learn from input examples paired with known outcomes."),
            quiz("What is a useful first model comparison?", ["A simple baseline", "A complicated model with no evaluation", "Training accuracy only"], 0, "A baseline helps show whether added complexity provides value."),
        ],
    },
    {
        "title": "Model evaluation: accuracy, precision, recall and confusion matrix",
        "lessons": ["Read a confusion matrix and calculate metrics", "Choose evaluation measures for the task's costs"],
        "objectives": ["Explain accuracy, precision, and recall", "Select metrics based on error consequences and class balance"],
        "explanation": "A confusion matrix counts correct and incorrect predictions by class. Accuracy is the share of all predictions that are correct; precision asks how many predicted positives were truly positive; recall asks how many actual positives were found.",
        "steps": ["Define which class counts as positive.", "Count true positives, false positives, true negatives, and false negatives.", "Choose metrics based on the cost of each error and report the evaluation data used."],
        "real_world": "For screening a rare condition, missing a true case may be more costly than reviewing a false alarm, so recall deserves attention alongside precision.",
        "example": "If 8 of 10 predicted positives are real, precision is 8/10 = 0.80. If the model finds 8 of 20 actual positives, recall is 8/20 = 0.40.",
        "exercise": "Create a small confusion matrix with 6 true positives, 2 false positives, 4 false negatives, and 8 true negatives. Calculate accuracy, precision, and recall.",
        "quiz": [
            quiz("What does recall measure?", ["The share of actual positives found", "The share of predicted positives that are correct", "The number of model parameters"], 0, "Recall is true positives divided by all actual positives."),
            quiz("When can accuracy be misleading?", ["When classes are highly imbalanced", "When all labels are known", "When a table has column names"], 0, "A model can score highly by predicting the majority class while missing rare cases."),
        ],
    },
    {
        "title": "Analytics types: descriptive, diagnostic, predictive and prescriptive",
        "lessons": ["Separate what happened from why it happened", "Use predictions and recommendations responsibly"],
        "objectives": ["Classify common analytics questions", "Explain why a recommendation needs assumptions and constraints"],
        "explanation": "Descriptive analytics summarizes what happened; diagnostic analytics investigates why; predictive analytics estimates what may happen; prescriptive analytics compares possible actions. Each step adds assumptions and should communicate uncertainty.",
        "steps": ["Write the decision question in plain language.", "Identify whether it asks for a summary, explanation, forecast, or action.", "State assumptions and constraints before recommending a decision."],
        "real_world": "A retailer may summarize monthly sales, investigate a decline, forecast demand, and compare inventory actions.",
        "example": "“What were sales?” is descriptive. “Why did they fall?” is diagnostic. “What might next month be?” is predictive. “How much should we stock?” is prescriptive.",
        "exercise": "Write one question for each analytics type using a school attendance scenario and note one uncertainty for the predictive question.",
        "quiz": [
            quiz("Which analytics type asks what may happen next?", ["Predictive", "Descriptive", "Diagnostic"], 0, "Predictive analytics estimates likely future outcomes."),
            quiz("What additional care does prescriptive analytics need?", ["Clear assumptions, constraints, and decision context", "No human review", "A promise that one action is always best"], 0, "Recommendations depend on assumptions and consequences that should be explicit."),
        ],
    },
    {
        "title": "Practical projects: student performance analysis and sales prediction",
        "lessons": ["Analyze student performance responsibly", "Build and evaluate a sales forecasting project"],
        "objectives": ["Complete an analysis from question to communication", "Evaluate a predictive project against a baseline and practical limits"],
        "explanation": "A capstone combines data sourcing, cleaning, analysis, evaluation, and communication. Student performance data is sensitive, so use public or synthetic data, minimize identifying details, and avoid using group patterns to make unsupported decisions about individuals.",
        "steps": ["Write the project question, data dictionary, and privacy plan.", "Explore and clean data with documented choices.", "Build a clear analysis or baseline model, evaluate it, and explain limits and next steps."],
        "real_world": "An aggregate performance report can help a school identify topics that may need more teaching support without labeling individual students.",
        "example": "Sales project: split by time (not randomly across future and past), forecast a baseline, compare error, and visualize actual versus predicted sales.",
        "exercise": "Draft a project proposal with question, permitted data, data-grain, cleaning plan, baseline, evaluation metric, and a limitation.",
        "quiz": [
            quiz("Why should student data be minimized or anonymized?", ["It reduces privacy risk", "It guarantees a better model", "It removes the need for consent"], 0, "Using less identifiable data helps protect people but does not replace appropriate permission."),
            quiz("Why should a sales forecast be compared with a baseline?", ["To check whether the model adds useful predictive value", "To avoid checking time order", "To guarantee future sales"], 0, "A baseline gives context for whether model complexity improves forecasts."),
        ],
    },
]


WEB_DEVELOPMENT_MODULES = [
    {
        "title": "HTML foundations and accessible structure",
        "lessons": [{"slug": "html-fundamentals", "title": "HTML Fundamentals"}],
        "objectives": ["Structure a document with semantic HTML", "Choose elements that describe the meaning of content"],
        "explanation": "HTML describes the structure and meaning of webpage content. Browsers use elements such as headings, paragraphs, links, lists, and forms to present information and make it navigable. Semantic elements communicate purpose to assistive technology and other tools.",
        "steps": ["Start with a valid document declaration, language, head, and body.", "Use headings in a logical hierarchy and choose elements by meaning rather than appearance.", "Label form controls and write descriptive link text; validate the result in a browser."],
        "real_world": "A course page with real headings and labeled links is easier to scan with a screen reader and easier to maintain than a page built from generic containers.",
        "example": "<!doctype html>\n<html lang=\"en\">\n  <head><meta charset=\"utf-8\"><title>Course notes</title></head>\n  <body>\n    <main>\n      <h1>Course notes</h1>\n      <p>Start with semantic HTML.</p>\n      <a href=\"lessons.html\">View lessons</a>\n    </main>\n  </body>\n</html>",
        "exercise": "Build a semantic course article with a heading, introduction, ordered steps, a descriptive link, and a labeled email form. Check its document outline and submit an empty form.",
        "quiz": [
            quiz("What is the main purpose of semantic HTML?", ["Describe the meaning and structure of content", "Add visual colors to a page", "Run database queries"], 0, "Semantic elements describe content roles and structure; CSS controls presentation."),
        ],
    },
    {
        "title": "CSS, layouts, responsive design and accessibility",
        "lessons": [{"slug": "css-responsive-design", "title": "CSS & Responsive Design"}],
        "objectives": ["Style content with selectors and the cascade", "Build flexible layouts with Grid and Flexbox", "Test responsive and accessible presentation"],
        "explanation": "CSS controls how HTML is displayed. The cascade resolves competing rules, while layout tools such as Flexbox and Grid arrange content. Responsive styles adapt to available space; accessible styling keeps text, focus, and controls usable.",
        "steps": ["Link a stylesheet and select elements by class or semantic role.", "Use spacing, readable typography, and Grid or Flexbox for the layout.", "Add a breakpoint only when the content needs it; test narrow widths, keyboard focus, and contrast."],
        "real_world": "A course catalogue can show three columns on a wide display and become a single readable column on a phone.",
        "example": ".course-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));\n  gap: 1.25rem;\n}\n\n:focus-visible {\n  outline: 3px solid #2563eb;\n  outline-offset: 3px;\n}",
        "exercise": "Style your HTML course article as a responsive card. Verify that it has no horizontal overflow at 375px and that keyboard focus is visible.",
        "quiz": [
            quiz("What should determine a responsive breakpoint?", ["Where the content needs to adapt", "A specific phone brand", "The page title"], 0, "Breakpoints should respond to layout and content needs, not device names."),
        ],
    },
    {
        "title": "JavaScript, browser interaction and application behavior",
        "lessons": [{"slug": "javascript-basics", "title": "JavaScript Basics"}],
        "objectives": ["Use variables, functions, conditions, and arrays", "Respond to user actions with DOM events", "Validate input and give clear feedback"],
        "explanation": "JavaScript adds behavior to webpages. It can read user input, update the Document Object Model (DOM), and respond to events. Keep behavior predictable: validate input, handle expected failures, and make status changes visible.",
        "steps": ["Write a small function that represents one action.", "Select the relevant element and attach an event listener.", "Update text or state safely and test both valid and invalid input."],
        "real_world": "A lesson-complete control can update a visible progress label and save a completion record so a learner can resume later.",
        "example": "const button = document.querySelector(\"[data-action='greet']\");\nconst message = document.querySelector(\"[data-message]\");\n\nbutton.addEventListener('click', () => {\n  message.textContent = 'Welcome back!';\n});",
        "exercise": "Create a small task list with an add form. Validate blank input, add a task using DOM methods, and announce the updated task count.",
        "quiz": [
            quiz("Which browser API commonly registers a click handler?", ["addEventListener", "queryDatabase", "setStyleSheet"], 0, "`addEventListener` registers a function to respond to an event."),
        ],
    },
    {
        "title": "Modern websites, testing, performance and deployment",
        "lessons": [{"slug": "modern-website-development", "title": "Modern Website Development"}],
        "objectives": ["Combine semantic HTML, responsive CSS, and maintainable JavaScript", "Check accessibility, links, and performance", "Plan a reliable publish and update workflow"],
        "explanation": "A modern website is a set of connected user tasks, not just a collection of screens. Good structure, responsive layout, accessible interaction, fast loading, and tested navigation work together. Small projects benefit from clear file organization and repeatable checks.",
        "steps": ["Turn a user goal into pages and working navigation.", "Build semantic structure, responsive styles, and focused interactions.", "Check links and keyboard use, inspect mobile layouts, optimize assets, and deploy to a host."],
        "real_world": "A student learning portal should let a learner locate a course, open a lesson, understand progress, and return to the next task on both desktop and mobile.",
        "example": "Project checks:\n- Every navigation link has a real destination.\n- Forms report invalid input clearly.\n- Main tasks work with a keyboard.\n- Images are sized appropriately and have useful alternative text.\n- Layout is checked at narrow and wide viewport widths.",
        "exercise": "Turn your course article and task list into a small learning portal. Add a course overview, lesson navigation, saved progress, and a short test checklist.",
        "quiz": [
            quiz("What is a useful release check for a multi-page website?", ["Verify every navigation destination and key task", "Check only the home page title", "Remove keyboard focus styles"], 0, "Testing actual destinations and tasks catches broken navigation before release."),
        ],
    },
]


COURSES = {
    "web-development": {
        "title": "Web Development",
        "icon": "💻",
        "description": "Progress from semantic HTML to responsive interfaces, interactive behavior, and complete website projects.",
        "difficulty": "Beginner to advanced",
        "duration": "30–40 hours",
        "prerequisites": "No coding experience required; a computer and a modern browser are enough to begin.",
        "modules": WEB_DEVELOPMENT_MODULES,
        "documentation": [
            ("MDN HTML Guide", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content"),
            ("MDN CSS Guide", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics"),
            ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
            ("W3C Web Accessibility Initiative", "https://www.w3.org/WAI/fundamentals/"),
            ("web.dev Learn", "https://web.dev/learn/"),
        ],
        "channels": [
            ("Mozilla Developer", "https://www.youtube.com/@MozillaDeveloper"),
            ("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp"),
        ],
        "assessment": [
            quiz("Which HTML element gives a page's main content a semantic landmark?", ["main", "span", "b"], 0, "`main` identifies the page's primary content area."),
            quiz("What is a useful responsive breakpoint strategy?", ["Adapt where content needs it", "Use one breakpoint per device brand", "Disable mobile layouts"], 0, "Breakpoints should be based on the layout's available space."),
            quiz("How should browser code listen for an interaction?", ["Register an event listener", "Rename the HTML file", "Add a SQL index"], 0, "Event listeners connect user actions to a handler function."),
            quiz("What helps keyboard users understand where they are?", ["Visible focus styling", "Removing outlines", "Color-only state changes"], 0, "Visible focus indicates the currently focused control."),
            quiz("What should a website release check include?", ["Working links and task flows", "Only the desktop logo", "A single page refresh"], 0, "Verifying destinations and tasks catches broken user journeys."),
        ],
        "capstone": {
            "title": "Responsive Learning Portal",
            "brief": "Build a small, accessible learning portal with course navigation, lesson pages, a working interaction, and visible saved progress.",
            "deliverables": ["Semantic HTML page structure and meaningful navigation", "Responsive CSS layout and visible keyboard focus", "JavaScript interaction with input validation and user feedback", "A simple persistent progress feature", "Desktop/mobile test checklist and project README"],
            "rubric": "Assess task completion and navigation (25%), semantic and accessible markup (20%), responsive styling (20%), reliable interaction (20%), and testing/documentation (15%).",
        },
        "resources": [
            ("MDN HTML Guide", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content"),
            ("MDN CSS Guide", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics"),
            ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
        ],
    },
    "python-programming": {
        "title": "Python Programming",
        "icon": "🐍",
        "description": "Build Python skills from your first script through data libraries and practical applications.",
        "difficulty": "Beginner to advanced",
        "duration": "45–60 hours",
        "prerequisites": "No programming experience required; access to a computer and willingness to practice.",
        "modules": PYTHON_MODULES,
        "documentation": [
            ("Python Tutorial", "https://docs.python.org/3/tutorial/"),
            ("Python Library Reference", "https://docs.python.org/3/library/"),
            ("NumPy Quickstart", "https://numpy.org/doc/stable/user/quickstart.html"),
            ("Pandas Getting Started", "https://pandas.pydata.org/docs/getting_started/"),
            ("Matplotlib Tutorials", "https://matplotlib.org/stable/tutorials/"),
        ],
        "channels": [
            ("Python Software Foundation", "https://www.youtube.com/@ThePSF"),
            ("Corey Schafer", "https://www.youtube.com/@coreyms"),
        ],
        "assessment": [
            quiz("Which collection stores unique values?", ["set", "list", "tuple"], 0, "A set keeps unique hashable values."),
            quiz("What does a function's `return` statement provide?", ["A value to its caller", "An automatic file", "A new module"], 0, "`return` sends the result to the calling code."),
            quiz("Which mode opens a file for reading text?", ["r", "w", "x"], 0, "`r` opens an existing file for reading."),
            quiz("What does a Pandas DataFrame represent?", ["Labeled tabular data", "A Python loop", "A single Boolean"], 0, "A DataFrame is a labeled two-dimensional data structure."),
            quiz("What is a sound first step when a program raises `ValueError` for user input?", ["Validate and explain the expected input", "Hide every exception", "Delete the input"], 0, "Specific validation gives the user useful feedback while leaving other bugs visible."),
        ],
        "capstone": {
            "title": "Student Management System",
            "brief": "Build a command-line student management system that can add, list, search, update, and remove students, then save and reload records.",
            "deliverables": ["A clear student data model and menu flow", "Input validation and focused functions or classes", "JSON or CSV persistence with safe error handling", "Tests for normal use, missing records, and invalid input", "A README explaining setup, data format, and limitations"],
            "rubric": "Assess correctness (40%), clarity and structure (20%), validation and persistence (20%), and tests/documentation (20%).",
        },
        "resources": [
            ("Python Tutorial", "https://docs.python.org/3/tutorial/"),
            ("NumPy Quickstart", "https://numpy.org/doc/stable/user/quickstart.html"),
            ("Pandas Getting Started", "https://pandas.pydata.org/docs/getting_started/"),
        ],
    },
    "ui-ux-design": {
        "title": "UI/UX Design",
        "icon": "🎨",
        "description": "Learn user research, information architecture, visual design, prototyping, testing, and portfolio storytelling.",
        "difficulty": "Beginner to advanced",
        "duration": "40–55 hours",
        "prerequisites": "No design software experience required; bring curiosity about how people use digital products.",
        "modules": UI_UX_MODULES,
        "documentation": [
            ("Figma Learn", "https://help.figma.com/hc/en-us"),
            ("W3C Web Accessibility Initiative", "https://www.w3.org/WAI/fundamentals/"),
            ("Material Design Foundations", "https://m3.material.io/foundations"),
            ("Nielsen Norman Group Articles", "https://www.nngroup.com/articles/"),
        ],
        "channels": [
            ("Figma", "https://www.youtube.com/@Figma"),
            ("Nielsen Norman Group", "https://www.youtube.com/@NNgroup"),
        ],
        "assessment": [
            quiz("Which method is most suited to learning about a recent real user task?", ["A neutral interview prompt", "A leading yes/no question", "A color preference vote only"], 0, "A neutral prompt invites evidence about actual behavior."),
            quiz("What does a user flow show?", ["Steps and decisions for a task", "A complete brand history", "A source-code dependency"], 0, "A flow maps the user's path through a task."),
            quiz("What is a design token?", ["A named reusable design decision", "A usability score", "A browser cookie"], 0, "Tokens provide shared names for design values."),
            quiz("What should a usability moderator avoid?", ["Coaching the participant toward the answer", "Observing task completion", "Taking notes"], 0, "Leading participants hides friction in the interface."),
            quiz("What should drive responsive breakpoints?", ["Content and layout needs", "Device brand names", "A fixed number of screens"], 0, "Breakpoints should be chosen where the content needs adaptation."),
        ],
        "capstone": {
            "title": "Student Learning Dashboard",
            "brief": "Design and test a responsive student dashboard that helps learners find courses, understand progress, resume lessons, and locate assignments.",
            "deliverables": ["Research summary and evidence-based user needs", "Information architecture and key user flows", "Low- and high-fidelity mobile and desktop screens", "Reusable components with documented states", "Clickable prototype and usability findings", "A portfolio case study showing iterations and accessibility checks"],
            "rubric": "Assess research evidence (20%), task clarity (25%), responsive and accessible UI (25%), prototype/testing iteration (20%), and communication (10%).",
        },
        "resources": [
            ("Figma Learn and Help", "https://help.figma.com/hc/en-us"),
            ("W3C Web Accessibility Initiative", "https://www.w3.org/WAI/fundamentals/"),
            ("Material Design Foundations", "https://m3.material.io/foundations"),
        ],
    },
    "data-science": {
        "title": "Data Science",
        "icon": "📊",
        "description": "Move from data questions and cleaning to analysis, visualization, SQL, and evaluated machine learning.",
        "difficulty": "Beginner to advanced",
        "duration": "55–75 hours",
        "prerequisites": "No prior data science required; basic arithmetic helps. Python foundations are included.",
        "modules": DATA_SCIENCE_MODULES,
        "documentation": [
            ("NumPy User Guide", "https://numpy.org/doc/stable/user/"),
            ("Pandas User Guide", "https://pandas.pydata.org/docs/user_guide/"),
            ("Matplotlib Tutorials", "https://matplotlib.org/stable/tutorials/"),
            ("Seaborn Tutorial", "https://seaborn.pydata.org/tutorial.html"),
            ("SQLite Language Reference", "https://www.sqlite.org/lang.html"),
            ("scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html"),
        ],
        "channels": [
            ("StatQuest with Josh Starmer", "https://www.youtube.com/@statquest"),
            ("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp"),
        ],
        "assessment": [
            quiz("What is a robust center measure when a distribution has extreme values?", ["Median", "Mean only", "Maximum"], 0, "The median is based on rank and is less affected by extreme magnitudes."),
            quiz("Does correlation alone prove causation?", ["No", "Yes", "Only in a scatter plot"], 0, "Other variables and chance can produce an association."),
            quiz("Which task is supervised learning?", ["Predict a known target from labeled examples", "Group data without labels", "Sort a file alphabetically"], 0, "Supervised learning uses examples paired with known outcomes."),
            quiz("What does recall measure?", ["Actual positives found by the model", "Predicted positives that are correct", "All model parameters"], 0, "Recall is the share of actual positives that were identified."),
            quiz("Why compare a forecast with a baseline?", ["To see whether the model adds value", "To guarantee future outcomes", "To remove uncertainty"], 0, "A baseline gives a simple reference for predictive performance."),
        ],
        "capstone": {
            "title": "Student Performance Analysis and Sales Prediction",
            "brief": "Complete two connected studies: responsibly explore a permitted student-performance dataset, then build and evaluate a time-aware sales forecast using a public or synthetic dataset.",
            "deliverables": ["Question, source, data dictionary, and privacy note for each dataset", "Reproducible cleaning and exploratory analysis", "SQL query or Pandas summary and clearly labeled visualizations", "A simple forecast baseline and a justified evaluation metric", "Discussion of uncertainty, limitations, and responsible use", "A concise report or notebook that another learner can rerun"],
            "rubric": "Assess data provenance and privacy (20%), reproducibility and cleaning (20%), analysis/visualization (20%), evaluation against baseline (20%), and communication/limitations (20%).",
        },
        "resources": [
            ("Pandas User Guide", "https://pandas.pydata.org/docs/user_guide/"),
            ("scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html"),
            ("NumPy User Guide", "https://numpy.org/doc/stable/user/"),
        ],
    },
}


def slugify(value):
    result = []
    for character in value.lower():
        if character.isalnum():
            result.append(character)
        elif result and result[-1] != "-":
            result.append("-")
    return "".join(result).strip("-")


def _lesson_title(lesson_entry):
    title = lesson_entry.get("title") if isinstance(lesson_entry, dict) else lesson_entry
    if isinstance(title, dict):
        title = title.get("title")
    if not isinstance(title, str):
        raise TypeError("Course lesson titles must be strings or contain a string 'title'.")
    return title


def iter_course_lessons(course_slug):
    course = COURSES[course_slug]
    for module_index, module in enumerate(course["modules"], start=1):
        module_slug = f"module-{module_index:02d}-{slugify(module['title'])}"
        for lesson_index, lesson_entry in enumerate(module["lessons"], start=1):
            title = _lesson_title(lesson_entry)
            is_foundation_lesson = lesson_index == 1
            objectives = (
                module["objectives"][:1]
                if is_foundation_lesson
                else module["objectives"][1:]
            )
            lesson_steps = (
                module["steps"][:2]
                if is_foundation_lesson
                else module["steps"][1:]
            )
            yield {
                "slug": lesson_entry.get("slug", f"{module_slug}-lesson-{lesson_index}")
                if isinstance(lesson_entry, dict)
                else f"{module_slug}-lesson-{lesson_index}",
                "title": title,
                "module_index": module_index,
                "module_slug": module_slug,
                "module_title": module["title"],
                "lesson_index": lesson_index,
                "objectives": [
                    ("Explain" if is_foundation_lesson else "Apply") + f" {title.lower()}",
                    *objectives,
                ],
                "explanation": f"{module['explanation']} This lesson focuses on {title.lower()}.",
                "steps": lesson_steps,
                "real_world": module["real_world"],
                "example": module["example"],
                "exercise": (
                    module["exercise"]
                    if is_foundation_lesson
                    else f"{module['exercise']} Extend your solution by explaining how it applies to {title.lower()}."
                ),
                "quiz": [module["quiz"][lesson_index - 1]],
            }
