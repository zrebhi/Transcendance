import { gameData } from "./pong.js";
import { endGame } from "./threejs.js";
import { getLanguage } from "/static/main/js/SPAContentLoader.js";

export function clearCanvas() {
  console.log("Clearing canvas");
  if (gameData.myp5) gameData.myp5.remove();
  if (gameData.renderer) endGame();
}

export function drawCanvas() {
  const s = (sketch) => {
    sketch.setup = () => setupCanvas(sketch);
    sketch.draw = () => drawGame(sketch);
  };
  gameData.myp5 = new p5(s);
}

function setupCanvas(sketch) {
  console.log("Setting up canvas");
  if (!gameData.canvasContainerWidth || !gameData.canvasContainerHeight) {
    return;
  }
  let canvas = sketch.createCanvas(
    gameData.canvasContainerWidth,
    gameData.canvasContainerHeight
  );
  let canvasContainer = document.getElementById("canvasContainer");
  if (!canvasContainer) return;
  canvas.parent("canvasContainer");
}

export function drawGame(sketch) {
  if (gameData.window) {
    drawBackground(sketch);
    drawScores(sketch);
    drawGameStatus(sketch);
    if (!gameData.winner) {
      drawPaddles(sketch);
      drawBall(sketch);
    }
  }
}

function drawBackground(sketch) {
  sketch.background(0);
  sketch.fill(255);
}

function drawPaddles(sketch) {
  sketch.rect(
    gameData.paddle1["xpos"],
    gameData.paddle1["ypos"],
    gameData.paddle1.width,
    gameData.paddle1.height
  );
  sketch.rect(
    gameData.paddle2["xpos"],
    gameData.paddle2["ypos"],
    gameData.paddle2.width,
    gameData.paddle2.height
  );
}

function drawBall(sketch) {
  sketch.ellipse(
    gameData.ball["xpos"],
    gameData.ball["ypos"],
    gameData.ball["radius"] * 2
  );
}

// Displays the current scores of the players.
function drawScores(sketch) {
  sketch.textSize(
    getAdaptiveTextSize(gameData.myp5.width, gameData.myp5.height, 24)
  );
  sketch.textFont("Bungee Spice");
  sketch.text(
    `${gameData.player1}: ${gameData.paddle1["score"]}`,
    gameData.myp5.width / 4,
    30
  );
  sketch.text(
    `${gameData.player2}: ${gameData.paddle2["score"]}`,
    (3 * gameData.myp5.width) / 4,
    30
  );
}

// Draws text related to the current game status, like pause or end messages.
function drawGameStatus(sketch) {
  if (gameData.status === "paused") {
    sketch.textSize(
      getAdaptiveTextSize(gameData.myp5.width, gameData.myp5.height, 30)
    );
    sketch.textAlign(sketch.CENTER);
    sketch.text(
      getPauseMessage(),
      gameData.myp5.width / 2,
      gameData.myp5.height / 10
    );
  }
  if (gameData.forfeitMessage) {
    sketch.textSize(
      getAdaptiveTextSize(gameData.myp5.width, gameData.myp5.height, 30)
    );
    sketch.textAlign(sketch.CENTER);
    sketch.text(
      getForfeitMessage(),
      gameData.myp5.width / 2,
      gameData.myp5.height / 5
    );
  }
  if (gameData.winner) {
    sketch.textSize(
      getAdaptiveTextSize(gameData.myp5.width, gameData.myp5.height, 50)
    );
    sketch.textAlign(sketch.CENTER);
    sketch.text(
      getWinnerMessage(),
      gameData.myp5.width / 2,
      gameData.myp5.height / 2.5
    );
  }
}

export function getPauseMessage() {
  let player, paddle;

  if (gameData.paddle1["pause_request"] && gameData.paddle2["pause_request"])
    paddle =
      gameData.paddle1["pause_timer"] > gameData.paddle2["pause_timer"]
        ? gameData.paddle1
        : gameData.paddle2;
  else if (gameData.paddle1["pause_request"]) paddle = gameData.paddle1;
  else if (gameData.paddle2["pause_request"]) paddle = gameData.paddle2;

  player = paddle === gameData.paddle1 ? gameData.player1 : gameData.player2;
  const language = getLanguage();
  const pauseMessages = {
    en: `${player} has requested a pause. 
        Game will resume in ${paddle["pause_timer"]} seconds.`,
    es: `${player} ha solicitado una pausa. 
        El juego se reanudará en ${paddle["pause_timer"]} segundos.`,
    fr: `${player} a demandé une pause. 
        Le jeu reprendra dans ${paddle["pause_timer"]} secondes.`,
  };
  return pauseMessages[language];
}

