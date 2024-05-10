import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.121.1/build/three.module.js";
import {
  getForfeitMessage,
  getPauseMessage,
  getWinnerMessage,
  resize3dCanvas,
} from "./draw.js";
import { gameData } from "./pong.js";

let scene,
  camera,
  ball,
  ballLight,
  paddle1,
  paddle2,
  ground,
  contour,
  middle,
  edges1,
  edges2;

export function setupCanvas() {
  if (!gameData.renderer) {
    const canvas = document.createElement("canvas");
    const canvasContainer = document.getElementById("canvasContainer");

    // Initialize camera
    camera = new THREE.PerspectiveCamera(
      80,
      gameData.canvasContainerWidth / gameData.canvasContainerHeight,
      1,
      10000
    );

    let outerWidth = window.outerWidth;

    let z = 650;
    let y = 900;

    if (outerWidth < 350) {
      z = 3000;
      y = 1600;
    }

    if (outerWidth < 400) {
      z = 2000;
      y = 1300;
    }

    if (outerWidth < 800) {
      z = 1500;
      y = 1000;
    }

    camera.position.set(600, y, z);
    camera.scale.y = -1;
    camera.rotation.set(-0.4, 0, 0);

    // Update canvas size based on container size
    if (!gameData.scoreDisplay) {
      gameData.scoreDisplay = document.createElement("div");
      gameData.scoreDisplay.id = "scoreDisplay";
      gameData.scoreDisplay.textContent = `${gameData.player1} : ${gameData.paddle1.score} - ${gameData.player2} : ${gameData.paddle2.score}`;

      if (canvasContainer) {
        canvasContainer.appendChild(gameData.scoreDisplay);
      }
    }

    if (canvasContainer) {
      canvasContainer.appendChild(canvas);
      scene = new THREE.Scene();

      gameData.renderer = new THREE.WebGLRenderer({ canvas });
      gameData.renderer.setPixelRatio(window.devicePixelRatio); // Consider device pixel ratio
      gameData.renderer.setSize(
        canvasContainer.offsetWidth,
        canvasContainer.offsetHeight
      );
      gameData.renderer.setClearColor(0x000000, 0);
      gameData.renderer.antialias = true;

      addElementsToScene();
    }
  }
}

function addElementsToScene() {
  addGround();
  addPaddles();
  addBall();
  addLights();
  addContour();
}

function addPaddles() {
  const paddleGeometry = new THREE.BoxGeometry(20, 90, 20);
  const paddleMaterial = new THREE.MeshStandardMaterial({ color: 0xffacffac });
  paddle1 = new THREE.Mesh(paddleGeometry, paddleMaterial);
  paddle2 = new THREE.Mesh(paddleGeometry, paddleMaterial);

  // Set paddle positions
  paddle1.position.set(gameData.paddle1.xpos, gameData.paddle1.ypos + 40, 10);
  paddle2.position.set(gameData.paddle2.xpos, gameData.paddle2.ypos + 40, 10);

  // Add paddles to the scene
  scene.add(paddle1, paddle2);

  // Edge geometry and material
  const edgeGeometry = new THREE.EdgesGeometry(paddleGeometry);
  const edgeMaterial = new THREE.LineBasicMaterial({
    color: 0xffffff,
    linewidth: 2,
  });

  // Create edge meshes
  edges1 = new THREE.LineSegments(edgeGeometry, edgeMaterial);
  edges2 = new THREE.LineSegments(edgeGeometry, edgeMaterial);

  // Align edges with the paddles
  edges1.position.copy(paddle1.position);
  edges2.position.copy(paddle2.position);

  // Add edges to the scene
  scene.add(edges1, edges2);
}
function addBall() {
  const ballGeometry = new THREE.SphereGeometry(10, 32, 32);
  const ballMaterial = new THREE.MeshStandardMaterial({
    color: 0xffff,
  });
  ball = new THREE.Mesh(ballGeometry, ballMaterial);

  ball.castShadow = true;
  ball.receiveShadow = true;
  scene.add(ball);

  ballLight = new THREE.PointLight(0xfcafff, 5, 0);
  ballLight.castShadow = true;
  scene.add(ballLight);
}

