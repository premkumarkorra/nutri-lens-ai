# NutriLens AI — Personalized Food Label & Allergy Analyzer

NutriLens AI is a production-quality, full-stack web application designed to analyze food ingredient labels and provide personalized, explainable nutrition and allergy warnings. It extracts ingredients from label photographs, parses compound items, maps chemical/scientific names to a canonical database, and screens them against the user's saved health profile.

---

## Key Features

*   **Secure Authentication & Session Management**: Secure hashing using `pbkdf2:sha256` and stateful Flask sessions.
*   **Dual-Database Support**: Out-of-the-box SQLite zero-configuration database fallback with support for full MySQL database production environments.
*   **Image Processing & OCR**: Integrated PIL binarization/grayscale preprocessing and Tesseract OCR text extraction.
*   **Intelligent Ingredient Parser**: Cleans noise, splits compound items (comma boundaries), handles nested sub-ingredients in parentheses, and removes percentages.
*   **Comprehensive Knowledge Base**: Seeded with major allergen categories, E-numbers, chemical/scientific aliases, vegan/vegetarian safety rules, and healthier alternatives.
*   **Personalization Rule Engine**: Calculates risk levels (**SAFE**, **CAUTION**, or **AVOID**) for each ingredient based on allergen status (direct vs. derivative), health goals (e.g. Low Sugar, Low Sodium), dietary preferences (Vegan, Vegetarian), and explicit blocklists.
*   **Explainable AI Results**: Informational details mapping every warning to its specific profile trigger, confidence level, and actionable alternatives.
*   **Dark Professional UI**: Premium, high-end dashboard styled with modern typography, smooth animations, webcam snapshot capture, drag-and-drop uploads, and responsive layouts.

---

## Tech Stack

### Backend
- **Language**: Python 3
- **Web Framework**: Flask 3.0.3
- **Database Drivers**: PyMySQL 1.1.1 (for MySQL)
- **Environment Management**: python-dotenv 1.0.1
- **Security**: cryptography 42.0.8 (password hashing with pbkdf2:sha256)

### Frontend
- **Markup**: HTML5
- **Styling**: CSS3 (custom modern dark theme)
- **Client Logic**: Vanilla JavaScript (no frameworks)
- **Features**: Responsive design, WebCam capture API, drag-and-drop file uploads

### Data & Storage
- **Primary Database**: SQLite (development/zero-config deployment)
- **Production Database**: MySQL (enterprise deployments)
- **Schema**: Relational SQL with full migrations support

### Image Processing & OCR
- **Image Manipulation**: Pillow (PIL) 10.4.0
- **OCR Engine**: Tesseract OCR (via pytesseract 0.3.10)
- **Computer Vision**: OpenCV 4.8.1.78
- **Image Preprocessing**: Binarization and grayscale conversion for OCR accuracy

### Data Processing
- **Numerical Computing**: NumPy 1.24.3

### Authentication & Session Management
- **Password Hashing**: PBKDF2-SHA256
- **Session Management**: Flask stateful sessions
- **Type**: Secure server-side session storage

---

## Project Structure

```text
NUTRISCAN/
├── app.py                      # Flask application entry point
├── config.py                   # Environment variable loader & startup image generator
├── requirements.txt            # Python package dependencies
├── .env                        # Local active configuration settings
├── .env.example                # Sample environment template
├── test_app.py                 # Automated unit and integration test suite
│
├── database/
│   ├── connection.py           # MySQL / SQLite switcher and execution wrapper
│   ├── schema.sql              # Relational SQL schema definitions
│   └── seed_data.py            # Prepopulated ingredients, allergens, and demo profiles
│
├── routes/
│   ├── auth.py                 # Login, Registration, Session checks
│   ├── profile.py              # User dietary options & avoid lists
│   ├── scan.py                 # File upload, OCR, and history lookups
│   └── analysis.py             # Match parser, rule executor, and saver
│
├── services/
│   ├── ocr_service.py          # Image processor and pytesseract integration
│   ├── ingredient_parser.py    # Ingredient text cleaner and splitter
│   ├── knowledge_base.py       # Ingredient & alias mappings queries
│   ├── personalization.py      # Core rules and status calculator
│   └── recommendation.py       # Alternatives matching service
│
├── templates/
│   └── index.html              # Main Single Page App (SPA) template
│
└── static/
    ├── css/
    │   └── style.css           # Premium dark-theme stylesheet
    └── js/
        └── app.js              # SPA router, API controller, webcam capture
```

