# NutriScan Frontend README

This document is for the frontend layer of NutriScan only. It focuses on the HTML, CSS, and JavaScript that power the user experience for scanning ingredients, uploading product images, managing profile settings, and reviewing analysis results.

## Frontend Overview

NutriScan uses a single-page interface built with:

- HTML5 templates served by Flask
- Custom CSS for a dark, premium dashboard look
- Vanilla JavaScript for client-side state, navigation, forms, and API calls
- Browser features such as camera capture, drag-and-drop uploads, and toast notifications

The frontend is primarily located in:

- `templates/index.html`
- `static/css/`
- `static/js/app.js`
- `static/images/`

## Main Frontend Files

### `templates/index.html`
This file contains the app shell and all UI sections, including:

- landing page
- login/register forms
- scan screen
- product analysis modal
- profile page
- history page
- navigation and notification areas

### `static/css/`
The styling layer includes:

- `style.css` — base styling and layout
- `modern-ui.css` — polished dashboard patterns and UI components
- `luxury-ui.css` — premium visual treatments and elevated design details

### `static/js/app.js`
This is the main frontend logic file. It handles:

- SPA view switching
- auth state and session checks
- scan workflow and form handlers
- preset ingredient simulation
- product history loading
- profile loading and updates
- toast notifications
- API communication with Flask routes

## Frontend Workflow

The UI is designed around a client-side workflow:

1. User signs in or creates an account.
2. User enters ingredients manually or uploads an image.
3. Frontend sends a request to the backend API.
4. Result data is displayed in the UI.
5. User can review warnings, alternatives, and product history.

## Running the Frontend

Because this app is served through Flask, the frontend is launched with the application itself.

1. Open the project root.
2. Activate your virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
python app.py
```

5. Open the browser at:

```text
http://127.0.0.1:5000
```

## Frontend Development Notes

### UI changes
When editing HTML and CSS:

- update the relevant file in `templates/` or `static/css/`
- refresh the browser page to see the changes
- test across common screen sizes

### JavaScript changes
When editing frontend logic:

- work in `static/js/app.js`
- verify that DOM selectors match actual IDs/classes from `templates/index.html`
- test the login, scan, profile, and history flows after changes

### API integration
The frontend talks to backend endpoints such as:

- authentication routes
- scan routes
- analysis routes
- profile routes
- history routes

If an API contract changes, both the frontend and backend must be updated together.

## Common Frontend Tasks

- Modify button styles and layout
- Add a new view or section to the main page
- Improve the scan form UX
- Update dashboard cards or result presentation
- Adjust notifications and error handling
- Enhance mobile responsiveness
- Add new presets for demo ingredient testing

## Testing the Frontend

For UI-level validation, run the app locally and test:

- landing page rendering
- sign-in and sign-up flows
- ingredient entry and upload flow
- product analysis result display
- profile and history pages
- error and success notifications

## Important Considerations

- This app is not a separate React/Vue frontend; it is a Flask-rendered UI with vanilla JavaScript.
- Frontend behavior is tightly connected to backend endpoints and session logic.
- Camera and upload features depend on browser permissions and backend OCR processing.
- Some flows are gated by authentication state and require a valid logged-in session.

## Quick Reference

```text
templates/
  index.html

static/
  css/
    style.css
    modern-ui.css
    luxury-ui.css
  js/
    app.js
  images/
```

## Notes

This README exists to keep frontend-specific work isolated from the main project documentation. For backend architecture, deployment, database setup, or OCR pipeline details, refer to the main project README.
