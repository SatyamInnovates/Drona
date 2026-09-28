const ml_streak = document.getElementById('ml-streak');
const dsa_streak = document.getElementById('dsa-streak');


fetch('../Backend(main files)/streaks.json')
    .then(response => response.json())
    .then(data => {
        ml_streak.textContent = data.ml_streak;
        dsa_streak.textContent = data.dsa_streak;
    })




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
