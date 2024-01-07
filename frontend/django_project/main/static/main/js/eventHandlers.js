import { loadView, clearPage, loadScripts, getCsrfToken, updateNavbar, updateSidebar, adjustPageContainerHeight } from './SPAContentLoader.js';

/**
 * Adjusts the height of the page container upon initial load and window resize.
 */
window.addEventListener('DOMContentLoaded', adjustPageContainerHeight);
window.addEventListener('resize', adjustPageContainerHeight);

/**
 * Handles form submissions within the page container to enable AJAX-based interactions.
 */
document.getElementById('pageContainer').addEventListener('submit', function(event) {
    if (event.target.matches('form')) {
        event.preventDefault();

        const form = event.target;
        const submissionUrl = form.action;
        const csrfToken = getCsrfToken();

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
                loadView(`https://localhost${data.next_url}`);
                updateNavbar();
                updateSidebar();
            } else {
                document.getElementById('pageContainer').innerHTML = data.form_html;
            }
        })
        .catch(error => console.error('Error:', error));
    }
});

/**
 * Handles navigation clicks in the navbar container.
 */
document.getElementById('navbarContainer').addEventListener('click', function(event) {
    const targetId = event.target.id;
    if (targetId === 'homeButton' || targetId === 'loginButton') {
        clearPage();
        loadView(`https://localhost/${targetId === 'homeButton' ? 'home' : 'users/login'}/`);
    } else if (targetId === 'playButton') {
        handlePlayButtonClick();
    } else if (targetId === 'logoutButton') {
        handleLogoutButtonClick(event);
    }
});

/**
 * Handles additional click interactions within the dynamically loaded content.
 */
document.getElementById('pageContainer').addEventListener('click', function(event) {
    const targetId = event.target.id;
    if (event.target.id === 'registerButton' || event.target.id === 'loginButton') {
        clearPage();
        loadView(`https://localhost/${targetId === 'registerButton' ? 'users/register' : 'users/login'}/`);
    }
});

let socketCreated = false;

function handlePlayButtonClick() {
    clearPage();
    loadView('https://localhost/pong/')
        .then(() => loadScripts([
            'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js',
            'https://localhost/static/pong_app/js/pong_template.js',
        ], () => {
            if (!socketCreated) {
                initGame();
                socketCreated = true;
            } else {
                drawCanvas();
            }
        }))
        .catch(error => console.error('Error:', error));
}

/**
 * Handles the click event on the logout button.
 * Prevents default form submission and logs out the user.
 * @param {Event} event - The event object from the click event.
 */
function handleLogoutButtonClick(event) {
    event.preventDefault();
    fetch('/users/logout/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNavbar();
            updateSidebar();
            clearPage();
            loadView(`https://localhost${data.next_url}`);
        }
    })
    .catch(error => console.error('Error:', error));
}

document.getElementById('joinQueueButton').addEventListener('click', function() {
    joinQueue();
});

function joinQueue() {
    fetch('https://localhost/matchmaking/', {  // Update with the correct URL
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(), // Include CSRF token if needed
            'Content-Type': 'application/json'
        },
        credentials: 'include'  // Necessary for including cookies (like CSRF token)
    })
        .then(response => {
            console.log(response); // Check what the response looks like
            return response.text(); // Use text() if you're not sure it's JSON
        })
        .then(text => {
            try {
                const data = JSON.parse(text);
                console.log('Join queue response:', data);
                if (data.status === 'success') {
                    // Connect to the WebSocket for queue updates
                    connectToQueueWebSocket();
                } else {
                    // Handle error (user already in queue, not authenticated, etc.)
                    console.error('Error joining queue:', data.message);
                }
            } catch (error) {
                console.error('Error parsing JSON:', error);
            }
        })
}

function connectToQueueWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(protocol + '://' + window.location.host + '/ws/queue/');

    socket.onopen = (event) => {
        console.log("WebSocket connection opened:", event);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'game_matched') {
            // Redirect to game session or handle the match notification
            // window.location.href = `/game/${data.data.session_id}`;
            console.log('game_matched');
        }
    };

    socket.onclose = (event) => {
        console.log("WebSocket connection closed:", event);
    };

    socket.onerror = (event) => {
        console.error("WebSocket error:", event);
    };
}
