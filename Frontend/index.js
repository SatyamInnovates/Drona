const ml_streak = document.getElementById('ml-streak');
const dsa_streak = document.getElementById('dsa-streak');

fetch('../Backend(main files)/streaks.json')
    .then(response => response.json())
    .then(data => {
        ml_streak.textContent = data.ml_streak;
        dsa_streak.textContent = data.dsa_streak;
    })