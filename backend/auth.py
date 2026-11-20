# Authentication APIs: login (password, Google or GitHub), logout, who am I.
# Passwords are checked with bcrypt. The login is kept in a signed HttpOnly cookie (session).
import json
import os
import secrets
import time
import urllib.parse
import urllib.request

import bcrypt
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.db import sql

router = APIRouter()
wrong_tries = {}  # email -> times of wrong passwords (5 in 5 minutes = blocked)

# Keys for Google / GitHub login, set in secrets.bat (empty = that button is hidden)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")


class Login(BaseModel):
    email: str
    password: str


class GoogleLogin(BaseModel):
    credential: str  # the token the Google button gives the browser


# The logged-in user from the cookie. Pass role to allow only "student" or only "staff".
def user(request, role=None):
    u = request.session.get("user")
    if not u:
        raise HTTPException(401, "Please log in")
    if role and u["role"] != role:
        raise HTTPException(403, "Only " + role + " can do this")
    return u


# Log in a Google/GitHub user by email. New emails become students (staff are added in the database).
def login_by_email(request, email, name):
    email = email.lower()
    rows = sql("SELECT id, name, role FROM users WHERE email = %s", (email,))
    if not rows:  # password_hash "-" = no password, can't use the password form
        rows = sql("INSERT INTO users (name, email, role, password_hash) VALUES (%s, %s, 'student', '-') "
                   "RETURNING id, name, role", (name or email, email))
    request.session["user"] = {"id": rows[0][0], "name": rows[0][1], "role": rows[0][2]}
    return request.session["user"]


# Call a web API and read the JSON answer. data = form POST, token = logged-in GitHub user.
def get_json(url, data=None, token=None):
    req = urllib.request.Request(url, urllib.parse.urlencode(data).encode() if data else None,
                                 {"Accept": "application/json"})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    return json.load(urllib.request.urlopen(req, timeout=10))


@router.post("/api/login")
def login(data: Login, request: Request):
    email, now = data.email.strip().lower(), time.time()
    tries = [t for t in wrong_tries.get(email, []) if now - t < 300]
    if len(tries) >= 5:
        raise HTTPException(429, "Too many tries. Wait 5 minutes.")
    rows = sql("SELECT id, name, role, password_hash FROM users WHERE email = %s", (email,))
    if not rows or not rows[0][3].startswith("$2") or not bcrypt.checkpw(data.password.encode(), rows[0][3].encode()):
        wrong_tries[email] = tries + [now]
        raise HTTPException(401, "Wrong email or password")
    wrong_tries.pop(email, None)
    request.session["user"] = {"id": rows[0][0], "name": rows[0][1], "role": rows[0][2]}
    return request.session["user"]


# Which login buttons to show on the login page
@router.get("/api/login-options")
def login_options():
    return {"google": GOOGLE_CLIENT_ID, "github": bool(GITHUB_CLIENT_ID)}


# Sign in with Google: ask Google if the token is real (made for OUR app, email verified)
@router.post("/api/google-login")
def google_login(data: GoogleLogin, request: Request):
    try:
        info = get_json("https://oauth2.googleapis.com/tokeninfo?id_token=" + urllib.parse.quote(data.credential))
    except Exception:
        raise HTTPException(401, "Google sign-in failed")
    if not GOOGLE_CLIENT_ID or info.get("aud") != GOOGLE_CLIENT_ID or info.get("email_verified") != "true":
        raise HTTPException(401, "Google sign-in failed")
    return login_by_email(request, info["email"], info.get("name"))


# Sign in with GitHub, step 1: send the user to GitHub's "Authorize CampusFix" page.
# "state" is a random code we check in step 2, so nobody can fake the callback.
@router.get("/api/github-login")
def github_login(request: Request):
    request.session["github_state"] = secrets.token_urlsafe(16)
    query = urllib.parse.urlencode({"client_id": GITHUB_CLIENT_ID, "scope": "user:email",
                                    "state": request.session["github_state"]})
    return RedirectResponse("https://github.com/login/oauth/authorize?" + query)


# Step 2: GitHub sends the user back here with a code. We swap the code for a token,
# then ask GitHub for the user's verified main email and name.
@router.get("/api/github-callback")
def github_callback(request: Request, code: str = "", state: str = ""):
    if not code or state != request.session.pop("github_state", None):
        return RedirectResponse("/index.html?error=github")
    try:
        token = get_json("https://github.com/login/oauth/access_token", {
            "client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code})["access_token"]
        emails = get_json("https://api.github.com/user/emails", token=token)
        email = next(e["email"] for e in emails if e["primary"] and e["verified"])
        name = get_json("https://api.github.com/user", token=token).get("name")
    except Exception:
        return RedirectResponse("/index.html?error=github")
    login_by_email(request, email, name)
    return RedirectResponse("/home.html")


@router.post("/api/logout")
def logout(request: Request):
    request.session.clear()


@router.get("/api/me")
def me(request: Request):
    return user(request)
