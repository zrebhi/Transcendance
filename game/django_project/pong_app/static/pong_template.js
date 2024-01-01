if (`${window.location.protocol}` === 'https:')
    wsType = 'wss';
else
    wsType = 'ws';

let url = wsType + `://${window.location.host}/ws/socket-server/`;
console.log(url);
const gameSocket = new WebSocket(url);

let windowData = null; // Initialize with default values
let player1Data;
let player2Data;
let ballData;
let initOK = 0;

let keyState = {}; // Object to track the state of keys

gameSocket.onopen = function (event) {
    console.log("WebSocket connection opened:", event);
    // Start listening for key presses
    requestAnimationFrame(handleKeyDown);

    gameSocket.send(JSON.stringify({ message: 'get_initial_data' }));
};

function sendMoveMessage() {
    // Send a message to the backend based on the current key state
    if (keyState['ArrowUp']) {
        gameSocket.send(JSON.stringify({ message: 'move_up_player' }));
    } else if (keyState['ArrowDown']) {
        gameSocket.send(JSON.stringify({ message: 'move_down_player' }));
    }
}

function handleKeyDown() {
    // Check the key state and send the move message
    sendMoveMessage();

    // Continue listening for the next frame
    requestAnimationFrame(handleKeyDown);
}

window.addEventListener('keydown', (event) => {
    if (!keyState[event.key]) {
        keyState[event.key] = true;
    }
});

gameSocket.onmessage = function (event) {
    const data = JSON.parse(event.data)
    windowData = data.window;
    player1Data = data.player1;
    player2Data = data.player2;
    ballData = data.ball;
    if (initOK === 0)
        setup();
};

gameSocket.onclose = function (event) {
    console.log("WebSocket connection closed:", event);

    // Remove event listeners when the connection is closed
    window.removeEventListener('keydown', handleKeyDown);
};

gameSocket.onerror = function (event) {
    console.error("WebSocket error:", event);
};

window.addEventListener('keydown', (event) => {
    if (!keyState[event.key]) {
        keyState[event.key] = true;
        sendMoveMessage();
    }
});

window.addEventListener('keyup', (event) => {
    keyState[event.key] = false;
});

function setup() {
    if (windowData != null) {
        createCanvas(windowData.width, windowData.height);
        initOK = 1;
    }
}

function draw() {
    if (initOK) {
        background(0);
        // Draw players and ball
        fill(255); // White color
        rect(player1Data.xpos, player1Data.ypos, player1Data.width, player1Data.height);
        rect(player2Data.xpos, player2Data.ypos, player2Data.width, player2Data.height);

        fill(255);
        ellipse(ballData.xpos, ballData.ypos, ballData.radius * 2);
    }
}
