export function showQueueUI() {
    document.getElementById('queueContainer').style.display = 'flex';
    startQueueTimer();
}

let queueTimerInterval;
function startQueueTimer() {
    let startTime = Date.now();
    let queueTimer = document.getElementById('queueTimer');
    queueTimerInterval = setInterval(function() {
        let elapsedTime = Date.now() - startTime;
        if (queueTimer)
            queueTimer.textContent = formatTime(elapsedTime);
    }, 1000);
}

function formatTime(milliseconds) {
    let totalSeconds = Math.floor(milliseconds / 1000);
    let minutes = Math.floor(totalSeconds / 60);
    let seconds = totalSeconds % 60;

    minutes = String(minutes).padStart(2, '0');
    seconds = String(seconds).padStart(2, '0');

    return `${minutes}:${seconds}`;
}

export function hideQueueUI() {
    clearInterval(queueTimerInterval);
    document.getElementById('queueContainer').style.display = 'none';
}
