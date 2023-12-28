const player1 = pongData.player1;
const player2 = pongData.player2;
const ball = pongData.ball;
const window_width = pongData.window.width;
const window_height = pongData.window.height

function setup() {
    createCanvas(window_width, window_height);
    // Initialize players and ball using the retrieved data
}

function draw() {
    background(0);
    // Draw players and ball
    fill(255); // White color
    rect(player1.xpos, player1.ypos, player1.width, player1.height);
    rect(player2.xpos, player2.ypos, player2.width, player2.height);
    ellipse(ball.xpos, ball.ypos, ball.radius * 2);
}