function addLights() {
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);
}

function addGround() {
  const groundGeometry = new THREE.BoxGeometry(1200, 900, 3);
  const groundMaterial = new THREE.MeshStandardMaterial({
    color: 0x4c3d,
  });
  ground = new THREE.Mesh(groundGeometry, groundMaterial);
  ground.position.set(600, 450, -5);

  scene.add(ground);
}

function addContour() {
  const contourGeometry = new THREE.BoxGeometry(1210, 920, 1);
  const contourMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
  contour = new THREE.Mesh(contourGeometry, contourMaterial);
  contour.position.set(600, 450, -7);

  const middleGeometry = new THREE.BoxGeometry(10, 910, 1);
  const middleMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
  middle = new THREE.Mesh(middleGeometry, middleMaterial);
  middle.position.set(600, 450, -4);

  scene.add(middle);
  scene.add(contour);
}

function handlePauseMessage() {
  gameData.scoreDisplay.textContent = `${getPauseMessage()}`;
}

export function draw3dCanvas() {
  setupCanvas();
  (function animate() {
    gameData.animationid = requestAnimationFrame(animate);

    resize3dCanvas();
    if (gameData.status === "paused") {
      handlePauseMessage();
    } else if (!gameData.winner && !gameData.forfeitMessage) {
      updateGameElementsPosition();
      updateScoreDisplay();
      gameData.renderer?.render(scene, camera);
    } else if (gameData.forfeitMessage || gameData.winner) {
      handleGameEnd();
      return;
    } else {
      gameData.renderer?.render(scene, camera);
    }
  })();
}

async function handleGameEnd() {
  if (gameData.forfeitMessage) {
    gameData.scoreDisplay.textContent = `${getForfeitMessage()}`;
    gameData.scoreDisplay.classList.add("centered");
  }
  if (gameData.winner) {
    gameData.scoreDisplay.textContent = `${getWinnerMessage()}`;
    gameData.scoreDisplay.classList.add("centered");
  }
}

async function updateGameElementsPosition() {
  ball.position.set(gameData.ball?.xpos, gameData.ball?.ypos, 10);
  ballLight.position.set(gameData.ball?.xpos, gameData.ball?.ypos, -10);
  paddle1.position.set(gameData.paddle1?.xpos, gameData.paddle1?.ypos + 40, 10);
  edges1.position.set(gameData.paddle1?.xpos, gameData.paddle1?.ypos + 40, 10);
  paddle2.position.set(gameData.paddle2?.xpos, gameData.paddle2?.ypos + 40, 10);
  edges2.position.set(gameData.paddle2?.xpos, gameData.paddle2?.ypos + 40, 10);
}

function getRandomColor() {
  const letters = "0123456789ABCDEF";
  let color = "#";
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

let previousScore = null;

function updateScoreDisplay() {
  const currentScore = `${gameData.player1} : ${gameData.paddle1.score} - ${gameData.player2} : ${gameData.paddle2.score}`;

  if (gameData.paddle1.score !== 0 || gameData.paddle2.score !== 0) {
    gameData.scoreDisplay.textContent = currentScore;
    if (currentScore !== previousScore) {
      ballLight.color.set(getRandomColor());
      previousScore = currentScore;
    }
  }
}

export function endGame() {
  cancelAnimationFrame(gameData.animationid);

  if (scene && ball && paddle1 && paddle2 && ballLight && ground)
    scene.remove(ball, paddle1, paddle2, ballLight, ground);

  scene =
    camera =
    ball =
    ballLight =
    paddle1 =
    paddle2 =
    ground =
    contour =
    middle =
    edges1 =
    edges2 =
    gameData.animationid =
      null;

  if (gameData.renderer) {
    gameData.renderer.dispose();
  }

  if (gameData.scoreDisplay) {
    gameData.scoreDisplay.remove();
    gameData.scoreDisplay = null;
  }
  gameData.renderer = null;
}
