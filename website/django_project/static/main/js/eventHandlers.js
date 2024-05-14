import {
    loadView,
    getCsrfToken,
    adjustPageContainerHeight,
    updatePage,
    getSessionId,
    showUI, loadGame,
    getLanguage, setLanguage,
    underlineNavbar
} from './SPAContentLoader.js';
import { joinQueue, cancelQueue, startLocalGame } from '/static/matchmaking/js/matchmaking.js';
import { forfeitGame, quitGame, changeRender} from "/static/pong_app/js/pong.js";
import { joinTournament, leaveTournament, tournamentView,
    updateReadyState, observeRoundTimers, createTournament } from "/static/tournaments/js/tournaments.js";

// Define actions for various buttons in the application
const buttonActions = {
    'homeButton': () => loadView('/home/'),
    'loginButton': () => loadView('/users/login/'),
    'logoutButton': handleLogoutButtonClick,
    'registerButton': () => loadView('/users/register/'),
    'profileButton': () => loadView('/users/profile/'),
    'tournamentsListButton': () => loadView('/tournaments/'),
    'createTournamentButton': () => createTournament(),
    'tournamentUserReadyButton': (event) => updateReadyState(event, window.tournamentWebSocket, 'ready'),
    'tournamentUserNotReadyButton': (event) => updateReadyState(event, window.tournamentWebSocket, 'not_ready'),
    'tournamentButton': tournamentView,
    'joinQueueButton': joinQueue,
    'localPlayButton': startLocalGame,
    'cancelQueueButton': cancelQueue,
    'forfeitGameButton': forfeitGame,
    'quitGameButton': quitGame,
    'setLanguageButton': setLanguage,
    'changeRenderButton': changeRender
};

// Initialize event handlers
export function eventHandlers() {
    console.log("Event handlers called");

    // Adjust the height of the page container on load and window resize
    window.addEventListener('DOMContentLoaded', adjustPageContainerHeight);
    window.addEventListener('resize', adjustPageContainerHeight);

    window.addEventListener('popstate', async (event) => {
        console.log('State popped:', event.state);

        // Use the stored state if available, or fallback to window.location.pathname
        // This ensures that even if the state is null or undefined, the application
        // can still load the correct view based on the URL path.
       
        const path = event.state ? event.state.path : window.location.pathname;
        await loadView(path, false, true).catch(error => console.error('Error:', error));
    });

    // Listen for form submissions in the page container
    document.getElementById('pageContainer').addEventListener('submit', handleSubmit);
    // Add click event listeners to various containers
    ['navbarContainer', 'pageContainer', 'queueContainer'].forEach(containerId => {
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

    document.getElementById('pageContainer').addEventListener('click', function(event) {
        const leaveTournamentButton = event.target.closest('.leaveTournamentButton');
        if (leaveTournamentButton) {
            const tournamentId = leaveTournamentButton.getAttribute('data-tournament-id');
            leaveTournament(event, tournamentId);
        }
    });
    

    // Add a MutationObserver to observe round timers
    observeRoundTimers();
}

// Generic click handler that maps buttons to their actions
async function handleClick(event) {
    const action = buttonActions[event.target.id];
    if (action) {
        event.preventDefault();
        await action(event);
    }
}

// Handles form submission with AJAX
async function handleSubmit(event) {
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
async function handleFormResponse(data) {
    if (data.success) {
        try {
            await updatePage();
            await loadView(data["next_url"])
        } catch (error) { (console.error('Error:', error)); }
    } else
    {
      console.log(data);
        document.getElementById('pageContainer').innerHTML = data['form_html'];
    }
}

// Logout button handler
async function handleLogoutButtonClick(event) {
    event.preventDefault();
    fetch('/users/logout/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(async data =>  {
        if (data.success) {
            await setLanguage(event, "en");
            console.log("Logout successful");
        }
    })
    .catch(error => console.error('Error:', error));
}

