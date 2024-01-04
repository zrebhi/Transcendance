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

// Allow form submission via AJAX without refreshing the page
document.getElementById('pageContainer').addEventListener('submit', function(event) {
    // Check if the event target is a form
    if (event.target.matches('form')) {
        event.preventDefault();  // Prevent the default form submission

        var form = event.target;
        var submissionUrl = form.action; // Assuming the form's 'action' attribute is set
        var csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(submissionUrl, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadView(`https://localhost${data.next_url}`); // Load next view for successful submission
            } else {
                document.getElementById('pageContainer').innerHTML = data.form_html;
                // No need to re-attach the event listener
            }
        })
        .catch(error => console.error('Error:', error));
    }
});

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


document.getElementById('registerButton').addEventListener('click', function() {
    clearPage();

    loadView('https://localhost/users/register/');
});









