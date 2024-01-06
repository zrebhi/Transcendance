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

function updateNavbar() {
    fetch('https://localhost/navbar/')  // URL that returns the navbar HTML
        .then(response => response.text())
        .then(navbarHtml => {
            document.getElementById('navbarContainer').innerHTML = navbarHtml;
            setupNavbar();
        })
        .catch(error => console.error('Error:', error));
}

function updateSidebar() {
    fetch('https://localhost/sidebar/')  // URL that returns the sidebar HTML
        .then(response => response.text())
        .then(sidebarHtml => {
            document.getElementById('sidebarContainer').innerHTML = sidebarHtml;
        })
        .catch(error => console.error('Error:', error));
}

function getCsrfToken() {
    let csrfToken = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, "csrftoken".length + 1) === ("csrftoken" + '=')) {
                csrfToken = decodeURIComponent(cookie.substring("csrftoken".length + 1));
                break;
            }
        }
    }
    return csrfToken;
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
                clearPage();
                loadView(`https://localhost${data.next_url}`); // Load next view for successful submission
                updateNavbar();
                updateSidebar();
            } else {
                document.getElementById('pageContainer').innerHTML = data.form_html;
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

document.getElementById('navbarContainer').addEventListener('click', function(event) {
    if (event.target && event.target.id === 'homeButton') {
        clearPage();

        loadView('https://localhost/home/')
            .catch(error => console.error('Error:', error));
    }
});

let socketCreated = false;

document.getElementById('navbarContainer').addEventListener('click', function(event) {
    if (event.target && event.target.id === 'playButton') {
        clearPage();
        loadView('https://localhost/pong/')
            .then(() => loadScripts([
                'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js',
                'https://localhost/static/pong_app/js/pong_template.js',
            ], () => {
                if (!socketCreated) {
                    initGame();
                    socketCreated = true;
                } else
                    drawCanvas();
            }))
            .catch(error => console.error('Error:', error));
    }
});

document.getElementById('navbarContainer').addEventListener('click', function(event) {
    if (event.target && event.target.id === 'loginButton') {
        clearPage();
        loadView('https://localhost/users/login/'); // Adjust the URL as needed
    }
});

// Attaching the event listener to the page container for it to work on dynamically loaded content
document.getElementById('pageContainer').addEventListener('click', function(event) {
    if (event.target && event.target.id === 'loginButton') {
        clearPage();
        loadView('https://localhost/users/login/'); // Adjust the URL as needed
    }
});

document.getElementById('pageContainer').addEventListener('click', function(event) {
    if (event.target && event.target.id === 'registerButton') {
        clearPage();
        loadView('https://localhost/users/register/');
    }
});

document.getElementById('navbarContainer').addEventListener('click', function(event) {
    if (event.target && event.target.id === 'logoutButton') {
        event.preventDefault();
        fetch('/users/logout/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken() // Ensure you include CSRF token
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNavbar(); // Update navbar to reflect logged-out state
                    updateSidebar();
                    clearPage();
                    loadView(`https://localhost${data.next_url}`);
                }
            })
            .catch(error => console.error('Error:', error));
    }
});







