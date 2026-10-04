const ml_streak = document.getElementById('ml-streak');
const dsa_streak = document.getElementById('dsa-streak');
const selectedCategoryCard = document.getElementById('selected-category-card');
const selectedCategoryLabel = document.getElementById('selected-category-label');
const selectedCategoryValue = document.getElementById('selected-category-value');
const yesterday = new Date();


yesterday.setDate(yesterday.getDate() - 1);
const localIsoDate = value => `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;


fetch('../Database/streaks.json')
    .then(response => response.json())
    .then(data => {
        ml_streak.textContent = data.ml_streak;
        dsa_streak.textContent = data.dsa_streak;
        const selectedCategory = data.selected_category;
        const builtInCategories = ['dsa', 'machine learning'];
        if (selectedCategory && !builtInCategories.includes(selectedCategory.trim().toLowerCase())) {
            selectedCategoryLabel.textContent = selectedCategory;
            selectedCategoryValue.textContent = data.selected_category_streak;
            selectedCategoryCard.hidden = false;
        }
    })
    .catch(() => {
        ml_streak.textContent = '0';
        dsa_streak.textContent = '0';
    });

const todayTopics = document.getElementById('today-topics');
const topicCount = document.getElementById('topic-count');
const recapButton = document.getElementById('generate-recap');
const recapOutput = document.getElementById('recap-output');
let todayItems = [];

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
}

function update(){
    elapsetTime = Date.now() - startTime;
    display.textContent = formatTime(elapsetTime);
    showTotal();
}

function showTotal(){
    const completed = sessions.reduce((sum, ms) => sum + ms, 0);
    const total = completed + (isRunning ? Date.now() - segmentStart : 0);
    totalDisplay.textContent = formatTime(total);
}

showTotal();
syncSessions();


