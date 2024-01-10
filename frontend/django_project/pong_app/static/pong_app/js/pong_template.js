function createGameSessionWebSocket(sessionId) {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}/ws/game/${sessionId}/`; // Update with the correct URL pattern
    console.log("Game session WebSocket URL:", url);
    return new WebSocket(url);
}
function setupWebSocketListeners(socket) {
    socket.onopen = (event) => {
        console.log("WebSocket connection opened:", event);
        requestAnimationFrame(() => handleKeyDown(socket));
    };

    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'game_state') {
            const gameData = message.data;
            window.windowData = gameData["window"];
            window.player1Data = gameData["player1"];
            window.player2Data = gameData["player2"];
            window.ballData = gameData["ball"];
            window.pauseGame = gameData["pause"];
        }
    }

    socket.onclose = (event) => {
        console.log("WebSocket connection closed:", event);
        window.removeEventListener('keydown', handleKeyDown);
    };

    socket.onerror = (event) => {
        console.error("WebSocket error:", event);
    };
}

async function waitForWindowData() {
    while (window.windowData === null) {
        await new Promise(resolve => setTimeout(resolve, 100)); // Wait for 100ms before checking again
    }
}

export async function initGame(sessionId) {
    window.myp5 = null;
    window.player1Data = null;
    window.player2Data = null;
    window.ballData = null;
    window.pauseGame = null;
    window.windowData = null;
    window.keyState = {};

    let gameSocket = createGameSessionWebSocket(sessionId);
    setupWebSocketListeners(gameSocket);
    await waitForWindowData();
    setupPlayerMovement(gameSocket);
    drawCanvas();
}

function setupPlayerMovement(socket) {
    window.addEventListener('keydown', (event) => {
        if (!window.keyState[event.key]) {
            window.keyState[event.key] = true;
            sendMoveMessage(socket);
        }
    });

    window.addEventListener('keyup', (event) => {
        window.keyState[event.key] = false;
    });
}

function sendMoveMessage(socket) {
    if (window.keyState['ArrowUp']) {
        socket.send(JSON.stringify({ message: 'move_up_player' }));
    } else if (window.keyState['ArrowDown']) {
        socket.send(JSON.stringify({ message: 'move_down_player' }));
    }
}

function handleKeyDown(socket) {
    sendMoveMessage(socket);
    requestAnimationFrame(() => handleKeyDown(socket));
}

export function drawCanvas() {
    const s = (sketch) => {
        sketch.setup = () => {
            if (window.windowData) {
                let canvas = sketch.createCanvas(window.windowData.width, window.windowData.height);
                canvas.parent("pageContainer");
            }
        };

        sketch.draw = () => {
            if (window.windowData) {
                sketch.background(0);
                sketch.fill(255);
                sketch.rect(window.player1Data.xpos, window.player1Data.ypos, window.player1Data.width, window.player1Data.height);
                sketch.rect(window.player2Data.xpos, window.player2Data.ypos, window.player2Data.width, window.player2Data.height);
                sketch.ellipse(window.ballData.xpos, window.ballData.ypos, window.ballData.radius * 2);

                if (window.pauseGame) {
                    sketch.fill(255);
                    sketch.textSize(32);
                    sketch.textAlign(sketch.CENTER, sketch.CENTER);
                    sketch.text("Awaiting Second Player...", window.windowData.width / 2, window.windowData.height / 10);
                }
            }
        };
    };

    window.myp5 = new p5(s);
}

export function clearCanvas() {
    if (window.myp5)
        window.myp5.remove();
}
