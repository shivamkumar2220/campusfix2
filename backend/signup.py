# Email codes: create an account, or log in without a password.
# Sign up:    name + email + password -> we email a 6-digit code -> right code = account created (student) + logged in.
#             Nothing is saved in the database until the email is verified.
# Code login: email of an existing account -> we email a code -> right code = logged in.
# Codes are sent from a real Gmail account and kept only as bcrypt hashes.
import os
import re
import secrets
import smtplib
import time
from email.message import EmailMessage

import bcrypt
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.auth import start_session
from backend.db import sql

router = APIRouter()

# The Gmail account that sends the codes, set in secrets.bat.
# GMAIL_APP_PASSWORD is a 16-letter "App password" (Google Account > Security > App passwords), not the normal password.
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")

CODE_MINUTES = 10    # a code works for 10 minutes
MAX_TRIES = 5        # 5 wrong codes = ask for a new one
RESEND_SECONDS = 60  # wait 1 minute before asking for a new code
signup_codes = {}    # email -> {code_hash, name, sent, expires, tries, password_hash}
login_codes = {}     # email -> {code_hash, name, sent, expires, tries}


class Email(BaseModel):
    email: str


class EmailCode(Email):
    code: str


class Signup(Email):
    name: str
    password: str


# Send the code by email through Gmail's mail server (encrypted SSL connection)
def send_code(email, name, code):
    message = EmailMessage()
    message["Subject"] = "Your CampusFix code: " + code
    message["From"] = "CampusFix <" + GMAIL_USER + ">"
    message["To"] = email
    message.set_content(f"Hi {name},\n\nYour CampusFix verification code is: {code}\n\n"
                        f"It works for {CODE_MINUTES} minutes. If you did not ask for this code, ignore this email.")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(message)


# Make a random 6-digit code, email it, and remember its hash in "store" (plus any extra data)
def new_code(store, email, name, **extra):
    now = time.time()
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise HTTPException(503, "Email codes are not set up yet (no Gmail sender in secrets.bat)")
    if email in store and now - store[email]["sent"] < RESEND_SECONDS:
        raise HTTPException(429, "A code was just sent. Wait a minute before asking again.")
    code = f"{secrets.randbelow(1000000):06d}"  # e.g. 042917
    try:
        send_code(email, name, code)
    except Exception:
        raise HTTPException(502, "Could not send the email. Check the address and try again.")
    store[email] = {"code_hash": bcrypt.hashpw(code.encode(), bcrypt.gensalt(8)), "name": name,
                    "sent": now, "expires": now + CODE_MINUTES * 60, "tries": 0, **extra}
    return {"sent": True}


# Check a typed code. Right code = return the saved data and forget it (a code works only once).
def check_code(store, email, code):
    saved = store.get(email)
    if not saved or time.time() > saved["expires"]:
        store.pop(email, None)
        raise HTTPException(400, "The code has expired. Please ask for a new one.")
    if saved["tries"] >= MAX_TRIES:
        store.pop(email)
        raise HTTPException(429, "Too many wrong codes. Please ask for a new one.")
    if not bcrypt.checkpw(code.strip().encode(), saved["code_hash"]):
        saved["tries"] += 1
        raise HTTPException(401, f"Wrong code ({MAX_TRIES - saved['tries']} tries left)")
    return store.pop(email)


@router.post("/api/signup")
def signup_start(data: Signup):
    name, email, password = data.name.strip(), data.email.strip().lower(), data.password
    if not name or len(name) > 60:
        raise HTTPException(400, "Please enter your name")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
        raise HTTPException(400, "Please enter a real email address")
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(400, "Password needs at least 8 characters, with letters and numbers")
    if sql("SELECT 1 FROM users WHERE email = %s", (email,)):
        raise HTTPException(409, "This email already has an account. Please log in.")
    return new_code(signup_codes, email, name, password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode())


@router.post("/api/signup/verify")
def signup_verify(data: EmailCode, request: Request):
    email = data.email.strip().lower()
    saved = check_code(signup_codes, email, data.code)
    rows = sql("INSERT INTO users (name, email, role, password_hash) VALUES (%s, %s, 'student', %s) "
               "ON CONFLICT (email) DO NOTHING RETURNING id, name, role", (saved["name"], email, saved["password_hash"]))
    if not rows:
        raise HTTPException(409, "This email already has an account. Please log in.")
    return start_session(request, rows[0])


@router.post("/api/code-login")
def code_login_start(data: Email):
    email = data.email.strip().lower()
    rows = sql("SELECT name FROM users WHERE email = %s", (email,))
    if not rows:
        raise HTTPException(404, "No account with this email. Please create an account first.")
    return new_code(login_codes, email, rows[0][0])


@router.post("/api/code-login/verify")
def code_login_verify(data: EmailCode, request: Request):
    email = data.email.strip().lower()
    check_code(login_codes, email, data.code)
    rows = sql("SELECT id, name, role FROM users WHERE email = %s", (email,))
    if not rows:
        raise HTTPException(404, "No account with this email.")
    return start_session(request, rows[0])
