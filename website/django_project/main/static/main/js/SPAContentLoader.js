import { setupNavbar } from './navbar.js';
import { eventHandlers } from './eventHandlers.js';
import { getGame } from '/pong_app/static/pong_app/js/pong.js';
import { clearCanvas } from '/pong_app/static/pong_app/js/draw.js';
import { tournamentWebSocketConnection } from "/tournaments/static/tournaments/js/tournaments.js";


export function adjustPageContainerHeight() {
    const navbarHeight = document.querySelector('.navbar').offsetHeight;
    document.getElementById('pageContainer').style.height = `calc(100vh - ${navbarHeight}px)`;
}

export function loadView(viewPath) {
    // Determine the base URL from the current location
    const baseUrl = window.location.origin;
    // Construct the full URL by combining the base URL with the viewPath
    const fullUrl = new URL(viewPath, baseUrl).href;

    console.log('Loading view:', fullUrl);
    clearPage();

    // Update the browser's URL and history without reloading the page
    // Use the relative path (viewPath) for pushState to maintain relative URL in the browser
    history.pushState({ path: viewPath }, '', viewPath);

    return fetch(fullUrl)
        .then(response => response.text())
        .then(data => {
            document.getElementById('pageContainer').innerHTML = data;
        })
        .catch(error => console.error('Error loading view:', error));
}


export async function loadGame(sessionId) {
    if (!sessionId) return;

    try {
        await hideUI();
        await loadView(`/pong/${sessionId}/`);
        await loadScript('pong_app/static/pong_app/p5/p5.js');
        await getGame(sessionId);

    } catch (error) {
        console.error('Error:', error);
    }
}

function hideUI() {
    document.getElementById('navbarContainer').classList.add('d-none');
    document.getElementById('sidebarContainer').classList.add('d-none');
}

export function showUI() {
    document.getElementById('navbarContainer').classList.remove('d-none');
    document.getElementById('sidebarContainer').classList.remove('d-none');
}

export function loadScripts(scriptUrls) {
    removeExistingScripts(scriptUrls);
    return scriptUrls.reduce((promise, scriptUrl) => promise.then(() => loadScript(scriptUrl)), Promise.resolve());
}

function removeExistingScripts(scriptUrls) {
    scriptUrls.forEach(url => {
        let existingScript = document.querySelector(`script[src="${url}"]`);
        if (existingScript) {
            existingScript.remove();
        }
    });
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const baseUrl = window.location.origin;
        const fullSrc = new URL(src, baseUrl).href;

        const script = document.createElement('script');
        script.src = fullSrc;
        script.type = 'module';
        script.className = 'dynamic-script';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

export function clearPage() {
    if (typeof clearCanvas === 'function') clearCanvas();
    document.getElementById('pageContainer').innerHTML = '';
}

export function updateNavbar() {
    fetch('/navbar/')
        .then(response => response.text())
        .then(navbarHtml => {
            document.getElementById('navbarContainer').innerHTML = navbarHtml;
        })
        .then (() => {
            loadScript('/static/main/js/navbar.js').catch(error => console.error('Error:', error));
            setupNavbar();
        })
        .catch(error => console.error('Error:', error));
}

export function updateSidebar() {
    fetch('/sidebar/')
        .then(response => response.text())
        .then(sidebarHtml => document.getElementById('sidebarContainer').innerHTML = sidebarHtml)
        .catch(error => console.error('Error:', error));
}

export function updatePage() {
    console.log('Updating page');
    fetch('/')
        .then(response => response.text())
        .then(pageHtml => document.body.innerHTML = pageHtml)
        .then(() => loadScripts([
            '/static/main/js/eventHandlers.js',
            '/static/main/js/navbar.js',
            '/static/tournaments/js/tournaments.js',
            '/static/main/bootstrap/js/bootstrap.bundle.min.js'
        ]))
        .then(() => {
            adjustPageContainerHeight();
            setupNavbar();
            eventHandlers();
            loadGame(getSessionId()).catch(error => console.error('Error:', error));
            console.log('Tournament ID:', getTournamentId());
            tournamentWebSocketConnection(getTournamentId());
        })
        .catch(error => console.error('Error:', error));
}

function getSessionId() {
    const sessionIdMeta = document.querySelector('meta[name="user-session-id"]');

    let sessionId;
    sessionIdMeta ? sessionId = sessionIdMeta.getAttribute('content') : null;

    return sessionId;
}

export function getTournamentId() {
    const tournamentIdMeta = document.querySelector('meta[name="user-tournament-id"]');

    let tournamentId;
    tournamentIdMeta ? tournamentId = tournamentIdMeta.getAttribute('content') : null;

    return tournamentId;
}

export function getCsrfToken() {
    return document.cookie.split(';').find(cookie => cookie.trim().startsWith("csrftoken="))?.split('=')[1] ?? null;
}
