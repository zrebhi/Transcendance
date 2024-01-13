import { loadView, getCsrfToken, adjustPageContainerHeight, updatePage, loadGame, clearPage } from './SPAContentLoader.js';
import { joinQueue, cancelQueue, startLocalGame } from '/static/matchmaking/js/matchmaking.js';
import { drawCanvas } from "/static/pong_app/js/pong_template.js";

// Define actions for various buttons in the application
const buttonActions = {
    'homeButton': () => loadView('/home/'),
    'loginButton': () => loadView('/users/login/'),
    'registerButton': () => loadView('/users/register/'),
    'playButton': () => { if (window.gameSocket) { clearPage(); drawCanvas(); } },
    'logoutButton': handleLogoutButtonClick,
    'profileButton': () => loadView('/users/profile/'),
    'joinQueueButton': joinQueue,
    'localPlayButton': startLocalGame,
    'cancelQueueButton': cancelQueue
};

// Initialize event handlers
export function eventHandlers() {
    // Adjust the height of the page container on load and window resize
    window.addEventListener('DOMContentLoaded', adjustPageContainerHeight);
    window.addEventListener('resize', adjustPageContainerHeight);

    // Listen for form submissions in the page container
    document.getElementById('pageContainer').addEventListener('submit', handleSubmit);
    // Add click event listeners to various containers
    ['navbarContainer', 'pageContainer', 'sidebarContainer', 'queueWrapper'].forEach(containerId => {
        document.getElementById(containerId).addEventListener('click', handleClick);
    });
}

// Generic click handler that maps buttons to their actions
function handleClick(event) {
    const action = buttonActions[event.target.id];
    if (action) {
        event.preventDefault();
        action(event);
    }
}

// Handles form submission with AJAX
function handleSubmit(event) {
    if (event.target.matches('form')) {
        event.preventDefault();
        const form = event.target;
        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken(),
            },
            credentials: 'include'
        })
        .then(response => response.json())
        .then(handleFormResponse)
        .catch(error => console.error('Error:', error));
    }
}

// Processes the response from form submission
function handleFormResponse(data) {
    if (data.success) {
        updatePage();
        loadView(data["next_url"]).catch(error => console.error('Error:', error));
    } else {
        document.getElementById('pageContainer').innerHTML = data.form_html;
    }
}

// Logout button handler
function handleLogoutButtonClick(event) {
    console.log("Logout button clicked");
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
            updatePage();
            loadView(data["next_url"]).catch(error => console.error('Error:', error));
        }
    })
    .catch(error => console.error('Error:', error));
}

// Execute the event handler setup
eventHandlers();
