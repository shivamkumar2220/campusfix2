// Home page (home.html): complaint form for students, complaint table for everyone.
// Uses $, api, show from common.js
let me; // the logged-in user: {id, name, role}

// Find out who is logged in, or go back to the login page
async function start() {
    const response = await fetch("/api/me");
    if (!response.ok) return (location.href = "index.html");
    me = await response.json();
    $("name").textContent = me.name + " (" + me.role + ")";
    $("new").hidden = me.role !== "student";
    loadComplaints();
}

// Fill the table. textContent is used so text typed by users is never run as HTML.
async function loadComplaints() {
    const complaints = await (await fetch("/api/complaints")).json();
    $("rows").innerHTML = complaints.length ? "" : "<tr><td colspan='9'>No complaints yet</td></tr>";
    for (const c of complaints) {
        const row = $("rows").insertRow();
        for (const key of ["id", "student", "title", "category"]) row.insertCell().textContent = c[key];
        const priority = row.insertCell();
        for (const key of ["location", "description", "date"]) row.insertCell().textContent = c[key];
        const status = row.insertCell();

        if (me.role === "staff") {
            // Staff can change priority (override the AI) and status
            priority.append(menu(c, "priority", ["Critical", "High", "Medium", "Low"]), " (" + c.score + ")");
            status.append(menu(c, "status", ["Open", "In Progress", "Resolved"]));
        } else {
            priority.textContent = c.priority + " (" + c.score + ")";
            const badge = document.createElement("span");
            badge.className = "badge";
            badge.textContent = c.status;
            status.append(badge);
        }
        priority.className = c.priority; // colour
    }
}

// Staff only: dropdown that saves a new value of "status" or "priority" when changed
function menu(c, field, options) {
    const select = document.createElement("select");
    select.innerHTML = options.map((o) => "<option>" + o + "</option>").join("");
    select.value = c[field];
    select.onchange = async () => {
        const response = await api("/api/complaints/" + c.id + "/" + field, { value: select.value });
        show(response.ok ? "Complaint #" + c.id + " " + field + ": " + select.value : "Could not save", response.ok);
    };
    return select;
}

// Student only: send the complaint. The server adds category (AI) and priority (priority engine).
async function addComplaint() {
    const complaint = {};
    for (const id of ["title", "location", "description", "severity", "academic_impact"]) complaint[id] = $(id).value;
    complaint.affected_students = Number($("affected_students").value);
    complaint.duration_hours = Number($("duration_hours").value);

    const response = await api("/api/complaints", complaint);
    if (!response.ok) return show("Could not save. Check the form.", false);
    const result = await response.json();
    show("Complaint saved! Category: " + result.category + ", Priority: " + result.priority + " (score " + result.score + ")", true);
    $("new").reset();
    loadComplaints();
}

// Forget the login cookie and go back to the login page
async function logout() {
    await api("/api/logout", {});
    location.href = "index.html";
}
