import {loadView, getCsrfToken, adjustPageContainerHeight, updatePage, loadGame} from './SPAContentLoader.js';
import {joinQueue, cancelQueue} from "/static/matchmaking/js/matchmaking.js";

export function eventHandlers() {
    console.log("eventHandlers.js loaded");
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
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updatePage();
                    loadView(`${data.next_url}`)
                        .catch(error => console.error('Error:', error));
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
            loadView(`/${targetId === 'homeButton' ? 'home' : 'users/login'}/`)
                .catch(error => console.error('Error:', error));
        } else if (targetId === 'playButton') {
            loadGame();
        } else if (targetId === 'logoutButton') {
            handleLogoutButtonClick(event);
        }
    });

    /**
     * Handles navigation clicks in the sidebar container.
     */
    document.getElementById('sidebarContainer').addEventListener('click', function(event) {
        const targetId = event.target.id;
        if (event.target.id === "profileButton") {
            loadView(`/users/profile/`)
                .catch(error => console.error('Error:', error));
        }
    });

    /**
     * Handles additional click interactions within the dynamically loaded content.
     */
    document.getElementById('pageContainer').addEventListener('click', function(event) {
        if (event.target.id === 'registerButton' || event.target.id === 'loginButton') {
            loadView(`/${event.target.id === 'registerButton' ? 'users/register' : 'users/login'}/`)
                .catch(error => console.error('Error:', error));
        }
        if (event.target.id === 'joinQueueButton') {
            joinQueue();
        }
        if (event.target.id === 'cancelQueueButton') {
            cancelQueue();
        }
    });

    document.getElementById('queueWrapper').addEventListener('click', function(event) {
        if (event.target.id === 'cancelQueueButton') {
            cancelQueue();
        }
    });

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
                updatePage();
                loadView(`${data.next_url}`)
                    .catch(error => console.error('Error:', error));
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

eventHandlers();


