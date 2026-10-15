const monochromeToggle = document.getElementById('monochrome-toggle');
const monochromeStorageKey = 'drona-monochrome-display';
try {
    const monochromeEnabled = localStorage.getItem(monochromeStorageKey) === 'true';
    document.documentElement.classList.toggle('monochrome', monochromeEnabled);
    monochromeToggle.setAttribute('aria-pressed', String(monochromeEnabled));
    monochromeToggle.setAttribute('aria-label', monochromeEnabled ? 'Switch to color display' : 'Switch to black and white display');
} catch {}
monochromeToggle.addEventListener('click', () => {
    const enabled = document.documentElement.classList.toggle('monochrome');
    monochromeToggle.setAttribute('aria-pressed', String(enabled));
    monochromeToggle.setAttribute('aria-label', enabled ? 'Switch to color display' : 'Switch to black and white display');
    try { localStorage.setItem(monochromeStorageKey, String(enabled)); } catch {}
});

const planForm = document.getElementById('plan-form');
const planInput = document.getElementById('plan-task-input');
const planList = document.getElementById('plan-task-list');
const planCompletion = document.getElementById('plan-completion');
const planProgressTrack = document.getElementById('plan-progress-track');
const planProgressFill = document.getElementById('plan-progress-fill');
// Use a local date key so plans roll over at local midnight with the dashboard.
const now = new Date();
const planDateKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
const planStorageKey = `drona-focus-plan-${planDateKey}`;
let focusTasks = [];
try {
    const savedTasks = JSON.parse(localStorage.getItem(planStorageKey) || '[]');
    if (Array.isArray(savedTasks)) focusTasks = savedTasks.filter(task => task && typeof task.text === 'string').map(task => ({ text: task.text, done: Boolean(task.done) }));
} catch {}

function saveFocusTasks() {
    try { localStorage.setItem(planStorageKey, JSON.stringify(focusTasks)); } catch {}
}

function renderFocusPlan() {
    planList.replaceChildren();
    if (!focusTasks.length) {
        const empty = document.createElement('li');
        empty.className = 'plan-empty';
        empty.textContent = 'Your plan is clear. Add one small win to get started.';
        planList.append(empty);
    }
    focusTasks.forEach((task, index) => {
        const item = document.createElement('li');
        item.className = `plan-task${task.done ? ' is-done' : ''}`;
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = task.done;
        checkbox.setAttribute('aria-label', `Mark ${task.text} ${task.done ? 'incomplete' : 'complete'}`);
        checkbox.addEventListener('change', () => {
            focusTasks[index].done = checkbox.checked;
            saveFocusTasks();
            renderFocusPlan();
        });
        const label = document.createElement('span');
        label.textContent = task.text;
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'plan-task-remove';
        remove.textContent = '×';
        remove.setAttribute('aria-label', `Remove ${task.text}`);
        remove.addEventListener('click', () => {
            focusTasks.splice(index, 1);
            saveFocusTasks();
            renderFocusPlan();
        });
        item.append(checkbox, label, remove);
        planList.append(item);
    });
    const complete = focusTasks.filter(task => task.done).length;
    const percent = focusTasks.length ? Math.round(complete / focusTasks.length * 100) : 0;
    planCompletion.textContent = `${complete}/${focusTasks.length}`;
    planProgressFill.style.width = `${percent}%`;
    planProgressTrack.setAttribute('aria-valuenow', String(percent));
}

planForm.addEventListener('submit', event => {
    event.preventDefault();
    const text = planInput.value.trim();
    if (!text) return;
    focusTasks.push({ text, done: false });
    saveFocusTasks();
    renderFocusPlan();
    planInput.value = '';
    planInput.focus();
});
renderFocusPlan();
