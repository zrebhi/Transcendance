function loadView(viewUrl) {
        return fetch(viewUrl)
            .then(response => response.text())
            .then(data => {
                document.getElementById('pageContainer').innerHTML = data;
            });
    }

function loadScripts(scriptUrls, callback) {
    return scriptUrls.reduce((promise, scriptUrl) => {
        return promise.then(() => loadScript(scriptUrl));
    }, Promise.resolve()).then(callback);
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        let script = document.createElement('script');
        script.src = src;
        script.className = 'dynamic-script'; // Add a class to identify the script
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}


function clearPage() {
    // Call clearCanvas if it's available
    if (typeof clearCanvas === 'function')
        clearCanvas();
    // Remove all dynamically loaded scripts
    const dynamicScripts = document.querySelectorAll('.dynamic-script');
    dynamicScripts.forEach(script => {
        script.parentNode.removeChild(script);
    });
    // Clear the page container
    document.getElementById('pageContainer').innerHTML = '';
}


let socketCreated = false;

document.getElementById('playButton').addEventListener('click', function() {
    loadView('https://localhost/pong/')
        .then(() => loadScripts([
            'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js',
            'https://localhost/static/pong_app/pong_template.js'
        ], () => {
            if (!socketCreated) {
                initGame();
                socketCreated = true;
            }
            else
                drawCanvas();
        }))
        .catch(error => console.error('Error:', error));
});

document.getElementById('homeButton').addEventListener('click', function() {
    clearPage(); // From pong_template.js

    loadView('https://localhost/pong/')
    .catch(error => console.error('Error:', error));

});