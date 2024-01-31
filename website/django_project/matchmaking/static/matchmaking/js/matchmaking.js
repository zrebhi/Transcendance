import {getCsrfToken, loadGame } from "/main/static/main/js/SPAContentLoader.js";
import {showQueueUI, hideQueueUI} from "/main/static/main/js/queue.js";

let queueSocket = null;

function connectToQueueWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    queueSocket = new WebSocket(protocol + '://' + window.location.host + '/ws/queue/');

    queueSocket.onopen = (event) => {
        console.log("Queue WebSocket connection opened:", event);
    };

    queueSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'game_matched') {
            console.log('Game matched:', data);
            // Display "Match found" in the queue container
            document.getElementById('queueContent').innerHTML = '<p>Match found!</p>';

            setTimeout(function() {
                hideQueueUI();
                loadGame(data["session_id"]).catch(error => console.error('Error:', error));
            }, 3000);
        }
    };

    queueSocket.onclose = (event) => {
        console.log("Queue WebSocket connection closed:", event);
    };

    queueSocket.onerror = (event) => {
        console.error("Queue WebSocket error:", event);
    };
}

export function joinQueue() {
    fetch('/matchmaking/', {  // Update with the correct URL
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
                    showQueueUI();
                }
                else {
                    // Handle error (user already in queue, not authenticated, etc.)
                    console.error('Error joining queue:', data.message);
                    alert(data.message);
                }
            } catch (error) {
                console.error('Error parsing JSON:', error);
            }
        })
}

export function cancelQueue() {
    if (queueSocket && queueSocket.readyState === WebSocket.OPEN) {
        queueSocket.send(JSON.stringify({
            type: 'leave_message'
        }));
        console.log('Leaving queue');
        hideQueueUI();
    } else {
        console.error('WebSocket is not connected');
    }
}

export function startLocalGame() {
    fetch('/matchmaking/local_game/', {  // Update with the correct URL
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),  // Include CSRF token if needed
            'Content-Type': 'application/json'
        },
        credentials: 'include'  // Necessary for including cookies (like CSRF token)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Local game response:', data);
        if (data.status === 'success') {
            loadGame(data["session_id"]).catch(error => console.error('Error:', error));
        } else {
            // Handle error (user already in a game, etc.)
            console.error('Error starting local game:', data.message);
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
