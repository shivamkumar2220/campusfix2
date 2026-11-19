// Send email + password to the server. If correct, open the complaint page.
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password })
    });

    if (response.ok) {
        const student = await response.json();
        localStorage.setItem("student", JSON.stringify(student)); // remember who logged in
        window.location.href = "complaint.html";
    } else {
        document.getElementById("message").innerText = "Wrong email or password";
        document.getElementById("message").className = "error";
    }
}