---

## Getting Started

### 1. Installation

1.  Clone or navigate to the `NUTRISCAN` workspace folder.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # Windows Command Prompt:
    venv\Scripts\activate
    # macOS/Linux Terminal:
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Running the Application

Start the Flask local development server:
```bash
python app.py
```

*   **Database Auto-Initialization**: On startup, if no MySQL credentials are set, the app creates a local SQLite database file `nutrilens.db`, runs the schema migration, and seeds the default ingredients, aliases, and demo user accounts.
*   **Sample Image Auto-Generation**: On startup, the configuration manager generates 4 sample food label images (`label_milk.jpg`, `label_peanut.jpg`, `label_soy.jpg`, `label_generic.jpg`) inside the `static/images/` directory. You can use these to test files directly from your desktop browse window!
*   **Open in Browser**: Open your web browser and navigate to: `http://127.0.0.1:5000`

---

## Database Configuration

By default, NutriLens AI runs on **SQLite**. To switch to a **MySQL** server:

1.  Open your `.env` file in the root directory.
2.  Change `DB_TYPE` to `mysql`.
3.  Uncomment and fill in your MySQL connection details:
    ```ini
    DB_TYPE=mysql
    MYSQL_HOST=localhost
    MYSQL_USER=your_username
    MYSQL_PASSWORD=your_password
    MYSQL_DATABASE=nutrilens
    ```
4.  Ensure your MySQL server is running and the database (`nutrilens`) is created. Restart `app.py` to trigger the schema migrations and seeding.

---

## Tesseract OCR Installation

To enable real OCR on photos:

1.  Install Tesseract OCR binary on your computer:
    *   **Windows**: Download installer from [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
    *   **macOS**: Run `brew install tesseract`.
    *   **Linux**: Run `sudo apt-get install tesseract-ocr`.
2.  If the Tesseract binary is not automatically added to your system environment variables (common on Windows), locate the installation path (e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`) and set it in your `.env` file:
    ```ini
    TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
    ```

> **Note on OCR Fallback**: If Tesseract is not installed or configured, the application detects this and enters **Simulation Mode**. In this mode, uploading an image will still parse successfully using realistic mock text based on the file name. Users can also manually type and edit ingredients in the textarea.

---

## Running Automated Tests

A comprehensive suite of unit and integration tests is located in `test_app.py`. To run them:
```bash
python test_app.py
```

---

## Demo Test Scenarios

Log in with any of the seeded profiles to test the personalization engine:

### Scenario A — Milk Allergy & Vegetarian
*   **Credentials**: Username `usera` | Password `Password123`
*   **Action**: Select the camera or browse files. Upload `static/images/label_milk.jpg`.
*   **Expected Results**:
    *   Overall Status: **AVOID**
    *   Warnings: `Whey Protein Isolate` flagged as **AVOID** because it is a milk derivative.
    *   Health suggestions: Safer dairy alternatives are recommended (Oat milk, Pea protein).

### Scenario B — Peanut Allergy & Vegan
*   **Credentials**: Username `userb` | Password `Password123`
*   **Action**: Upload `static/images/label_peanut.jpg`.
*   **Expected Results**:
    *   Overall Status: **AVOID**
    *   Warnings: `Peanut Flour` flagged as **AVOID** (Direct Peanut allergen). `Carmine` flagged as **AVOID** (animal-derived coloring, violates Vegan diet).
    *   Health suggestions: Alternatives like Sunflower seed flour, Beetroot extract.

### Scenario C — Soy Allergy & Low Sugar Goal
*   **Credentials**: Username `userc` | Password `Password123`
*   **Action**: Upload `static/images/label_generic.jpg`.
*   **Expected Results**:
    *   Overall Status: **AVOID**
    *   Warnings: `Soy Lecithin` flagged as **AVOID** (Soy allergen derivative). `High Fructose Corn Syrup` and `Maltodextrin` flagged as **CAUTION** (triggers warning for the user's Low Sugar goal).
