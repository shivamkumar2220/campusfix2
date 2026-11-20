# Module 5 – Frontend: Login Page

**Owner:** Member 5  **Files:** `frontend/index.html`, `login.js`, `login.css`, shared `common.js`, `style.css`, and `start.bat`

## What it does
The first screen. Users log in with email + password or with GitHub. Also holds the **shared** code and design both pages use, and the one-click start file.

## Files
| File | Job |
|------|-----|
| `index.html` | Login form, "or", GitHub button, (hidden) Google button, message line |
| `login.js` | `login()`, `loginPage()`, `googleButton()`, `googleLogin()` |
| `login.css` | Centre the card, GitHub button style |
| `common.js` *(shared)* | `$()`, `api()`, `show()` – used by both pages |
| `style.css` *(shared)* | Colours, fonts, card, inputs, buttons |
| `start.bat` | Makes the venv, installs packages, loads `secrets.bat`, starts the server, opens the browser |

> `common.js` and `style.css` are used by Module 6 too – talk to Member 6 before changing them.

## Shared helpers – `common.js`
```javascript
const $ = (id) => document.getElementById(id);           // short way to find an element

function api(url, body) {                                 // call the server
    return fetch(url, body && { method: "POST",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
}                                                         // with body → POST JSON, without → GET

function show(text, ok) { ... }                           // green (ok) or red message
```

## Login flow
```
User fills email + password → clicks "Log in"
   → login() → api("/api/login", {email, password})
        ├─ OK    → go to home.html
        └─ error → show("Wrong email or password", false)   (red)
```

## Which buttons appear – `loginPage()`
Runs when the page opens (`<body onload="loginPage()">`):
1. Asks `/api/login-options` → `{"google": "", "github": true}`
2. GitHub set up → shows the black **Sign in with GitHub** button and the "or" line.
3. URL has `?error=github` (GitHub login failed) → shows a red message.

The GitHub button is just a link to `/api/github-login`; the server does the rest (Module 2).
The Google button only appears if `GOOGLE_CLIENT_ID` is set.

## `start.bat` – one click to run
```
cd to project folder
call secrets.bat               (GitHub keys, if the file exists)
make venv if missing
pip install -r requirements.txt
open http://localhost:8002
start uvicorn server
```

## How to test
- Open http://localhost:8002 → card in the middle, GitHub button visible.
- Wrong password → red message. Right password → complaints page.
- Make the window narrow → the card still fits (mobile friendly).

## Viva questions
| Question | Answer |
|----------|--------|
| How does the frontend talk to the backend? | `fetch()` sends JSON to `/api/...` URLs and reads the JSON reply. |
| Why `async/await`? | Server calls take time; `await` waits for the answer without freezing the page. |
| Where is the login remembered? | In an HttpOnly cookie set by the server – JavaScript does not store any password or token. |
| Why split into common.js / login.js? | Two people can work on two pages without editing the same file. |
| What does `onsubmit="login(); return false;"` do? | Runs our function and stops the browser from reloading the page. |
