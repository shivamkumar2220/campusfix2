// Login page (index.html): password, GitHub and Google login.
// Uses $, api, show from common.js

// The server checks the password and sets the login cookie
async function login() {
    const response = await api("/api/login", { email: $("email").value, password: $("password").value });
    if (response.ok) location.href = "home.html";
    else show((await response.json()).detail, false);
}

// Show a GitHub sign-in error, and the GitHub button if it is set up
async function loginPage() {
    if (location.search.includes("error=github")) show("GitHub sign-in failed. Try again.", false);
    const options = await (await fetch("/api/login-options")).json();
    if (options.github) $("github").hidden = $("or").hidden = false;
}

// Show the "Sign in with Google" button (only if a Google client id is set)
async function googleButton() {
    const options = await (await fetch("/api/login-options")).json();
    if (!options.google) return;
    google.accounts.id.initialize({ client_id: options.google, callback: googleLogin });
    google.accounts.id.renderButton($("google"), { theme: "outline", size: "large", text: "signin_with" });
    $("or").hidden = false;
}

// Google gives us a token, the server checks it with Google and sets the login cookie
async function googleLogin(answer) {
    const response = await api("/api/google-login", { credential: answer.credential });
    if (response.ok) location.href = "home.html";
    else show((await response.json()).detail, false);
}
