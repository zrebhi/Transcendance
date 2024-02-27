import { gameData } from './pong.js';

let scene, camera, ball, ballLight, paddle1, paddle2, ambientLight, ballTrail, bubbleTrail;
let textMeshes = {};
let fontLoaded = false;
const fontLoader = new THREE.FontLoader();
let font;
const bubbles = [];
const bubbleCount = 40;
let lastBubbleSpawnTime = Date.now();
const bubbleSpawnInterval = 100; // Spawn a bubble every 100ms

fontLoader.load('https://threejs.org/examples/fonts/helvetiker_bold.typeface.json', function (loadedFont) {
    font = loadedFont;
    fontLoaded = true;
});

export function setupCanvas() {
    if (!gameData.renderer) {
        const canvas = document.createElement('canvas');
        canvas.width = gameData.canvasContainerWidth;
        canvas.height = gameData.canvasContainerHeight;
        const canvasContainer = document.getElementById('canvasContainer');
        
        if (canvasContainer) {
            canvasContainer.appendChild(canvas);
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, gameData.canvasContainerWidth / gameData.canvasContainerHeight, 0.1, 1000);
            camera.position.set(600, 450, 570);
            camera.scale.y = -1;
        
            gameData.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
            gameData.renderer.setSize(gameData.canvasContainerWidth, gameData.canvasContainerHeight);
            gameData.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            addElementsToScene();
            createBubbleTrail();
        }
    }
}

function addElementsToScene() {
    addPaddles();
    addBall();
    addLights();
    addTextMeshes();
}

function createBubbleTrail() {
    const bubbleGeometry = new THREE.SphereGeometry(6, 30, 30);
    const bubbleMaterial = new THREE.MeshBasicMaterial({ color: 0xadd8e6, transparent: true, opacity: 0.7 });

    for (let i = 0; i < bubbleCount; i++) {
        const bubble = new THREE.Mesh(bubbleGeometry, bubbleMaterial);
        bubble.visible = false; // Bubbles are initially invisible
        scene.add(bubble);
        bubbles.push(bubble);
    }
}

function updateBubbleTrail() {
    if (Date.now() - lastBubbleSpawnTime > bubbleSpawnInterval) {
        lastBubbleSpawnTime = Date.now();
        const bubble = bubbles.shift(); // Remove the oldest bubble
        bubble.position.set(ball.position.x, ball.position.y, ball.position.z);
        bubble.visible = true;
        bubbles.push(bubble); // Add it back to the end of the array
    }

    bubbles.forEach(bubble => {
        bubble.position.y -= 1; // Move bubbles upwards to create trail effect
        bubble.material.opacity *= 0.98; // Slow fade out effect
        if (bubble.material.opacity < 0.1) {
            bubble.visible = false;
            bubble.material.opacity = 0.7; // Reset opacity for reuse
        }
    });
}

function addPaddles() {
    const paddleGeometry = new THREE.BoxGeometry(20, 90, 10);
    const paddleMaterial = new THREE.MeshLambertMaterial({color: 0x1E90FF}); // Blue paddles for aquatic theme
    paddle1 = new THREE.Mesh(paddleGeometry, paddleMaterial);
    paddle2 = new THREE.Mesh(paddleGeometry, paddleMaterial);
    
    paddle1.position.set(gameData.paddle1.xpos, gameData.paddle1.ypos + 40, 0);
    paddle2.position.set(gameData.paddle2.xpos, gameData.paddle2.ypos + 40, 0);
    scene.add(paddle1, paddle2);
}

function addBall() {
    const ballGeometry = new THREE.SphereGeometry(9, 16, 16);
    const ballMaterial = new THREE.MeshPhongMaterial({color: 0x00FFFF, emissive: 0x00FFFF}); // Cyan ball for aquatic look
    ball = new THREE.Mesh(ballGeometry, ballMaterial);
    scene.add(ball);

    ballLight = new THREE.PointLight(0x00FFFF, 30, 10000); // Cyan light to match the ball
    ballLight.position.set(gameData.ball.xpos, gameData.ball.ypos, -10);
    scene.add(ballLight);
}

function addLights() {
    ambientLight = new THREE.AmbientLight(0xadd8e6, 1); // Soft blue light for underwater effect
    scene.add(ambientLight);
}

function addTextMeshes() {
    updateText('status', gameData?.status, 500, 100);
    updateText('player1Score', `${gameData?.player1} : ${gameData?.paddle1?.score}`, 50, 100);
    updateText('player2Score', `${gameData?.player2} : ${gameData?.paddle2?.score}`, 950, 100);
}

function updateText(id, string, x, y) {
    if (!fontLoaded) {
        setTimeout(() => {
            updateText(id, string, x, y);
        }, 100);
        return;
    }

    if (!string) return;

    const existingTextMesh = textMeshes[id]?.mesh;

    const textGeometry = new THREE.TextGeometry(string, {
        font: font,
        size: 30,
        height: 2,
        curveSegments: 6,
        bevelEnabled: false,
    });
    textGeometry.scale(1, -1, 1);
    const textMaterial = new THREE.MeshPhongMaterial({ color: 0x1E90FF }); // Blue for aquatic theme
    const textMesh = new THREE.Mesh(textGeometry, textMaterial);
    textMesh.position.set(x, y, 0);
    scene.add(textMesh);

    if (existingTextMesh) {
        scene.remove(existingTextMesh);
    }

    textMeshes[id] = { mesh: textMesh, string: string };
}

export function draw3dCanvas() {
    setupCanvas();
    function animate() {
        gameData.animationid = requestAnimationFrame(animate);
        updateText('status', gameData?.status, 500, 100);
        updateText('player1Score', `${gameData?.player1} : ${gameData?.paddle1?.score}`, 50, 100);
        updateText('player2Score', `${gameData?.player2} : ${gameData?.paddle2?.score}`, 950, 100);

        if (!gameData.winner && !gameData.forfeitMessage) {
            updateGameElementsPosition();
            updateBubbleTrail();
            gameData.renderer?.render(scene, camera);
        } else if (gameData.forfeitMessage || gameData.winner) {
            handleGameEnd();
            return;
        } else {
            gameData.renderer?.render(scene, camera);
        }
    }
    animate();
}

function updateGameElementsPosition() {
    ball.position.set(gameData.ball?.xpos, gameData.ball?.ypos, 0);
    ballLight.position.set(gameData.ball?.xpos, gameData.ball?.ypos, -10);
    paddle1.position.set(gameData.paddle1?.xpos, gameData.paddle1?.ypos + 40, 0);
    paddle2.position.set(gameData.paddle2?.xpos, gameData.paddle2?.ypos + 40, 0);
}

function handleGameEnd() {
    if (gameData.forfeitMessage) {
        updateText('forfeitMessage', gameData.forfeitMessage, 450, 500);
    } else if (gameData.winner) {
        updateText('winner', `Winner: ${gameData.winner}`, 450, 500);
    gameData.renderer?.render(scene, camera);
    }

    endGame();
}

export function endGame() {
    cancelAnimationFrame(gameData.animationid);
    
    if (scene && ball && paddle1 && paddle2 && ballLight)
        scene.remove(ball, paddle1, paddle2, ballLight);
    
    for (const key in textMeshes) {
        if (textMeshes.hasOwnProperty(key)) {
            const textMesh = textMeshes[key].mesh;
            if (textMesh && scene)
                scene.remove(textMesh);
        }
    }
    
    scene = camera = ball = ballLight = paddle1 = paddle2 = gameData.animationid = null;

    if (gameData.renderer) {
        gameData.renderer.dispose();
    }
}
