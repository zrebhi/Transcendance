import {getCsrfToken, loadView, loadGame, updateNavbar} from "/main/static/main/js/SPAContentLoader.js";

export function joinTournament(event, tournamentId) {
    fetch(`/tournaments/join/${tournamentId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            tournamentWebSocketConnection(tournamentId);
            loadView(data["next_url"]).catch(error => console.error('Error:', error));
            updateNavbar();
        } else {
            console.error('Join tournament failed:', data.message);
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

export function tournamentView(event) {
    const tournamentId = event.target.getAttribute('data-tournament-id');
    loadView(`/tournaments/${tournamentId}`).catch(error => console.error('Error:', error));
}

export function tournamentWebSocketConnection(tournamentId) {
    console.log('Connecting to tournament WebSocket:', tournamentId);
    if (!tournamentId) return;

    let ws;
    window.tournamentWebSocket == null ? ws = getWebSocket() : ws = window.tournamentWebSocket;

    ws.onopen = function(event) {
        console.log('Tournament WebSocket connection opened:', event);
        window.tournamentWebSocket = ws;
    };

    ws.onmessage = async function(event) {
        console.log('Tournament WebSocket message received:', event);
        const message = JSON.parse(event.data);
        switch (message.type) {
            case 'tournament_message':
                await updateTournament(tournamentId);
                break;
            case 'game_start':
                await loadGame(message["session_id"])
                    .catch(error => console.error('Error:', error));
                break;
        }
    };

    ws.onclose = function(event) {
        console.log('Tournament WebSocket connection closed:', event);
        window.tournamentWebSocket = null;
    };

    ws.onerror = function(event) {
        console.error('Tournament WebSocket error:', event);
    };
}

function getWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsProtocol}://${window.location.host}/ws/tournaments/`;
    return new WebSocket(wsUrl);
}

function updateTournament(tournamentId) {
    console.log('Updating tournament:', tournamentId);
    const tournamentContainer = document.getElementById('tournament');
    updateNavbar();
    if (tournamentContainer) {
        loadView(`/tournaments/${tournamentId}`).catch(error => console.error('Error:', error));
    }
}

export function updateReadyState(event, ws, ready_state) {
    if (!ws || !event.target) {
        console.error("WebSocket or event target is not available.");
        return;
    }

    if (ws.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open. Current state:", ws.readyState);
        return;
    }

    try {
        const matchId = event.target.getAttribute('data-match-id');
        const message = JSON.stringify({
            type: 'ready_state_update',
            ready_state: ready_state,
            match_id: matchId
        });
        ws.send(message);
    } catch (error) {
        console.error("Failed to send message over WebSocket:", error);
    }
}

export function observeRoundTimers() {
    // Create a new MutationObserver instance to monitor DOM changes
    const observer = new MutationObserver((mutationsList, observer) => {
        // Loop through all mutations observed
        for (const mutation of mutationsList) {
            // Check for new child elements being added to the DOM
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    // Ensure the node is an element and has the 'round-timer' class or contains an element with it
                    if (node.nodeType === Node.ELEMENT_NODE && (node.classList.contains('round-timer') || node.querySelector('.round-timer'))) {
                        // Execute the roundTimers function to update the newly added timer elements
                        roundTimers();
                    }
                });
            }
        }
    });

    // Specify which mutations to observe: additions of child elements and deeper subtree modifications
    const config = { childList: true, subtree: true };

    // Begin observing the document body for specified mutations
    observer.observe(document.body, config);
}


function roundTimers() {
    console.log('Setting up round timers');
    const timerElements = document.querySelectorAll('.round-timer');
    timerElements.forEach(function(timerElement) {
        const startTime = new Date(timerElement.getAttribute('data-start-time'));
        const updateTimer = function() {
            const now = new Date();
            const timeLeft = startTime - now;
            if (timeLeft > 0) {
                const minutes = Math.floor(timeLeft / 60000);
                const seconds = ((timeLeft % 60000) / 1000).toFixed(0);
                timerElement.textContent = minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
            } else {
                timerElement.textContent = '00:00';
            }
        };
        updateTimer();
        setInterval(updateTimer, 1000);
    });
}