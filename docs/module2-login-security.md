# Module 2 – Login & Security

**Owner:** Member 2  **Files:** `backend/auth.py`, `backend/main.py`, `secrets.bat` (not on GitHub)

## What it does
Checks who the user is, remembers them with a **session cookie**, and makes sure students and staff can only do their own work.

## APIs
| Method | URL | What it does |
|--------|-----|--------------|
| POST | `/api/login` | Email + password login |
| GET | `/api/github-login` | Step 1 of GitHub login – sends user to GitHub |
| GET | `/api/github-callback` | Step 2 – GitHub sends the user back here |
| POST | `/api/google-login` | Google login (code ready, switched off for now) |
| GET | `/api/login-options` | Tells the login page which buttons to show |
| POST | `/api/logout` | Clears the session |
| GET | `/api/me` | Who is logged in |

## 1. Password login
```
email + password ──▶ find user by email ──▶ bcrypt.checkpw(password, hash)
                                              ├─ wrong → count the try, "Wrong email or password"
                                              └─ right → save {id, name, role} in the session cookie
```
**Too many tries:** 5 wrong passwords in 5 minutes → blocked for 5 minutes (`wrong_tries` dictionary).

## 2. Session cookie
`main.py` adds `SessionMiddleware`. After login the user's `{id, name, role}` is stored in a cookie that is **signed** with `SECRET_KEY`, so the browser cannot change it (for example, make itself staff). The cookie is `HttpOnly`, so JavaScript cannot read it.

## 3. Roles – the `user()` function
```python
def user(request, role=None):
    # no session        → 401 "Please log in"
    # wrong role        → 403 "Only staff can do this"
    # otherwise         → returns {id, name, role}
```
Every API calls `user(request)` or `user(request, "staff")` / `user(request, "student")` first.

## 4. GitHub login (OAuth)
```
① User clicks "Sign in with GitHub"
② /api/github-login  → save a random "state" in the session → redirect to github.com
③ User clicks "Authorize" on GitHub
④ GitHub → /api/github-callback?code=...&state=...
⑤ Server checks state matches (stops fake callbacks)
⑥ Server sends code + client secret to GitHub → gets an access token
⑦ Server asks GitHub for the user's verified primary email and name
⑧ login_by_email(): email exists → log in with that role; new email → create as student
```
Staff cannot be created by GitHub login. To make someone staff:
`UPDATE users SET role='staff' WHERE email='someone@gmail.com';`

## 5. Keeping keys secret
`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GOOGLE_CLIENT_ID` live in `secrets.bat`, which is in `.gitignore`. `start.bat` loads it. `secrets.example.bat` (empty) is on GitHub so the team knows what to fill.

## How to test
- Wrong password → red message. 6 wrong tries → "Too many tries".
- Log in as a student, open http://localhost:8002/api/me → shows your name and role.
- GitHub button → Authorize → lands on the complaints page.

## Viva questions
| Question | Answer |
|----------|--------|
| What is a session? | Server remembers the logged-in user using a signed cookie sent with every request. |
| 401 vs 403? | 401 = not logged in. 403 = logged in but not allowed (wrong role). |
| What is OAuth? | Logging in through another site (GitHub). We never see the user's GitHub password. |
| Why the `state` value? | Random code saved before going to GitHub and checked when coming back, so an attacker cannot fake the callback. |
| Why is the client secret not in the code? | The repo is public. Anyone with the secret could pretend to be our app. |
