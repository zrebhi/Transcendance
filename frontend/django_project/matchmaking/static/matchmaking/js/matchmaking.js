import {getCsrfToken, loadGame, loadView} from "/static/main/js/SPAContentLoader.js";
import {showQueueUI, hideQueueUI} from "/static/main/js/queue.js";

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
        document.getElementById('queueContainer').innerHTML = '<p>Match found!</p>';

        setTimeout(function() {
            hideQueueUI();
            loadGame(data["session_id"]);
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
            if (response.status === 401) {
               loadView('https://localhost/users/login/')
                        .catch(error => console.error('Error:', error));
            }
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