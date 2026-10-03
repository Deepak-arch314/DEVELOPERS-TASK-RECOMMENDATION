const API_BASE = 'http://127.0.0.1:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    loadDashboardStats();
    loadDevelopersDropdown();
    loadDevelopersList();
    loadTasksList();

    const devSelect = document.getElementById('developer-select');
    const topNSelect = document.getElementById('top-n-select');
    if (devSelect) devSelect.addEventListener('change', handleDeveloperChange);
    if (topNSelect) topNSelect.addEventListener('change', handleDeveloperChange);
});

function setupNavigation() {
    const navButtons = document.querySelectorAll('nav button');
    const views = document.querySelectorAll('.view-section');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetView = button.getAttribute('data-target');

            navButtons.forEach(btn => {
                btn.classList.remove('bg-white', 'text-blue-600', 'shadow');
                btn.classList.add('text-white', 'hover:bg-blue-700');
            });

            button.classList.add('bg-white', 'text-blue-600', 'shadow');
            button.classList.remove('text-white', 'hover:bg-blue-700');

            views.forEach(view => {
                if (view.id === `${targetView}-view`) {
                    view.classList.remove('hidden');
                } else {
                    view.classList.add('hidden');
                }
            });
        });
    });
}

async function loadDashboardStats() {
    try {
        const [devsRes, tasksRes] = await Promise.all([
            fetch(`${API_BASE}/developers/`),
            fetch(`${API_BASE}/tasks/`)
        ]);

        const developers = await devsRes.json();
        const tasks = await tasksRes.json();

        const openTasks = tasks.filter(t => t.status && t.status.toLowerCase() === 'open');

        document.getElementById('total-developers').innerText = developers.length || 0;
        document.getElementById('total-tasks').innerText = tasks.length || 0;
        document.getElementById('open-tasks').innerText = openTasks.length || 0;
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

async function loadDevelopersDropdown() {
    try {
        const response = await fetch(`${API_BASE}/developers/`);
        const developers = await response.json();
        const devSelect = document.getElementById('developer-select');

        if (!devSelect) return;

        devSelect.innerHTML = '<option value="">Select a developer...</option>';
        developers.forEach(dev => {
            const option = document.createElement('option');
            option.value = dev.id;
            const skillsStr = Array.isArray(dev.skills) ? dev.skills.join(', ') : dev.skills;
            option.textContent = `${dev.name} (${skillsStr})`;
            devSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading developers dropdown:', error);
    }
}

async function handleDeveloperChange() {
    const devSelect = document.getElementById('developer-select');
    const topNSelect = document.getElementById('top-n-select');
    const recommendationsContainer = document.getElementById('recommendations-list');

    if (!devSelect || !recommendationsContainer) return;

    const devId = devSelect.value;
    const topN = topNSelect ? topNSelect.value || 5 : 5;

    if (!devId) {
        recommendationsContainer.innerHTML = '<p class="text-gray-500">Please select a developer to view recommendations.</p>';
        return;
    }

    recommendationsContainer.innerHTML = '<p class="text-gray-500">Loading recommendations...</p>';

    try {
        const response = await fetch(`${API_BASE}/recommendations/developer/${devId}?top_n=${topN}`);
        const recommendations = await response.json();

        if (!recommendations || recommendations.length === 0) {
            recommendationsContainer.innerHTML = '<p class="text-gray-500">No suitable task recommendations found.</p>';
            return;
        }

        recommendationsContainer.innerHTML = '';
        recommendations.forEach(item => {
            const card = document.createElement('div');
            card.className = 'p-4 border rounded-lg bg-white shadow-sm mb-3';
            const skillsStr = Array.isArray(item.task.required_skills) 
                ? item.task.required_skills.join(', ') 
                : item.task.required_skills;

            card.innerHTML = `
                <div class="flex justify-between items-center mb-2">
                    <h3 class="font-bold text-lg text-blue-600">${item.task.title}</h3>
                    <span class="bg-blue-100 text-blue-800 text-xs px-2.5 py-0.5 rounded font-semibold">
                        Score: ${(item.recommendation_score * 100).toFixed(1)}%
                    </span>
                </div>
                <p class="text-gray-600 text-sm mb-2">${item.task.description || 'No description provided.'}</p>
                <div class="text-xs text-gray-500">
                    <strong>Required Skills:</strong> ${skillsStr}
                </div>
            `;
            recommendationsContainer.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        recommendationsContainer.innerHTML = '<p class="text-red-500">Failed to load recommendations.</p>';
    }
}

async function loadDevelopersList() {
    const listEl = document.getElementById('developers-table-body');
    if (!listEl) return;

    try {
        const response = await fetch(`${API_BASE}/developers/`);
        const developers = await response.json();
        
        listEl.innerHTML = developers.map(dev => `
            <tr class="border-b">
                <td class="p-2 font-medium">${dev.id}</td>
                <td class="p-2">${dev.name}</td>
                <td class="p-2">${Array.isArray(dev.skills) ? dev.skills.join(', ') : dev.skills}</td>
                <td class="p-2">${dev.experience_years} yrs</td>
                <td class="p-2">${dev.current_load}/${dev.max_capacity}</td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Error loading developer list', e);
    }
}

async function loadTasksList() {
    const listEl = document.getElementById('tasks-table-body');
    if (!listEl) return;

    try {
        const response = await fetch(`${API_BASE}/tasks/`);
        const tasks = await response.json();
        
        listEl.innerHTML = tasks.map(t => `
            <tr class="border-b">
                <td class="p-2 font-medium">${t.id}</td>
                <td class="p-2 font-semibold text-blue-600">${t.title}</td>
                <td class="p-2">${Array.isArray(t.required_skills) ? t.required_skills.join(', ') : t.required_skills}</td>
                <td class="p-2">${t.difficulty}</td>
                <td class="p-2">${t.estimated_hours} hrs</td>
                <td class="p-2"><span class="px-2 py-1 text-xs rounded bg-green-100 text-green-800">${t.status}</span></td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Error loading task list', e);
    }
}