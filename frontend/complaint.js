// Read the logged-in student. If nobody is logged in, go back to the login page.
const student = JSON.parse(localStorage.getItem("student"));
if (!student) {
    window.location.href = "index.html";
}
document.getElementById("student-name").innerText = student.name;

// Send the form to the server so it is saved in the database
async function submitComplaint() {
    const complaint = {
        student_id: student.id,
        title: document.getElementById("title").value,
        location: document.getElementById("location").value,
        description: document.getElementById("description").value
    };

    const response = await fetch("/api/complaints", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(complaint)
    });

    const message = document.getElementById("message");
    if (response.ok) {
        message.innerText = "Complaint saved!";
        message.className = "success";
        document.querySelector("form").reset();
        loadComplaints();
    } else {
        message.innerText = "Could not save. Try again.";
        message.className = "error";
    }
}

// Get this student's complaints from the server and show them in the table
async function loadComplaints() {
    const response = await fetch("/api/complaints/" + student.id);
    const complaints = await response.json();

    let rows = "";
    for (const c of complaints) {
        rows += `<tr><td>${c.id}</td><td>${c.title}</td><td>${c.location}</td>
                 <td><span class="badge">${c.status}</span></td><td>${c.date}</td></tr>`;
    }
    document.getElementById("complaint-rows").innerHTML = rows || "<tr><td colspan='5'>No complaints yet</td></tr>";
}

// Forget the student and go back to the login page
function logout() {
    localStorage.removeItem("student");
    window.location.href = "index.html";
}

loadComplaints();
