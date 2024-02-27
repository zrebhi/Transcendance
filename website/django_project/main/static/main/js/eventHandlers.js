import {loadView, getCsrfToken, adjustPageContainerHeight, updatePage} from './SPAContentLoader.js';
import { joinQueue, cancelQueue, startLocalGame } from '/matchmaking/static/matchmaking/js/matchmaking.js';
import { forfeitGame, quitGame, changeRender} from "/pong_app/static/pong_app/js/pong.js";
import { joinTournament, tournamentView, updateReadyState } from "/tournaments/static/tournaments/js/tournaments.js";

// Define actions for various buttons in the application
const buttonActions = {
    'homeButton': () => loadView('/home/'),
    'loginButton': () => loadView('/users/login/'),
    'logoutButton': handleLogoutButtonClick,
    'registerButton': () => loadView('/users/register/'),
    'profileButton': () => loadView('/users/profile/'),
    'tournamentsListButton': () => loadView('/tournaments/'),
    'createTournamentButton': () => loadView('/tournaments/create/'),
    'tournamentUserReadyButton': (event) => updateReadyState(event, window.tournamentWebSocket, 'ready'),
    'tournamentUserNotReadyButton': (event) => updateReadyState(event, window.tournamentWebSocket, 'not_ready'),
    'tournamentButton': tournamentView,
    'joinQueueButton': joinQueue,
    'localPlayButton': startLocalGame,
    'cancelQueueButton': cancelQueue,
    'forfeitGameButton': forfeitGame,
    'quitGameButton': quitGame,
    'changeRenderButton': changeRender,
};

// Initialize event handlers
export function eventHandlers() {
    console.log("Event handlers called");

    // Adjust the height of the page container on load and window resize
    window.addEventListener('DOMContentLoaded', adjustPageContainerHeight);
    window.addEventListener('resize', adjustPageContainerHeight);

    // Listen for form submissions in the page container
    document.getElementById('pageContainer').addEventListener('submit', handleSubmit);
    // Add click event listeners to various containers
    ['navbarContainer', 'pageContainer', 'sidebarContainer', 'queueContainer'].forEach(containerId => {
        document.getElementById(containerId).addEventListener('click', handleClick);
    });

    // Add click event listeners to joinTournament buttons.
    // They need to be handled differently because each button has a different data-tournament-id
    document.getElementById('pageContainer').addEventListener('click', function(event) {
        // Find the closest element with the class 'joinTournamentButton' up the DOM tree
        const joinTournamentButton = event.target.closest('.joinTournamentButton');
        if (joinTournamentButton) {
            const tournamentId = joinTournamentButton.getAttribute('data-tournament-id');
            joinTournament(event, tournamentId);
        }
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
        loadView(data["next_url"])
        .then(updatePage)
        .catch(error => console.error('Error:', error));
    } else {
        document.getElementById('pageContainer').innerHTML = data['form_html'];
    }
}

// Logout button handler
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
            loadView(data["next_url"])
            .then(updatePage)
            .then(() => console.log("Logout successful"))
            .catch(error => console.error('Error:', error));
        }
    })
    .catch(error => console.error('Error:', error));
}
