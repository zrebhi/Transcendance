import { updateNavbar } from "/main/static/main/js/SPAContentLoader.js";
import {showUI, loadView} from "/main/static/main/js/SPAContentLoader.js";
import { drawCanvas, handleResize } from "./draw.js";

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
        mode: null,
        winner: null,
        canvasContainerWidth: null,
        canvasContainerHeight: null,
        keyState: {},
    };
}

export let gameData = initGameData();

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
    window.gameSocket = gameData.socket;
    setupWebSocketListeners();
    await waitForWindowData();
    setupPlayerMovement();
    getCanvasContainerSize();
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

// Sets up key event listeners for player movement.
function setupPlayerMovement() {
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
}

function handleKeyDown(event) {
    if (!gameData.keyState[event.key]) gameData.keyState[event.key] = true;
}

function handleKeyUp(event) {
    gameData.keyState[event.key] = false;
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

   if (gameData.mode === 'Local') {
       if (gameData.keyState['z']) messages.push("move_up_player1");
       if (gameData.keyState['s']) messages.push("move_down_player1");

       if (gameData.keyState['ArrowUp']) messages.push("move_up_player2");
       if (gameData.keyState['ArrowDown']) messages.push("move_down_player2");
   } else if (gameData.mode === 'Online') {
       if (gameData.keyState['ArrowUp']) messages.push("move_up_player");
       if (gameData.keyState['ArrowDown']) messages.push("move_down_player");
   }

    return messages;
}

// Handles incoming WebSocket messages.
function handleWebSocketMessage(event) {
    const message = JSON.parse(event.data);
    if (!gameData.window && message.type !== 'game_init') return;
    switch (message.type) {
        case 'game_init':
            setGameData(message.data);
            break;
        case 'game_state':
            updateGameState(message.data);
            break;
        case 'winner_message':
            gameData.winner = message.winner;
            break;
        case 'forfeit_notification':
            gameData.forfeitMessage = message.message;
    }
}

// Updates gameData with incoming data from the server.
function setGameData(data) {
    Object.assign(gameData, data);
}

// Updates the game state based on the latest data from the server.
function updateGameState(data) {

    const scales = getScaleFactors();

    if (data.paddle1) {
        data.paddle1.xpos *= scales.scaleX;
        data.paddle1.ypos *= scales.scaleY;
        data.paddle1.width *= scales.scaleX;
        data.paddle1.height *= scales.scaleY;
    }
    if (data.paddle2) {
        data.paddle2.xpos *= scales.scaleX;
        data.paddle2.ypos *= scales.scaleY;
        data.paddle2.width *= scales.scaleX;
        data.paddle2.height *= scales.scaleY;
    }

    if (data.ball) {
        data.ball.xpos *= scales.scaleX;
        data.ball.ypos *= scales.scaleY;
        data.ball.radius *= scales.scaleX;
    }

    Object.assign(gameData, data);
}

// Adapts the game data to the current canvas size.
function getScaleFactors() {
    if (!gameData.myp5) return { scaleX: 1, scaleY: 1 };

    const serverWidth = gameData.window.width;
    const serverHeight = gameData.window.height;

    const canvasWidth = gameData.myp5.width;
    const canvasHeight = gameData.myp5.height;

    return {
        scaleX: canvasWidth / serverWidth,
        scaleY: canvasHeight / serverHeight
    };
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


// Handles the closing event of the WebSocket connection.
function handleWebSocketClose(event) {
    console.log("WebSocket connection closed:", event);
    window.removeEventListener('keydown', handleKeyDown);
    window.removeEventListener('keyup', handleKeyUp);
    // window.removeEventListener('resize', handleResize);
    window.gameSocket = null;
    showUI();
    updateNavbar();
    hideMenu();

    if (gameData.myp5)
        gameData.myp5.noLoop();
}

function hideMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const menu = document.getElementById('menu');

    if (menuToggle)
        menuToggle.classList.add('d-none');

    if (menu)
        menu.classList.add('d-none');

    let canvasContainer = document.getElementById('canvasContainer');
    if (canvasContainer) {
        setTimeout(() => {
            console.log(canvasContainer.offsetWidth)
            gameData.myp5.resizeCanvas(0, 0);
            console.log(canvasContainer.offsetWidth)
            canvasContainer.style.marginLeft = '10px'; // Reset margin left
            gameData.myp5.resizeCanvas(canvasContainer.offsetWidth, canvasContainer.offsetHeight);
        }, 0);
    }
}

// Gets the size of the canvas container. Used for scaling the canvas.
function getCanvasContainerSize() {
    showMenu();
    gameData.canvasContainerWidth = document.getElementById('canvasContainer').offsetWidth;
    gameData.canvasContainerHeight = document.getElementById('canvasContainer').offsetHeight;
}

// Shows the menu if it was hidden after a game session.
export function showMenu() {
    document.getElementById('menuToggle').classList.remove('d-none');
    document.getElementById('menu').classList.remove('d-none');
}

// For online games. Sends a forfeit message to the server.
export function forfeitGame() {
    if (gameData.socket && gameData.socket.readyState === WebSocket.OPEN) {
        gameData.socket.send(JSON.stringify({
            type: 'forfeit_message'
        }));
        console.log('Forfeiting game');
    }
}

// For local games. Sends a quit message to the server.
export function quitGame() {
    if (gameData.socket && gameData.socket.readyState === WebSocket.OPEN) {
        gameData.socket.send(JSON.stringify({
            type: 'quit_message'
        }));
        console.log('Quitting game');
    }
    loadView('/home/').catch(error => console.error('Error:', error))
}
