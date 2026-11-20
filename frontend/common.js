// Shared helpers used by both pages (login + home). Change only if both people agree.
const $ = (id) => document.getElementById(id);

// Call our API. With a body it sends a JSON POST, without it a GET.
function api(url, body) {
    return fetch(url, body && { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
}

// Show a green (ok) or red message
function show(text, ok) {
    $("message").textContent = text;
    $("message").className = ok ? "success" : "error";
}
