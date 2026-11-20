// Create account page (signup.html): details -> code on email -> account made.
// Uses $, api, show from common.js

// Step 1: send the details, the server emails a code
async function sendCode() {
    if ($("password").value !== $("password2").value) return show("Passwords do not match", false);
    $("sendButton").disabled = true;
    show("Sending code...", true);
    const response = await api("/api/signup", { name: $("name").value, email: $("email").value, password: $("password").value });
    $("sendButton").disabled = false;
    if (!response.ok) return show((await response.json()).detail, false);
    $("sentTo").textContent = $("email").value;
    $("step1").hidden = true;
    $("step2").hidden = false;
    $("code").focus();
    show("Code sent. Check your inbox (and spam folder).", true);
}

// Step 2: the server checks the code, creates the account and logs in
async function verifyCode() {
    const response = await api("/api/signup/verify", { email: $("email").value, code: $("code").value });
    if (response.ok) location.href = "home.html";
    else show((await response.json()).detail, false);
}

function backToStep1() {
    $("step2").hidden = true;
    $("step1").hidden = false;
    show("", true);
}
