const API_BASE_URL = "http://127.0.0.1:8000";

let allDevelopers = [];
let allTasks = [];

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    await fetchStats();
    await fetchDevelopers();
    await fetchTasks();
    setupEventListeners();
}

// Fetch dashboard stats
async function fetchStats() {
    try {
        let devRes = await fetch(`${API_BASE_URL}/developers`);
        let taskRes = await fetch(`${API_BASE_URL}/tasks`);

        if (!devRes.ok || !taskRes.ok) {
            devRes = await fetch(`${API_BASE_URL}/api/developers`);
            taskRes = await fetch(`${API_BASE_URL}/api/tasks`);
        }

        if (devRes.ok && taskRes.ok) {
            allDevelopers = await devRes.json();
            allTasks = await taskRes.json();

            const devCount = document.getElementById("total-developers");
            const taskCount = document.getElementById("total-tasks");

            if (devCount) devCount.textContent = allDevelopers.length || 0;
            if (taskCount) taskCount.textContent = allTasks.length || 0;

            populateDeveloperDropdown(allDevelopers);
        }
    } catch (error) {
        console.error("Error fetching stats:", error);
    }
}

// Fetch developers list
async function fetchDevelopers() {
    try {
        let res = await fetch(`${API_BASE_URL}/developers`);
        if (!res.ok) res = await fetch(`${API_BASE_URL}/api/developers`);

        if (res.ok) {
            allDevelopers = await res.json();
            renderDevelopersTable(allDevelopers);
        }
    } catch (error) {
        console.error("Error fetching developers:", error);
    }
}

// Fetch tasks list
async function fetchTasks() {
    try {
        let res = await fetch(`${API_BASE_URL}/tasks`);
        if (!res.ok) res = await fetch(`${API_BASE_URL}/api/tasks`);

        if (res.ok) {
            allTasks = await res.json();
            renderTasksTable(allTasks);
        }
    } catch (error) {
        console.error("Error fetching tasks:", error);
    }
}

// Populate Developer Dropdown for Recommendations
function populateDeveloperDropdown(developers) {
    const devSelect = document.getElementById("developer-select");
    if (!devSelect) return;

    devSelect.innerHTML = '<option value="">-- Select Developer --</option>';
    developers.forEach(dev => {
        const option = document.createElement("option");
        option.value = dev.id || dev.developer_id;
        const skillsText = Array.isArray(dev.skills) ? dev.skills.join(", ") : (dev.skills || "No skills listed");
        option.textContent = `${dev.name} (${skillsText})`;
        devSelect.appendChild(option);
    });
}

// Fetch Recommendations
async function fetchRecommendations(developerId) {
    const container = document.getElementById("recommendations-list");
    if (!container) return;

    container.innerHTML = '<p class="text-center">Loading recommendations...</p>';

    try {
        const topNSelect = document.getElementById("top-n-select");
        const topN = topNSelect ? topNSelect.value : 10;

        let res = await fetch(`${API_BASE_URL}/recommend?developer_id=${developerId}&top_n=${topN}`);
        if (!res.ok) {
            res = await fetch(`${API_BASE_URL}/api/recommend?developer_id=${developerId}&top_n=${topN}`);
        }

        if (res.ok) {
            const recommendations = await res.json();
            renderRecommendations(recommendations);
        } else {
            container.innerHTML = '<p class="text-center text-danger">Failed to load recommendations.</p>';
        }
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        container.innerHTML = '<p class="text-center text-danger">Error connecting to server.</p>';
    }
}

// Render Recommendations Table
function renderRecommendations(tasks) {
    const container = document.getElementById("recommendations-list");
    if (!container) return;

    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p class="text-center">No recommendations found for this developer.</p>';
        return;
    }

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>TASK TITLE</th>
                    <th>REQUIRED SKILLS</th>
                    <th>DIFFICULTY</th>
                    <th>EST. HOURS</th>
                    <th>MATCH SCORE</th>
                </tr>
            </thead>
            <tbody>
    `;

    tasks.forEach(task => {
        const title = task.title || task.task_title || "N/A";
        const skills = Array.isArray(task.required_skills) ? task.required_skills.join(", ") : (task.required_skills || "N/A");
        const difficulty = task.difficulty || "Medium";
        const hours = task.est_hours || task.estimated_hours || "N/A";
        const score = task.score ? (task.score * 100).toFixed(1) + "%" : "N/A";

        html += `
            <tr>
                <td><strong>${title}</strong></td>
                <td>${skills}</td>
                <td><span class="badge badge-info">${difficulty}</span></td>
                <td>${hours} hrs</td>
                <td><strong class="text-success">${score}</strong></td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

