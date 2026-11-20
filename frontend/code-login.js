// Code login page (code-login.html): email -> code on email -> logged in, no password.
// Uses $, api, show from common.js

// Step 1: the server emails a login code (only if the account exists)
async function sendCode() {
    $("sendButton").disabled = true;
    show("Sending code...", true);
    const response = await api("/api/code-login", { email: $("email").value });
    $("sendButton").disabled = false;
    if (!response.ok) return show((await response.json()).detail, false);
    $("sentTo").textContent = $("email").value;
    $("step1").hidden = true;
    $("step2").hidden = false;
    $("code").focus();
    show("Code sent. Check your inbox (and spam folder).", true);
}

// Step 2: the server checks the code and sets the login cookie
async function verifyCode() {
    const response = await api("/api/code-login/verify", { email: $("email").value, code: $("code").value });
    if (response.ok) location.href = "home.html";
    else show((await response.json()).detail, false);
}

function backToStep1() {
    $("step2").hidden = true;
    $("step1").hidden = false;
    show("", true);
}
