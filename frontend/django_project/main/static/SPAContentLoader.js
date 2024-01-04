function loadView(viewUrl) {
    return fetch(viewUrl)
        .then(response => response.text())
        .then(data => {
            document.getElementById('pageContainer').innerHTML = data;
            return data; // Resolve the promise with the fetched data
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
    clearPage();
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
    clearPage();

    loadView('https://localhost/home/')
    .catch(error => console.error('Error:', error));

});

function attachFormSubmitListener() {
    const form = document.querySelector('#pageContainer form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();

            var csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('https://localhost/users/register/', {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadView(`https://localhost${data.next_url}`);
                } else {
                    document.getElementById('pageContainer').innerHTML = data.form_html;
                    attachFormSubmitListener(); // Re-attach listener to the new form
                }
            })
            .catch(error => console.error('Error:', error));
        });
    } else {
        console.error('Form not found in the DOM');
    }
}


document.getElementById('registerButton').addEventListener('click', function() {
    clearPage();
    loadView('https://localhost/users/register/')
        .then(() => {
            attachFormSubmitListener(); // This is now called after the form is loaded
        })
        .catch(error => console.error('Error:', error));
});