// Render Developers Roster Table
function renderDevelopersTable(developers) {
    const container = document.getElementById("developers-list");
    if (!container) return;

    if (!developers || developers.length === 0) {
        container.innerHTML = '<p class="text-center">No developers found.</p>';
        return;
    }

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>NAME</th>
                    <th>SKILLS</th>
                    <th>EXPERIENCE</th>
                </tr>
            </thead>
            <tbody>
    `;

    developers.forEach(dev => {
        const id = dev.id || dev.developer_id || "N/A";
        const skills = Array.isArray(dev.skills) ? dev.skills.join(", ") : dev.skills;
        const exp = dev.experience_level || dev.experience_years || dev.experience || "N/A";

        html += `
            <tr>
                <td>${id}</td>
                <td><strong>${dev.name}</strong></td>
                <td>${skills}</td>
                <td>${exp}</td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

// Render Tasks Backlog Table
function renderTasksTable(tasks) {
    const container = document.getElementById("tasks-list");
    if (!container) return;

    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p class="text-center">No tasks found.</p>';
        return;
    }

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>TASK TITLE</th>
                    <th>REQUIRED SKILLS</th>
                    <th>DIFFICULTY</th>
                    <th>EST. HOURS</th>
                </tr>
            </thead>
            <tbody>
    `;

    tasks.forEach(task => {
        const id = task.id || task.task_id || "N/A";
        const skills = Array.isArray(task.required_skills) ? task.required_skills.join(", ") : task.required_skills;
        const hours = task.est_hours || task.estimated_hours || "N/A";

        html += `
            <tr>
                <td>${id}</td>
                <td><strong>${task.title}</strong></td>
                <td>${skills}</td>
                <td>${task.difficulty}</td>
                <td>${hours} hrs</td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

// Event Listeners
function setupEventListeners() {
    const devSelect = document.getElementById("developer-select");
    if (devSelect) {
        devSelect.addEventListener("change", (e) => {
            if (e.target.value) {
                fetchRecommendations(e.target.value);
            }
        });
    }

    // Add Developer Form Handler
    const addDevBtn = document.getElementById("add-developer-btn");
    if (addDevBtn) {
        addDevBtn.addEventListener("click", async () => {
            const name = document.getElementById("dev-name")?.value;
            const skills = document.getElementById("dev-skills")?.value;
            const exp = document.getElementById("dev-exp")?.value;

            if (!name || !skills) return alert("Please fill in developer details!");

            try {
                let res = await fetch(`${API_BASE_URL}/developers`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, skills: skills.split(",").map(s => s.trim()), experience_level: exp })
                });

                if (res.ok) {
                    initApp();
                }
            } catch (err) {
                console.error("Error adding developer:", err);
            }
        });
    }

    // Add Task Form Handler
    const addTaskBtn = document.getElementById("add-task-btn");
    if (addTaskBtn) {
        addTaskBtn.addEventListener("click", async () => {
            const title = document.getElementById("task-title")?.value;
            const skills = document.getElementById("task-skills")?.value;
            const diff = document.getElementById("task-difficulty")?.value;
            const hours = document.getElementById("task-hours")?.value;

            if (!title || !skills) return alert("Please fill in task details!");

            try {
                let res = await fetch(`${API_BASE_URL}/tasks`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, required_skills: skills.split(",").map(s => s.trim()), difficulty: diff, est_hours: parseInt(hours) || 8 })
                });

                if (res.ok) {
                    initApp();
                }
            } catch (err) {
                console.error("Error adding task:", err);
            }
        });
    }
}