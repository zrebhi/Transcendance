import {clearPage, getCsrfToken, loadScripts, loadView} from "./SPAContentLoader.js";

// Modify connectToQueueWebSocket to use startGameSession
function connectToQueueWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(protocol + '://' + window.location.host + '/ws/queue/');

    socket.onopen = (event) => {
        console.log("Queue WebSocket connection opened:", event);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'game_matched') {
            console.log('Game matched:', data);
            loadGame(data.session_id);
        }
    };

    socket.onclose = (event) => {
        console.log("Queue WebSocket connection closed:", event);
    };

    socket.onerror = (event) => {
        console.error("Queue WebSocket error:", event);
    };
}


export function joinQueue() {
    fetch('https://localhost/matchmaking/', {  // Update with the correct URL
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(), // Include CSRF token if needed
            'Content-Type': 'application/json'
        },
        credentials: 'include'  // Necessary for including cookies (like CSRF token)
    })
        .then(response => {
            console.log(response); // Check what the response looks like
            return response.text(); // Use text() if you're not sure it's JSON
        })
        .then(text => {
            try {
                const data = JSON.parse(text);
                console.log('Join queue response:', data);
                if (data.status === 'success') {
                    // Connect to the WebSocket for queue updates
                    connectToQueueWebSocket();
                } else {
                    // Handle error (user already in queue, not authenticated, etc.)
                    console.error('Error joining queue:', data.message);
                }
            } catch (error) {
                console.error('Error parsing JSON:', error);
            }
        })
}

let socketCreated = false;

function loadGame(sessionId) {
    clearPage();
    loadView('https://localhost/pong/')
        .then(() => loadScripts([
            'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js',
            'https://localhost/static/pong_app/js/pong_template.js',
        ], () => {
            if (!socketCreated) {
                initGame(sessionId);
                socketCreated = true;
            } else {
                drawCanvas();
            }
        }))
        .catch(error => console.error('Error:', error));
}
