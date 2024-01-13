import { updateNavbar } from "/static/main/js/SPAContentLoader.js";

// Initializes the default state of the game.
function initGameData() {
    return {
        myp5: null,
        socket: null,
        player1: null,
        player2: null,
        paddle1: null,
        paddle2: null,
        ball: null,
        status: null,
        window: null,
        gameType: null,
        winner: null,
        keyState: {},
        moveMessageCount: 0,
        lastResetTime: performance.now()
    };
}

let gameData = initGameData();

// Main entry point for starting or resuming a game session.
export async function getGame(sessionId) {
    if (!window.gameSocket) {
        await initGame(sessionId);
        updateNavbar();
    } else {
        drawCanvas();
    }
}

// Initializes a new game session.
async function initGame(sessionId) {
    gameData = initGameData();
    gameData.socket = createGameSessionWebSocket(sessionId);
    setupWebSocketListeners();
    await waitForWindowData();
    setupPlayerMovement();
    drawCanvas();
}

// Creates and returns a WebSocket connection for the game session.
function createGameSessionWebSocket(sessionId) {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}/ws/game/${sessionId}/`;
    return new WebSocket(url);
}

// Sets up WebSocket event listeners.
function setupWebSocketListeners() {
    gameData.socket.onopen = () => {
        console.log("WebSocket connection opened");
        requestAnimationFrame(createAnimationLoop());
    };
    gameData.socket.onmessage = handleWebSocketMessage;
    gameData.socket.onclose = handleWebSocketClose;
    gameData.socket.onerror = (event) => console.error("WebSocket error:", event);
}

// Sets up key event listeners for player movement.
function setupPlayerMovement() {
    window.addEventListener('keydown',
        (event) => { if (!gameData.keyState[event.key]) gameData.keyState[event.key] = true });
    window.addEventListener('keyup', (event) => gameData.keyState[event.key] = false);
}

// Animation loop for handling continuous tasks (keyhold).
// Limits movement updates per second for better compatibility across browsers.
function createAnimationLoop() {
    let lastTime = performance.now();

    function animate() {
        const currentTime = performance.now();
        const deltaTime = currentTime - lastTime;
        const timestep = 1000 / 75;

        if (deltaTime > timestep) {
            sendMoveMessage(deltaTime);
            lastTime = currentTime;
    }

    if (gameData.socket && gameData.socket.readyState === WebSocket.OPEN)
        requestAnimationFrame(animate);
}


    return animate;
}

// Sends a movement message to the server.
function sendMoveMessage() {
    let moveMessages = getMoveMessages();
    if (moveMessages.length > 0 && gameData.socket.readyState === WebSocket.OPEN) {
        moveMessages.forEach(message => {
            gameData.socket.send(JSON.stringify({ type: 'move_command', message: message }));
        });
    }
}


// Determines the movement message based on the current key state.
function getMoveMessages() {
    let messages = [];

    // Player 1 Controls
    if (gameData.keyState['z']) messages.push("move_up_player1");
    if (gameData.keyState['s']) messages.push("move_down_player1");

    // Player 2 Controls
    if (gameData.keyState['ArrowUp']) messages.push("move_up_player2");
    if (gameData.keyState['ArrowDown']) messages.push("move_down_player2");

    return messages;
}



// Handles incoming WebSocket messages.
function handleWebSocketMessage(event) {
    const message = JSON.parse(event.data);
    switch (message.type) {
        case 'game_init':
            setGameData(message.data);
            break;
        case 'game_state':
            updateGameState(message.data);
            break;
        case 'winner_message':
            gameData.winner = message.winner;
            updateNavbar();
            break;
    }
}

// Updates gameData with incoming data from the server.
function setGameData(data) {
    console.log("Initializing game data:", data);
    Object.assign(gameData, data);
    console.log("Game data:", gameData);
}

// Updates the game state based on the latest data from the server.
function updateGameState(data) {
    Object.assign(gameData, data);
}

// Waits for initial game data from the server.
async function waitForWindowData() {
    while (!gameData.window) {
        if (gameData.socket.readyState === WebSocket.OPEN) {
            gameData.socket.send(JSON.stringify({ type: "game_init_request" }));
        }
        await sleep(100);
    }
}

// Helper function for asynchronous sleep.
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Initializes and starts the p5 sketch for the game's canvas.
export function drawCanvas() {
    const s = (sketch) => {
        sketch.setup = () => setupCanvas(sketch);
        sketch.draw = () => drawGame(sketch);
    };
    gameData.myp5 = new p5(s);
    console.log(gameData.myp5);
}

// Sets up the canvas with initial configurations.
function setupCanvas(sketch) {
    if (gameData.window) {
        let canvas = sketch.createCanvas(gameData.window.width, gameData.window.height);
        canvas.parent("pageContainer");
    }
}

// Main function for drawing game elements on the canvas.
function drawGame(sketch) {
    if (gameData.window) {
        drawBackground(sketch);
        drawPaddles(sketch);
        drawBall(sketch);
        drawScores(sketch);
        drawGameStatus(sketch);
    }
}

// Draws the game background.
function drawBackground(sketch) {
    sketch.background(0);
    sketch.fill(255);
}

// Draws the paddles on the canvas.
function drawPaddles(sketch) {
    sketch.rect(gameData.paddle1['xpos'], gameData.paddle1['ypos'], gameData.paddle1.width, gameData.paddle1.height);
    sketch.rect(gameData.paddle2['xpos'], gameData.paddle2['ypos'], gameData.paddle2.width, gameData.paddle2.height);
}

// Draws the ball on the canvas.
function drawBall(sketch) {
    sketch.ellipse(gameData.ball['xpos'], gameData.ball['ypos'], gameData.ball['radius'] * 2);
}

// Displays the current scores of the players.
function drawScores(sketch) {
    sketch.textSize(24);
    sketch.textFont("Bungee Spice");
    sketch.text(`${gameData.player1}: ${gameData.paddle1['score']}`, gameData.window.width / 4, 30);
    sketch.text(`${gameData.player2}: ${gameData.paddle2['score']}`, 3 * gameData.window.width / 4, 30);
    sketch.text(`${gameData.moveCount}`, gameData.window.width / 2, 30);
}

// Draws text related to the current game status, like pause or end messages.
function drawGameStatus(sketch) {
    if (gameData.status === "paused") {
        sketch.textSize(32);
        sketch.textAlign(sketch.CENTER);
        sketch.text("Awaiting Second Player...", gameData.window.width / 2, gameData.window.height / 10);
    }
    if (gameData.winner) {
        sketch.textSize(50);
        sketch.textAlign(sketch.CENTER);
        sketch.text(`${gameData.winner} wins!`, gameData.window.width / 2, gameData.window.height / 2.5);
        // console.log(gameData.ball);
    }
}

// Clears the canvas when necessary, e.g., at the end of a game.
export function clearCanvas() {
    if (gameData.myp5) {
        gameData.myp5.remove();
    }
}

// Handles the closing event of the WebSocket connection.
function handleWebSocketClose(event) {
    window.removeEventListener('keydown', (event) => { if (!gameData.keyState[event.key]) gameData.keyState[event.key] = true });
    window.removeEventListener('keyup', (event) => { gameData.keyState[event.key] = false });
    window.gameSocket = null;
    console.log("WebSocket connection closed:", event);
}
