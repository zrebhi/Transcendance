import { loadView, getCsrfToken, adjustPageContainerHeight, updatePage, clearPage } from './SPAContentLoader.js';
import { joinQueue, cancelQueue, startLocalGame } from '/matchmaking/static/matchmaking/js/matchmaking.js';
import { drawCanvas } from "/pong_app/static/pong_app/js/draw.js";
import { forfeitGame, quitGame} from "/pong_app/static/pong_app/js/pong.js";

// Define actions for various buttons in the application
const buttonActions = {
    'homeButton': () => loadView('/home/'),
    'loginButton': () => loadView('/users/login/'),
    'registerButton': () => loadView('/users/register/'),
    'profileButton': () => loadView('/users/profile/'),
    'tournamentsButton': () => loadView('/tournaments/'),
    'createTournamentButton': () => loadView('/tournaments/create/'),
    'playButton': () => { if (window.gameSocket) { clearPage(); drawCanvas(); } },
    'logoutButton': handleLogoutButtonClick,
    'joinQueueButton': joinQueue,
    'localPlayButton': startLocalGame,
    'cancelQueueButton': cancelQueue,
    'forfeitGameButton': forfeitGame,
    'quitGameButton': quitGame,
};

// Initialize event handlers
export function eventHandlers() {
    // Adjust the height of the page container on load and window resize
    window.addEventListener('DOMContentLoaded', adjustPageContainerHeight);
    window.addEventListener('resize', adjustPageContainerHeight);

    // Listen for form submissions in the page container
    document.getElementById('pageContainer').addEventListener('submit', handleSubmit);
    // Add click event listeners to various containers
    ['navbarContainer', 'pageContainer', 'sidebarContainer', 'queueContainer'].forEach(containerId => {
        document.getElementById(containerId).addEventListener('click', handleClick);
    });
}

// Generic click handler that maps buttons to their actions
function handleClick(event) {
    const action = buttonActions[event.target.id];
    if (action) {
        event.preventDefault();
        event.stopPropagation(); // Stop the event from bubbling up
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
        console.log(data["next_url"]);
    } else {
        document.getElementById('pageContainer').innerHTML = data['form_html'];
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
