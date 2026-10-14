const ml_streak = document.getElementById('ml-streak');
const dsa_streak = document.getElementById('dsa-streak');
const selectedCategoryCard = document.getElementById('selected-category-card');
const selectedCategoryLabel = document.getElementById('selected-category-label');
const selectedCategoryValue = document.getElementById('selected-category-value');
const yesterday = new Date();


yesterday.setDate(yesterday.getDate() - 1);
const localIsoDate = value => `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;


function calculateStreak(commits, category) {
    const dates = new Set(commits
        .filter(commit => commit.category?.trim().toLowerCase() === category.trim().toLowerCase())
        .map(commit => commit.date));
    const current = new Date();
    let day = dates.has(localIsoDate(current)) ? current : new Date(current.getFullYear(), current.getMonth(), current.getDate() - 1);
    let streak = 0;
    while (dates.has(localIsoDate(day))) {
        streak += 1;
        day.setDate(day.getDate() - 1);
    }
    return streak;
}

Promise.all([
    fetch('../Database/data.json?day=' + localIsoDate(new Date()), { cache: 'no-store' }).then(response => {
        if (!response.ok) throw new Error('Could not load activity data');
        return response.json();
    }),
    fetch('../Database/streaks.json?day=' + localIsoDate(new Date()), { cache: 'no-store' }).then(response => {
        if (!response.ok) throw new Error('Could not load streak settings');
        return response.json();
    }).catch(() => ({}))
])
    .then(([commits, settings]) => {
        ml_streak.textContent = calculateStreak(commits, 'Machine learning');
        dsa_streak.textContent = calculateStreak(commits, 'DSA');
        const selectedCategory = settings.selected_category;
        const builtInCategories = ['dsa', 'machine learning'];
        if (selectedCategory && !builtInCategories.includes(selectedCategory.trim().toLowerCase())) {
            selectedCategoryLabel.textContent = selectedCategory;
            selectedCategoryValue.textContent = calculateStreak(commits, selectedCategory);
            selectedCategoryCard.hidden = false;
        }
    })
    .catch(() => {
        ml_streak.textContent = '—';
        dsa_streak.textContent = '—';
    });

const todayTopics = document.getElementById('today-topics');
const topicCount = document.getElementById('topic-count');
const recapButton = document.getElementById('generate-recap');
const recapOutput = document.getElementById('recap-output');
let todayItems = [];

const githubPushButton = document.getElementById('github-push');
const githubPushStatus = document.getElementById('github-push-status');
const githubPushCategory = document.getElementById('github-push-category');
const githubPushCustomCategory = document.getElementById('github-push-custom-category');
githubPushCategory.addEventListener('change', () => {
    const wantsCustom = githubPushCategory.value === 'custom';
    githubPushCustomCategory.hidden = !wantsCustom;
    if (wantsCustom) githubPushCustomCategory.focus();
});
githubPushButton.addEventListener('click', async () => {
    const category = githubPushCategory.value === 'custom'
        ? githubPushCustomCategory.value.trim()
        : githubPushCategory.value;
    if (!category) {
        githubPushStatus.textContent = 'Enter a category before pushing.';
        githubPushStatus.classList.add('recap-error');
        githubPushCustomCategory.focus();
        return;
    }
    githubPushButton.disabled = true;
    githubPushStatus.classList.remove('recap-error');
    githubPushStatus.textContent = 'Running the tracker and pushing changes…';
    try {
        const response = await fetch('/api/github-push', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not push to GitHub.');
        githubPushStatus.textContent = data.message;
    } catch (error) {
        githubPushStatus.textContent = error.message || 'Could not push to GitHub. Please try again.';
        githubPushStatus.classList.add('recap-error');
    } finally {
        githubPushButton.disabled = false;
    }
});

async function generateRecap(topics, focusTime) {
    const response = await fetch('/api/recap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topics, focusTime, day: todayIso })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not generate recap.');
    return data.recap;
}

recapButton.addEventListener('click', async () => {
    console.log('Generate recap button clicked');
    recapButton.disabled = true;
    recapOutput.textContent = 'Generating your recap…';
    recapOutput.classList.remove('recap-error');
    try {
        const recap = await generateRecap(todayItems, totalDisplay.textContent);
        recapOutput.textContent = recap;
    } catch (error) {
        console.error('Recap request failed:', error);
        recapOutput.textContent = error.message || 'Could not generate your recap. Please try again.';
        recapOutput.classList.add('recap-error');
    } finally {
        recapButton.disabled = false;
    }
    console.log(recapOutput.textContent);
});


function renderTopicList(list, topics, emptyMessage) {
    list.replaceChildren();
    if (!topics.length) {
        const empty = document.createElement('li');
        empty.className = 'topic-empty';
        empty.textContent = emptyMessage;
        list.append(empty);
        return;
    }
    topics.forEach(data => {
        const item = document.createElement('li');
        item.className = 'topic-item';
        const name = document.createElement('span');
        name.className = 'topic-name';
        name.textContent = data.topic;
        const category = document.createElement('span');
        category.className = 'topic-category';
        category.textContent = data.category;
        item.append(name, category);
        list.append(item);
    });
}

const todayIso = localIsoDate(new Date());
const yesterdayIso = localIsoDate(yesterday);
const weeklyChart = document.getElementById('weekly-chart');
const weeklyGoalInput = document.getElementById('weekly-goal-hours');
const weeklyGoalStorageKey = 'drona-weekly-focus-goal-hours';
let weeklyDays = [];
let weeklyTopics = [];
let weeklySessionsAvailable = false;
let weeklyCodingAvailable = false;
try {
    const savedGoal = Number(localStorage.getItem(weeklyGoalStorageKey));
    if (Number.isFinite(savedGoal) && savedGoal >= 1 && savedGoal <= 168) weeklyGoalInput.value = String(savedGoal);
} catch {}

function renderWeeklyProgress() {
    if (!weeklyDays.length) return;
    const goalHours = Math.min(168, Math.max(1, Number(weeklyGoalInput.value) || 5));
    weeklyGoalInput.value = String(goalHours);
    const todayDay = weeklyDays.find(day => day.iso === localIsoDate(new Date()));
    const todayFocus = todayDay && todayDay.iso === localIsoDate(new Date())
        ? sessions.reduce((sum, ms) => sum + ms, 0) + (isRunning ? Date.now() - segmentStart : 0)
        : 0;
    const totalFocusMs = weeklyDays.reduce((sum, day) => sum + (day.iso === localIsoDate(new Date()) ? todayFocus : day.focusMs), 0);
    const totalCodingMs = weeklyDays.reduce((sum, day) => sum + day.codingMs, 0);
    const topicNames = new Set(weeklyTopics.map(topic => String(topic.topic || '').trim()).filter(Boolean));
    const studiedDays = new Set([
        ...weeklyDays.filter(day => day.focusMs > 0 || day.codingMs > 0 || (day.iso === todayDay?.iso && todayFocus > 0)).map(day => day.iso),
        ...weeklyTopics.map(topic => topic.date)
    ]);
    document.getElementById('weekly-focus-total').textContent = weeklySessionsAvailable ? formatTime(totalFocusMs) : 'Unavailable';
    document.getElementById('weekly-coding-total').textContent = weeklyCodingAvailable ? formatTime(totalCodingMs) : 'Unavailable';
    document.getElementById('weekly-study-days').textContent = weeklySessionsAvailable || weeklyCodingAvailable ? `${studiedDays.size} / 7` : '—';
    document.getElementById('weekly-topic-total').textContent = String(topicNames.size);
    const progress = totalFocusMs / (goalHours * 60 * 60 * 1000);
    const percent = Math.round(progress * 100);
    document.getElementById('weekly-goal-label').textContent = `${formatTime(totalFocusMs)} of ${goalHours} ${goalHours === 1 ? 'hour' : 'hours'}`;
    document.getElementById('weekly-goal-percent').textContent = `${percent}%`;
    const goalTrack = document.getElementById('weekly-goal-track');
    goalTrack.setAttribute('aria-valuemax', String(goalHours));
    goalTrack.setAttribute('aria-valuenow', String(Math.min(goalHours, totalFocusMs / 3600000).toFixed(2)));
    document.getElementById('weekly-goal-fill').style.width = `${Math.min(100, progress * 100)}%`;

    const maxFocus = Math.max(1, ...weeklyDays.map(day => day.focusMs), ...weeklyDays.map(day => day.codingMs), todayFocus);
    weeklyChart.replaceChildren();
    weeklyDays.forEach(day => {
        const focusMs = day.iso === todayDay?.iso ? todayFocus : day.focusMs;
        const codingMs = day.codingMs;
        const column = document.createElement('div');
        column.className = `weekly-day${day.iso === todayDay?.iso ? ' is-today' : ''}${codingMs > 0 ? ' has-activity' : ''}`;
        column.title = `${day.date.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}: manual focus ${formatTime(focusMs)}, coding ${formatTime(codingMs)}`;
        const area = document.createElement('div');
        area.className = 'weekly-bar-area';
        const focusBar = document.createElement('span');
        focusBar.className = 'weekly-bar focus-bar';
        focusBar.style.setProperty('--bar-height', `${focusMs ? Math.max(5, focusMs / maxFocus * 100) : 0}%`);
        const codingBar = document.createElement('span');
        codingBar.className = 'weekly-bar coding-bar';
        codingBar.style.setProperty('--bar-height', `${codingMs ? Math.max(5, codingMs / maxFocus * 100) : 0}%`);
        area.append(focusBar, codingBar);
        const label = document.createElement('span');
        label.className = 'weekly-day-label';
        label.textContent = day.date.toLocaleDateString(undefined, { weekday: 'short' });
        const time = document.createElement('span');
        time.className = 'weekly-day-time';
        time.textContent = `${formatShortTime(focusMs)}|${formatShortTime(codingMs)}`;
        column.append(area, label, time);
        weeklyChart.append(column);
    });
}

function formatShortTime(ms) {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor(ms / 60000) % 60;
    if (hours) return `${hours}h${minutes ? ` ${minutes}m` : ''}`;
    return `${minutes}m`;
}

weeklyGoalInput.addEventListener('change', () => {
    const goal = Math.min(168, Math.max(1, Number(weeklyGoalInput.value) || 5));
    weeklyGoalInput.value = String(goal);
    try { localStorage.setItem(weeklyGoalStorageKey, String(goal)); } catch {}
    renderWeeklyProgress();
});

const weekStart = new Date();
weekStart.setHours(0, 0, 0, 0);
weekStart.setDate(weekStart.getDate() - ((weekStart.getDay() + 6) % 7));
weeklyDays = Array.from({ length: 7 }, (_, index) => {
    const day = new Date(weekStart);
    day.setDate(weekStart.getDate() + index);
    return { date: day, iso: localIsoDate(day), focusMs: 0, codingMs: 0 };
});

async function loadWeeklyProgress() {
    const [sessionResult, codingResult, topicResult] = await Promise.allSettled([
        Promise.all(weeklyDays.map(async day => {
            const response = await fetch('/api/focus-sessions?day=' + encodeURIComponent(day.iso), { cache: 'no-store' });
            if (!response.ok) throw new Error('Could not load weekly focus sessions');
            const data = await response.json();
            day.focusMs = Array.isArray(data.sessions) ? data.sessions.reduce((sum, ms) => sum + (Number(ms) || 0), 0) : 0;
        })),
        Promise.all(weeklyDays.map(async day => {
            const response = await fetch('/api/coding-activity?day=' + encodeURIComponent(day.iso), { cache: 'no-store' });
            if (!response.ok) throw new Error('Could not load weekly coding activity');
            const data = await response.json();
            day.codingMs = Number(data.total_ms) || 0;
        })),
        fetch('../Database/data.json?day=' + todayIso, { cache: 'no-store' }).then(response => {
            if (!response.ok) throw new Error('Could not load weekly topics');
            return response.json();
        })
    ]);
    weeklySessionsAvailable = sessionResult.status === 'fulfilled';
    weeklyCodingAvailable = codingResult.status === 'fulfilled';
    if (topicResult.status === 'fulfilled') {
        const weekDates = new Set(weeklyDays.map(day => day.iso));
        weeklyTopics = topicResult.value.filter(commit => weekDates.has(commit.date));
    }
    renderWeeklyProgress();
}

void loadWeeklyProgress();
setInterval(() => { void loadWeeklyProgress(); }, 30_000);

const historyToggle = document.getElementById('history-toggle');
const historyDrawer = document.getElementById('yesterday-topics-drawer');
const yesterdayTopicsList = document.getElementById('yesterday-topics-list');
const yesterdayTopicDate = document.getElementById('drawer-date');
yesterdayTopicDate.textContent = yesterday.toLocaleDateString(undefined, {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

function setleHistoryOpen(isOpen){
    historyDrawer.classList.toggle('is-open', isOpen);
    historyDrawer.setAttribute('aria-hidden', String(!isOpen));
    historyToggle.setAttribute('aria-expanded', String(isOpen));
}

historyToggle.addEventListener('click', () => setleHistoryOpen(true));
document.getElementById('drawer-close').addEventListener('click',() => setleHistoryOpen(false));
document.addEventListener('keydown', event => {
    if(event.key === "Escape"){
        setleHistoryOpen(false);}
})



// let's rewrite this code
fetch('../Database/data.json?day=' + todayIso, { cache: 'no-store' })
    .then(response => {
        if (!response.ok) throw new Error("Could not fetch today's or yesterday's topics");
        return response.json();
    })
    .then(commits => {
        todayItems = commits.filter(commit => commit.date === todayIso);
        const yesterdayItems = commits.filter(commit => commit.date === yesterdayIso);
        topicCount.textContent = todayItems.length;
        renderTopicList(todayTopics, todayItems, "There aren't any topics recorded today.");
        renderTopicList(yesterdayTopicsList, yesterdayItems, "There aren't any topics recorded yesterday.");
    })
    .catch(() => {
        topicCount.textContent = '—';
        renderTopicList(todayTopics,[],'Today topics are not available');
        renderTopicList(yesterdayTopicsList,[],'Today topics are not available');
    }
)
// Reload at local midnight so the date labels and day-specific data roll over.
const tomorrow = new Date();
tomorrow.setHours(24, 0, 1, 0);
setTimeout(() => window.location.reload(), tomorrow.getTime() - Date.now());

// Yesterday's focus time is stored by the existing daily timer key.
document.getElementById('yesterday-date').textContent = yesterday.toLocaleDateString(undefined, {
    weekday: 'short', month: 'short', day: 'numeric'
});
const yesterdayKey = 'sessions-' + yesterday.toDateString();
let yesterdaySessions = [];
try {
    yesterdaySessions = JSON.parse(localStorage.getItem(yesterdayKey) || '[]');
    if (!Array.isArray(yesterdaySessions)) yesterdaySessions = [];
} catch {
    yesterdaySessions = [];
}
const yesterdayMs = yesterdaySessions.reduce((sum, duration) => sum + (Number(duration) || 0), 0);
document.getElementById('yesterday-hours').textContent = formatTime(yesterdayMs);

const yesterdayFiles = document.getElementById('yesterday-files');
const yesterdayFileCount = document.getElementById('yesterday-file-count');
fetch('../Database/yesterday_files.json?day=' + localIsoDate(yesterday), { cache: 'no-store' })
    .then(response => {
        if (!response.ok) throw new Error('Could not load yesterday’s GitHub files');
        return response.json();
    })
    .then(files => {
        yesterdayFiles.replaceChildren();
        yesterdayFileCount.textContent = `${files.length} ${files.length === 1 ? 'file' : 'files'}`;
        if (!files.length) {
            const empty = document.createElement('li');
            empty.className = 'topic-empty';
            empty.textContent = 'No files were committed yesterday.';
            yesterdayFiles.append(empty);
            return;
        }
        files.forEach(path => {
            const item = document.createElement('li');
            item.className = 'file-item';
            item.textContent = path;
            item.title = path;
            yesterdayFiles.append(item);
        });
    })
    .catch(() => {
        yesterdayFiles.replaceChildren();
        yesterdayFileCount.textContent = 'Unavailable';
        const error = document.createElement('li');
        error.className = 'topic-empty';
        error.textContent = 'Run the tracker to refresh yesterday’s GitHub activity.';
        yesterdayFiles.append(error);
    });



// Timer 
const display = document.getElementById('display');
const totalDisplay = document.getElementById('total');
let timer = null;
let startTime = 0;
let elapsetTime = 0;
let isRunning = false;
let segmentStart = 0;
let serverSessionsLoaded = false;

const storageKey = "sessions-" + new Date().toDateString();
const activeSessionKey = storageKey + "-active";
let sessions = [];
try {
    const savedSessions = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (Array.isArray(savedSessions)) sessions = savedSessions.map(Number).filter(Number.isFinite);
} catch {
    sessions = [];
}
let recoveredActiveMs = 0;

// Keep the start time separately so a browser closed during a running session
// can recover that time the next time the dashboard opens.
try {
    const savedStart = Number(localStorage.getItem(activeSessionKey));
    if (Number.isFinite(savedStart) && savedStart > 0) {
        recoveredActiveMs = Math.max(0, Date.now() - savedStart);
        localStorage.removeItem(activeSessionKey);
        localStorage.setItem(storageKey, JSON.stringify(sessions));
    }
} catch {
    // The timer remains usable when browser storage is unavailable.
}

function formatTime(ms){
    let hours = Math.floor(ms / (1000 * 60 * 60)).toString().padStart(2,"0");
    let minutes = Math.floor(ms / (1000 * 60) % 60).toString().padStart(2,"0");
    let seconds = Math.floor(ms / 1000 % 60).toString().padStart(2,"0");
    return `${hours}:${minutes}:${seconds}`;
}

function start(){
    if(!isRunning){
        startTime = Date.now() - elapsetTime;
        segmentStart = Date.now();
        try { localStorage.setItem(activeSessionKey, String(segmentStart)); } catch {}
        timer = setInterval(update,10);
        isRunning = true;
    }
}

async function syncSessions() {
    try {
        const localSessions = sessions;
        const response = await fetch('/api/focus-sessions?day=' + encodeURIComponent(localIsoDate(new Date())), { cache: 'no-store' });
        if (!response.ok) throw new Error('Server storage is unavailable');
        const data = await response.json();
        if (!Array.isArray(data.sessions)) throw new Error('Invalid server session data');
        const serverSavedSessions = data.sessions.map(Number).filter(value => Number.isFinite(value) && value >= 0);
        sessions = serverSavedSessions.length ? serverSavedSessions : localSessions;
        serverSessionsLoaded = true;
        if (recoveredActiveMs > 0) {
            sessions.push(recoveredActiveMs);
            recoveredActiveMs = 0;
            await saveSessionsToServer();
        } else {
            localStorage.setItem(storageKey, JSON.stringify(sessions));
            if (!serverSavedSessions.length && sessions.length) await saveSessionsToServer();
        }
        showTotal();
        renderWeeklyProgress();
    } catch {
        if (recoveredActiveMs > 0) {
            sessions.push(recoveredActiveMs);
            recoveredActiveMs = 0;
            try { localStorage.setItem(storageKey, JSON.stringify(sessions)); } catch {}
        }
        showTotal();
    }
}

async function saveSessionsToServer() {
    if (!serverSessionsLoaded) return;
    try {
        await fetch('/api/focus-sessions', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ day: localIsoDate(new Date()), sessions })
        });
    } catch {}
}

function stop(){
    if(isRunning){
        clearInterval(timer);
        elapsetTime = Date.now() - startTime;
        sessions.push(Date.now() - segmentStart);
        try {
            localStorage.setItem(storageKey, JSON.stringify(sessions));
            localStorage.removeItem(activeSessionKey);
        } catch {}
        isRunning = false;
        saveSessionsToServer();
        showTotal();
        renderWeeklyProgress();
    }
}

function reset(){
    clearInterval(timer);
    startTime = 0;
    elapsetTime = 0;
    isRunning = false;
    segmentStart = 0;
    sessions = [];
    try {
        localStorage.removeItem(storageKey);
        localStorage.removeItem(activeSessionKey);
    } catch {}
    saveSessionsToServer();
    display.textContent = "00:00:00";
    showTotal();
    renderWeeklyProgress();
}

function update(){
    elapsetTime = Date.now() - startTime;
    display.textContent = formatTime(elapsetTime);
    showTotal();
    renderWeeklyProgress();
}

function showTotal(){
    const completed = sessions.reduce((sum, ms) => sum + ms, 0);
    const total = completed + (isRunning ? Date.now() - segmentStart : 0);
    totalDisplay.textContent = formatTime(total);
}

showTotal();
syncSessions();


