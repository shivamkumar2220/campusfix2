# Module 6 – Frontend: Complaints Page

**Owner:** Member 6  **Files:** `frontend/home.html`, `home.js`, `home.css` (uses shared `common.js`, `style.css` from Module 5)

## What it does
The main screen after login. It looks different for students and staff:

| | Student | Staff |
|---|---------|-------|
| New complaint form | ✅ | ❌ hidden |
| Complaints shown | only their own | everyone's |
| Priority / Status | read only (coloured text, badge) | dropdowns to change them |

## Files
| File | Job |
|------|-----|
| `home.html` | Header (name + Log out), complaint form, complaints table |
| `home.js` | `start()`, `loadComplaints()`, `menu()`, `addComplaint()`, `logout()` |
| `home.css` | Header, form + table layout, table style, priority colours |

## Functions in `home.js`
| Function | What it does |
|----------|--------------|
| `start()` | Runs on page open. Asks `/api/me`. Not logged in → back to login page. Shows name, shows form only to students, loads the table. |
| `loadComplaints()` | Gets `/api/complaints` and builds one table row per complaint. |
| `menu(c, field, options)` | Staff only – makes a dropdown; when changed, saves it with `/api/complaints/{id}/{field}`. |
| `addComplaint()` | Student only – sends the form, shows "Category: … Priority: … (score …)", clears the form, reloads the table. |
| `logout()` | Calls `/api/logout`, goes back to the login page. |

## Page flow
```
home.html opens → start()
   ├─ /api/me fails → index.html (login)
   └─ ok → me = {id, name, role}
           ├─ student → show form
           └─ loadComplaints()
                 for each complaint → insert row
                    ├─ staff   → priority + status dropdowns
                    └─ student → coloured priority + status badge
```

## Safety: no XSS
Text typed by users (title, description) is put in the page with **`textContent`**, never `innerHTML`.
So if someone types `<script>alert(1)</script>` as a title, it is shown as plain text, not run.

## Design
- Form and table sit **side by side**, and wrap one under the other on phones (`flex-wrap`).
- Staff have no form, so the table takes the full width.
- Priority colours: **Critical** dark red, **High** red, **Medium** orange, **Low** grey (`.Critical`, `.High` … in `home.css`).

## How to test
1. Log in as a student → fill the form → green message with category and priority → new row appears.
2. Log in as staff → no form, all complaints, change a status → green "Complaint #… status: …".
3. Log out → back to the login page; opening home.html again sends you to login.

## Ideas for next modules
Search / filter box, dashboard counts (open / resolved), staff comments under a complaint.

## Viva questions
| Question | Answer |
|----------|--------|
| What is the DOM? | The page as objects JavaScript can change – we add table rows with `insertRow()`. |
| What is XSS and how do you stop it? | Injecting script through user text. We use `textContent`, so text is never run as HTML. |
| How do students and staff get different pages? | Same page; `start()` checks `me.role` and shows or hides parts. The server also checks the role, so hiding is not the only protection. |
| Why reload the table after adding? | To show the new complaint with the category and priority the server gave it. |
