import {getCsrfToken, loadView, loadGame} from "/main/static/main/js/SPAContentLoader.js";

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
    if (!tournamentId) return;

    let ws;
    window.tournamentWebSocket == null ? ws = getWebSocket() : ws = window.tournamentWebSocket;

    ws.onopen = function(event) {
        console.log('WebSocket connection opened:', event);
        window.tournamentWebSocket = ws;
    };

    ws.onmessage = async function(event) {
        console.log('WebSocket message received:', event);
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
        console.log('WebSocket connection closed:', event);
        window.tournamentWebSocket = null;
    };

    ws.onerror = function(event) {
        console.error('WebSocket error:', event);
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
