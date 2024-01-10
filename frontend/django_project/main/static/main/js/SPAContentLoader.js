import {setupNavbar} from './navbar.js';
import {eventHandlers} from './eventHandlers.js';
import {initGame, drawCanvas, clearCanvas} from '/static/pong_app/js/pong_template.js';
// Functions for dynamic content management in a Single Page Application (SPA)

/**
 * Adjusts the height of the page container based on the navbar's height.
 */
export function adjustPageContainerHeight() {
    const navbar = document.querySelector('.navbar');
    const navbarHeight = navbar.offsetHeight;
    const pageContainer = document.getElementById('pageContainer');

    if (pageContainer) {
        pageContainer.style.height = `calc(100vh - ${navbarHeight}px)`;
    }
}

/**
 * Loads a view into the page container from a given URL.
 * @param {string} viewUrl - The URL to fetch view content from.
 */
export function loadView(viewUrl) {
    clearPage();

    return fetch(viewUrl)
        .then(response => response.text())
        .then(data => {
            document.getElementById('pageContainer').innerHTML = data;
        });
}

export function loadGame(sessionId) {
    if (!window.socketCreated)
        window.socketCreated = false;
    loadView('/pong/')
        .then(() => loadScripts([
            'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js',
            '/static/pong_app/js/pong_template.js',
        ], async () => {
            if (!window.socketCreated) {
                await initGame(sessionId);
                window.socketCreated = true;
                updateNavbar();
            } else {
                drawCanvas();
            }
        }))
        .catch(error => console.error('Error:', error));
}

/**
 * Loads a series of scripts dynamically and executes a callback once complete.
 * @param {string[]} scriptUrls - Array of script URLs to load.
 * @param {Function} callback - Callback function to execute after loading scripts.
 */
export function loadScripts(scriptUrls, callback) {
    return scriptUrls.reduce((promise, scriptUrl) => {
        return promise.then(() => loadScript(scriptUrl));
    }, Promise.resolve()).then(callback);
}

/**
 * Dynamically loads a single script.
 * @param {string} src - The source URL of the script to load.
 */
function loadScript(src) {
    return new Promise((resolve, reject) => {
        let script = document.createElement('script');
        script.src = src;
        script.type = 'module';
        script.className = 'dynamic-script';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * Clears the page container and removes all dynamically loaded scripts.
 */
export function clearPage() {
    if (typeof clearCanvas === 'function') clearCanvas();

    const dynamicScripts = document.querySelectorAll('.dynamic-script');
    dynamicScripts.forEach(script => script.parentNode.removeChild(script));
    document.getElementById('pageContainer').innerHTML = '';
}

/**
 * Fetches and updates the navbar HTML content.
 */
export function updateNavbar() {
    fetch('/navbar/')
        .then(response => response.text())
        .then(navbarHtml => {
            document.getElementById('navbarContainer').innerHTML = navbarHtml;
            setupNavbar();
        })
        .catch(error => console.error('Error:', error));
}

/**
 * Fetches and updates the sidebar HTML content.
 */
export function updateSidebar() {
    fetch('/sidebar/')
        .then(response => response.text())
        .then(sidebarHtml => {
            document.getElementById('sidebarContainer').innerHTML = sidebarHtml;
        })
        .catch(error => console.error('Error:', error));
}

export function updatePage() {
    fetch('/')
        .then(response => response.text())
        .then(pageHtml => {
            document.body.innerHTML = pageHtml;
        })
        .then(() => {
            loadScripts(["/static/main/js/eventHandlers.js",
            "/static/main/js/navbar.js",
            "/static/main/bootstrap/js/bootstrap.bundle.min.js"
            ], () => {
                eventHandlers();
                setupNavbar();
            })
                .catch(error => console.error('Error:', error));
        })
        .catch(error => console.error('Error:', error));
}

/**
 * Retrieves the CSRF token from cookies.
 * @returns {string|null} The CSRF token if found, otherwise null.
 */
export function getCsrfToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const trimmedCookie = cookie.trim();
        if (trimmedCookie.startsWith("csrftoken=")) {
            csrfToken = decodeURIComponent(trimmedCookie.substring("csrftoken".length + 1));
            break;
        }
    }
    return csrfToken;
}
