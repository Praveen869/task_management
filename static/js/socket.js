const socket = io();

// UI Elements
const taskForm = document.getElementById('task-form');
const taskList = document.getElementById('task-list');

if (taskForm) {
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('task-title').value;
        const description = document.getElementById('task-desc').value;
        const priority = document.getElementById('task-priority').value;

        const status = document.getElementById('task-status').value;

        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description,
                priority,
                status
            })
        });

        if (response.ok) {
            taskForm.reset();
        }
    });
}

async function updateTaskStatus(id, status) {
    // Fetch current task data first or just send the status update
    // For simplicity, we'll assume the server can handle partial updates or we provide enough data
    // However, the current PUT /api/tasks/<id> requires all fields.
    // Let's first get the task info from UI
    const taskEl = document.getElementById(`task-${id}`);
    const title = taskEl.querySelector('h3').innerText;
    const priority = taskEl.querySelector('.badge').innerText;
    const description = taskEl.dataset.description || "";

    await fetch(`/api/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, status, priority, description })
    });
}

async function deleteTask(id) {
    if (confirm('Are you sure you want to delete this task?')) {
        await fetch(`/api/tasks/${id}`, {
            method: 'DELETE'
        });
    }
}

// Socket Events
socket.on('task_added', (task) => {
    addTaskToUI(task);
    updateStats();
});

socket.on('task_updated', (task) => {
    const taskEl = document.getElementById(`task-${task.id}`);
    if (taskEl) {
        taskEl.className = `glass-card task-item ${task.status === 'completed' ? 'completed' : ''}`;

        // Update badge and status
        const statusBadge = taskEl.querySelector('.status-badge');
        if (statusBadge) statusBadge.innerText = task.status;
        
        const priorityBadge = taskEl.querySelector('.badge');
        if (priorityBadge) {
            priorityBadge.innerText = task.priority;
            priorityBadge.className = `badge badge-${task.priority.toLowerCase()}`;
        }

        // Update button icon and action
        const toggleBtn = taskEl.querySelector('.complete');
        if (toggleBtn) {
            const isCompleted = task.status === 'completed';
            toggleBtn.innerHTML = `<i data-lucide="${isCompleted ? 'rotate-ccw' : 'check'}"></i>`;
            toggleBtn.setAttribute('onclick', `updateTaskStatus(\`${task.id}\`, \`${isCompleted ? 'pending' : 'completed'}\`)`);
        }
        
        // Re-init icons
        if (window.lucide) lucide.createIcons();
    }
    updateStats();
});

socket.on('task_deleted', (data) => {
    const taskEl = document.getElementById(`task-${data.id}`);
    if (taskEl) {
        taskEl.style.opacity = '0';
        taskEl.style.transform = 'translateY(10px)';
        setTimeout(() => {
            taskEl.remove();
            
            // Show empty state if list is empty
            const taskList = document.getElementById('task-list');
            if (taskList && taskList.querySelectorAll('.task-item:not(#empty-state)').length === 0) {
                let emptyState = document.getElementById('empty-state');
                if (!emptyState) {
                    emptyState = document.createElement('div');
                    emptyState.id = 'empty-state';
                    emptyState.className = 'glass-card task-item';
                    emptyState.style = 'justify-content: center; text-align: center; color: var(--text-muted); padding: 4rem;';
                    emptyState.innerHTML = `
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
                            <i data-lucide="clipboard-list" style="width: 48px; height: 48px; opacity: 0.2;"></i>
                            <p>You have no tasks yet. Time to be productive!</p>
                        </div>
                    `;
                    taskList.appendChild(emptyState);
                    if (window.lucide) lucide.createIcons();
                }
            }
        }, 300);
    }

    updateStats();
});

function addTaskToUI(task) {
    // Remove empty state if it exists
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const div = document.createElement('div');
    div.id = `task-${task.id}`;
    div.className = `glass-card task-item ${task.status === 'completed' ? 'completed' : ''}`;
    div.dataset.description = task.description || '';
    div.innerHTML = `
        <div class="task-content">
            <h3>${task.title}</h3>
            <p class="task-desc-text">${task.description || 'No description provided.'}</p>
            <div class="task-meta">
                <span class="badge badge-${task.priority.toLowerCase()}">${task.priority}</span>
                <span class="status-badge">${task.status}</span>
            </div>
        </div>
        <div class="task-actions">
            <button onclick="updateTaskStatus(\`${task.id}\`, \`${task.status === 'completed' ? 'pending' : 'completed'}\`)" class="btn-icon complete" title="Toggle Status">
                <i data-lucide="${task.status === 'completed' ? 'rotate-ccw' : 'check'}"></i>
            </button>
            <button onclick="deleteTask(\`${task.id}\`)" class="btn-icon delete" title="Delete Task">
                <i data-lucide="trash-2"></i>
            </button>
        </div>
    `;
    taskList.prepend(div);
    if (window.lucide) lucide.createIcons();
}

async function updateStats() {
    try {
        const response = await fetch(`/api/analytics?t=${new Date().getTime()}`);
        if (response.ok) {
            const data = await response.json();

            // Update UI elements
            const totalTasksEl = document.getElementById('stat-total');
            const completionRateEl = document.getElementById('stat-completion');
            const pendingTasksEl = document.getElementById('stat-pending');

            if (totalTasksEl) totalTasksEl.innerText = data.total_tasks;
            if (completionRateEl) completionRateEl.innerText = `${data.completion_percentage}%`;
            if (pendingTasksEl) pendingTasksEl.innerText = data.pending_tasks;

            const completedTasksEl = document.getElementById('stat-completed');
            if (completedTasksEl) completedTasksEl.innerText = data.completed_tasks;

            const inProgressEl = document.getElementById('stat-in-progress');
            if (inProgressEl) inProgressEl.innerText = data.in_progress_tasks;

            const avgTasksEl = document.getElementById('stat-avg-tasks');
            if (avgTasksEl) avgTasksEl.innerText = data.avg_tasks_per_day;

            const priorityEl = document.getElementById('stat-priority');
            if (priorityEl && data.priority_breakdown) {
                const h = data.priority_breakdown.high || 0;
                const m = data.priority_breakdown.medium || 0;
                const l = data.priority_breakdown.low || 0;
                priorityEl.innerText = `H: ${h} | M: ${m} | L: ${l}`;
            }
        }
    } catch (err) {
        console.error('Failed to update stats:', err);
    }
}
