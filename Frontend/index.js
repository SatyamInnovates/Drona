const ml_streak = document.getElementById('ml-streak');
const dsa_streak = document.getElementById('dsa-streak');
const selectedCategoryCard = document.getElementById('selected-category-card');
const selectedCategoryLabel = document.getElementById('selected-category-label');
const selectedCategoryValue = document.getElementById('selected-category-value');


fetch('../Backend(main files)/streaks.json')
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

const todayTopics = document.getElementById('today-topics');
const topicCount = document.getElementById('topic-count');

fetch('../Backend(main files)/today_topics.json')
    .then(response => {
        if (!response.ok) throw new Error('Could not load today\'s topics');
        return response.json();
    })
    .then(topics => {
        todayTopics.replaceChildren();
        topicCount.textContent = topics.length;

        if (topics.length === 0) {
            const empty = document.createElement('li');
            empty.className = 'topic-empty';
            empty.textContent = "There aren't any topics recorded today.";
            todayTopics.append(empty);
            return;
        }

        topics.forEach(data => {
            const item = document.createElement('li');
            item.className = 'topic-item';


            const topic = document.createElement('span');
            topic.className = 'topic-name';
            topic.textContent = data.topic;

            const category = document.createElement('span');
            category.className = 'topic-category';
            category.textContent = data.category;

            
            
            item.append(topic, category);
            todayTopics.append(item);
        });
    })
    .catch(() => {
        todayTopics.replaceChildren();
        topicCount.textContent = '—';

        const error = document.createElement('li');
        error.className = 'topic-empty';
        error.textContent = 'Today’s topics are unavailable.';
        todayTopics.append(error);
    });

// Yesterday's focus time is stored by the existing daily timer key.
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
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
fetch('../Backend(main files)/yesterday_files.json')
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

const storageKey = "sessions-" + new Date().toDateString();   // NEW: one box per day
let sessions = JSON.parse(localStorage.getItem(storageKey)) || [];   // NEW: load (null -> [])

function formatTime(ms){
    let hours = Math.floor(ms / (1000 * 60 * 60)).toString().padStart(2,"0");
    let minutes = Math.floor(ms / (1000 * 60) % 60).toString().padStart(2,"0");
    let seconds = Math.floor(ms / 1000 % 60).toString().padStart(2,"0");
    let milliseconds = Math.floor(ms % 1000 / 10).toString().padStart(2,"0");
    
    return `${hours}:${minutes}:${seconds}`;
}

function start(){
    if(!isRunning){
        startTime = Date.now() - elapsetTime;
        segmentStart = Date.now();
        timer = setInterval(update,10);
        isRunning = true;
    }
}

function stop(){
    if(isRunning){
        clearInterval(timer);
        elapsetTime = Date.now() - startTime;
        sessions.push(Date.now() - segmentStart);
        localStorage.setItem(storageKey, JSON.stringify(sessions));   // NEW: save
        showTotal();
        isRunning = false;
    }
}

function reset(){
    clearInterval(timer);
    startTime = 0;
    elapsetTime = 0;
    isRunning = false;
    display.textContent = "00:00:00:00";
}

function update(){
    elapsetTime = Date.now() - startTime;
    display.textContent = formatTime(elapsetTime);
}

function showTotal(){
    const total = sessions.reduce((sum, ms) => sum + ms, 0);
    totalDisplay.textContent = formatTime(total);
}

showTotal();   
