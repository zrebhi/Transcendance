import { gameData } from './pong.js';
import { getPauseMessage } from './draw.js';

let scene, camera, ball, ballLight, paddle1, paddle2;
let textMeshes = {};
let fontLoaded = false;
const fontLoader = new THREE.FontLoader();
let font;

fontLoader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', function (loadedFont) {
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
        
            gameData.renderer = new THREE.WebGLRenderer({ canvas });
            gameData.renderer.setSize(gameData.canvasContainerWidth, gameData.canvasContainerHeight);

            addElementsToScene();
        }
    }
}


function addElementsToScene() {
    addPaddles();
    addBall();
    addLights();
    addTextMeshes();
}

function addPaddles() {
    const paddleGeometry = new THREE.BoxGeometry(20, 90, 10);
    const paddleMaterial = new THREE.MeshPhongMaterial({color: 0xffffff});
    paddle1 = new THREE.Mesh(paddleGeometry, paddleMaterial);
    paddle2 = new THREE.Mesh(paddleGeometry, paddleMaterial);
    
    paddle1.position.set(gameData.paddle1.xpos, gameData.paddle1.ypos + 40, 0);
    paddle2.position.set(gameData.paddle2.xpos, gameData.paddle2.ypos + 40, 0);
    scene.add(paddle1, paddle2);
}

function addBall() {
    const ballGeometry = new THREE.SphereGeometry(9, 32, 32);
    const ballMaterial = new THREE.MeshPhongMaterial({color: 0x800080, emissive: 0x800080, transparent: true, opacity: 1});
    ball = new THREE.Mesh(ballGeometry, ballMaterial);
    scene.add(ball);

    ballLight = new THREE.PointLight(0x800080, 30, 10000);
    ballLight.position.set(gameData.ball.xpos, gameData.ball.ypos, -10);
    scene.add(ballLight);
}

function addLights() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
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

    if (!string) return ;

    const existingTextMesh = textMeshes[id]?.mesh;

    const textGeometry = new THREE.TextGeometry(string, {
        font: font,
        size: 30,
        height: 2,
        curveSegments: 12,
        bevelThickness: 10,
        bevelSize: 8,
        bevelOffset: 0,
        bevelSegments: 5,
    });
    textGeometry.scale(1, -1, 1);
    const textMaterial = new THREE.MeshPhongMaterial({ color: 0xffffff, specular: 0xffffff });
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
            gameData.renderer?.render(scene, camera);
        } else if (gameData.forfeitMessage || gameData.winner) {
            handleGameEnd();
            return ;
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
        updateText('forfeitMessage', gameData.forfeitMessage, 500, 500);
    } else if (gameData.winner) {
        updateText('winner', `Winner: ${gameData.winner}`, 500, 500);
    }
    gameData.renderer?.render(scene, camera);

    endGame();
}

export function endGame() {
    cancelAnimationFrame(gameData.animationid);
    
    // Supprimer les éléments de la scène
    scene.remove(ball, paddle1, paddle2, ballLight);
    
    // Supprimer les éléments de texte de la scène
    for (const key in textMeshes) {
        if (textMeshes.hasOwnProperty(key)) {
            const textMesh = textMeshes[key].mesh;
            scene.remove(textMesh);
        }
    }
    
    // Réinitialiser les variables à null
    scene = camera = ball = ballLight = paddle1 = paddle2 = gameData.animationid = null;
    
    // Disposer du renderer WebGL
    if (gameData.renderer) {
        gameData.renderer.dispose();
        gameData.renderer = null;
    }
}