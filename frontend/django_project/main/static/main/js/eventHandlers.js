import { loadView, clearPage, loadScripts, getCsrfToken, updateNavbar, updateSidebar, adjustPageContainerHeight } from './SPAContentLoader.js';
import {joinQueue} from "./matchmaking.js";

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

// let socketCreated = false;
//
// function handlePlayButtonClick() {
//     clearPage();
//     loadView('https://localhost/pong/')
//         .then(() => loadScripts([
//             'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js',
//             'https://localhost/static/pong_app/js/pong_template.js',
//         ], () => {
//             if (!socketCreated) {
//                 initGame();
//                 socketCreated = true;
//             } else {
//                 drawCanvas();
//             }
//         }))
//         .catch(error => console.error('Error:', error));
// }

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


