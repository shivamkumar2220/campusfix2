@echo off
REM Copy this file to secrets.bat and fill in the keys (ask Member 2 privately).
REM secrets.bat is in .gitignore so real keys never go to GitHub.

set GITHUB_CLIENT_ID=
set GITHUB_CLIENT_SECRET=
set GOOGLE_CLIENT_ID=

REM Gmail that sends sign-up codes. Needs 2-Step Verification ON, then make an
REM App password at https://myaccount.google.com/apppasswords (16 letters)
set GMAIL_USER=
set GMAIL_APP_PASSWORD=