export function getForfeitMessage() {
  console.log(gameData.forfeitMessage);
  const player = gameData.forfeitMessage.replace(" has forfeited the game", "");
  const language = getLanguage();
  const forfeitMessages = {
    en: `${player} has forfeited the game.`,
    es: `${player} ha abandonado el juego.`,
    fr: `${player} a abandonné la partie.`,
  };
  return forfeitMessages[language];
}

export function getWinnerMessage() {
  const winner = gameData.winner;
  const language = getLanguage();
  const winnerMessages = {
    en: `${winner} wins!`,
    es: `¡${winner} gana!`,
    fr: `${winner} gagne!`,
  };
  return winnerMessages[language];
}

// Function to adaptively calculate text size based on canvas size
function getAdaptiveTextSize(
  canvasWidth,
  canvasHeight,
  baselineSize,
  baselineWidth = 1200,
  baselineHeight = 900
) {
  const scaleFactor = Math.sqrt(
    (canvasWidth * canvasHeight) / (baselineWidth * baselineHeight)
  );
  return baselineSize * scaleFactor;
}

// Function to resize the p5.js canvas

export function resize3dCanvas() {
  let container = document.getElementById("canvasContainer");
  if (!container) return;

  let newWidth = container.offsetWidth;
  let newHeight = container.offsetHeight;
  console.log(`Resizing canvas to ${newWidth}x${newHeight}`);

  if (gameData.renderer) gameData.renderer.setSize(newWidth, newHeight);
}

export function resizeCanvas(sketch) {
  let container = document.getElementById("canvasContainer");
  if (!sketch || !container) return;

  let newWidth = container.offsetWidth;
  let newHeight = container.offsetHeight;
  console.log(`Resizing canvas to ${newWidth}x${newHeight}`);

  if (gameData.myp5) sketch.resizeCanvas(newWidth, newHeight);
  if (gameData.renderer) gameData.renderer.setSize(newWidth, newHeight);
}

// Event listener for window resize to adjust canvas size
window.addEventListener("resize", handleResize);

export function handleResize() {
  if (gameData.myp5) resizeCanvas(gameData.myp5);
  if (gameData.renderer) resizeCanvas();
}

// Function to resize the canvas continuously during menu transition
function resizeCanvasDuringTransition(start, duration, canvasContainer) {
  const now = performance.now();
  const elapsed = now - start;

  if (gameData.myp5)
    gameData.myp5.resizeCanvas(
      canvasContainer.offsetWidth,
      canvasContainer.offsetHeight
    );
  else if (gameData.renderer)
    gameData.renderer.setSize(
      canvasContainer.offsetWidth,
      canvasContainer.offsetHeight
    );

  if (elapsed < duration) {
    requestAnimationFrame(() =>
      resizeCanvasDuringTransition(start, duration, canvasContainer)
    );
  }
}

// Event listener for menu toggle
document.body.addEventListener("click", function (event) {
  //parentElement is used to handle clicks on the cross icon
  if (
    event.target.id === "menuToggle" ||
    event.target.parentElement.id === "menuToggle"
  ) {
    let menuToggle = document.getElementById("menuToggle");
    let menu = document.getElementById("menu");
    let canvasContainer = document.getElementById("canvasContainer");
    const transitionDuration = 300; // Duration of the menu transition in milliseconds

    menuToggle.classList.toggle("active");
    menu.classList.toggle("menu-visible");

    // Adjust canvas margin based on menu visibility
    if (menu.classList.contains("menu-visible")) {
      canvasContainer.style.marginLeft = "20%";
    } else {
      canvasContainer.style.marginLeft = "10px";
    }

    resizeCanvasDuringTransition(
      performance.now(),
      transitionDuration,
      canvasContainer
    );
  }
});
