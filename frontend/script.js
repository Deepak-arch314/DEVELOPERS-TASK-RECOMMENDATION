let allDevelopers = [];
let allTasks = [];

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    try {
        const response = await fetch("./data.json");
        const data = await response.json();

        allDevelopers = data.developers || [];
        allTasks = data.tasks || [];

        // Update counts
        const devCountEl = document.getElementById("total-developers");
        const taskCountEl = document.getElementById("total-tasks");
        if (devCountEl) devCountEl.textContent = allDevelopers.length;
        if (taskCountEl) taskCountEl.textContent = allTasks.length;

        // Render lists and dropdowns
        populateDeveloperDropdown(allDevelopers);
        renderDevelopersTable(allDevelopers);
        renderTasksTable(allTasks);
        setupEventListeners();
    } catch (error) {
        console.error("Error loading sample data:", error);
    }
}

// Populate Developer Dropdown
function populateDeveloperDropdown(developers) {
    const devSelect = document.getElementById("developer-select");
    if (!devSelect) return;

    devSelect.innerHTML = '<option value="">-- Select a Developer --</option>';
    developers.forEach(dev => {
        const option = document.createElement("option");
        option.value = dev.id;
        option.textContent = `${dev.name} (${dev.skills.join(", ")})`;
        devSelect.appendChild(option);
    });
}

// Generate Task Recommendations directly in JS (Pure Frontend Logic)
function generateRecommendations(developerId) {
    const container = document.getElementById("recommendations-list");
    if (!container) return;

    const dev = allDevelopers.find(d => d.id == developerId);
    if (!dev) return;

    // Calculate match score based on skill overlap
    const devSkills = dev.skills.map(s => s.toLowerCase());
    
    let scoredTasks = allTasks.map(task => {
        const reqSkills = task.required_skills.map(s => s.toLowerCase());
        const matchingSkills = reqSkills.filter(s => devSkills.includes(s));
        const score = reqSkills.length > 0 ? (matchingSkills.length / reqSkills.length) : 0;
        return { ...task, score };
    });

    // Sort highest match first
    scoredTasks.sort((a, b) => b.score - a.score);

    const topNSelect = document.getElementById("top-n-select");
    const topN = topNSelect ? parseInt(topNSelect.value, 10) : 10;
    renderRecommendations(scoredTasks.slice(0, topN));
}

// Render Recommendations Table
function renderRecommendations(tasks) {
    const container = document.getElementById("recommendations-list");
    if (!container) return;

    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p class="text-center">No recommendations found.</p>';
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
        html += `
            <tr>
                <td><strong>${task.title}</strong></td>
                <td>${Array.isArray(task.required_skills) ? task.required_skills.join(", ") : task.required_skills}</td>
                <td><span class="badge badge-info">${task.difficulty}</span></td>
                <td>${task.est_hours} hrs</td>
                <td><strong class="text-success">${(task.score * 100).toFixed(0)}%</strong></td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

// Render Developers Table
function renderDevelopersTable(developers) {
    const container = document.getElementById("developers-list");
    if (!container) return;

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>NAME</th>
                    <th>PRIMARY SKILLS</th>
                    <th>EXPERIENCE LEVEL</th>
                </tr>
            </thead>
            <tbody>
    `;

    developers.forEach(dev => {
        html += `
            <tr>
                <td><strong>${dev.name}</strong></td>
                <td>${dev.skills.join(", ")}</td>
                <td>${dev.experience_level}</td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

// Render Tasks Table
function renderTasksTable(tasks) {
    const container = document.getElementById("tasks-list");
    if (!container) return;

    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>TITLE</th>
                    <th>REQUIRED SKILLS</th>
                    <th>DIFFICULTY</th>
                    <th>EST. HOURS</th>
                </tr>
            </thead>
            <tbody>
    `;

    tasks.forEach(task => {
        html += `
            <tr>
                <td><strong>${task.title}</strong></td>
                <td>${task.required_skills.join(", ")}</td>
                <td>${task.difficulty}</td>
                <td>${task.est_hours} hrs</td>
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
                generateRecommendations(e.target.value);
            }
        });
    }

    const searchInput = document.getElementById("search-developer");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = allDevelopers.filter(d => 
                d.name.toLowerCase().includes(query) || 
                d.skills.some(s => s.toLowerCase().includes(query))
            );
            populateDeveloperDropdown(filtered);
        });
    }
}