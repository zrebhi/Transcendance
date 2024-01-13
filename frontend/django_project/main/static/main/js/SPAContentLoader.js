import { setupNavbar } from './navbar.js';
import { eventHandlers } from './eventHandlers.js';
import { getGame, drawCanvas, clearCanvas } from '/static/pong_app/js/pong_template.js';

export function adjustPageContainerHeight() {
    const navbarHeight = document.querySelector('.navbar').offsetHeight;
    document.getElementById('pageContainer').style.height = `calc(100vh - ${navbarHeight}px)`;
}

export function loadView(viewUrl) {
    clearPage();
    return fetch(viewUrl)
        .then(response => response.text())
        .then(data => document.getElementById('pageContainer').innerHTML = data);
}

export async function loadGame(sessionId) {
    try {
        await loadView('/pong/');
        await loadScripts(['/static/pong_app/p5/p5.js', '/static/pong_app/js/pong_template.js']);
        await getGame(sessionId);  // Awaits getGame to complete before proceeding
    } catch (error) {
        console.error('Error:', error);
    }
}

export function loadScripts(scriptUrls) {
    return scriptUrls.reduce((promise, scriptUrl) => promise.then(() => loadScript(scriptUrl)), Promise.resolve());
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.type = 'module';
        script.className = 'dynamic-script';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

export function clearPage() {
    if (typeof clearCanvas === 'function') clearCanvas();
    document.querySelectorAll('.dynamic-script').forEach(script => script.remove());
    document.getElementById('pageContainer').innerHTML = '';
}

export function updateNavbar() {
    fetch('/navbar/')
        .then(response => response.text())
        .then(navbarHtml => {
            document.getElementById('navbarContainer').innerHTML = navbarHtml;
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
    fetch('/')
        .then(response => response.text())
        .then(pageHtml => document.body.innerHTML = pageHtml)
        .then(() => loadScripts(['/static/main/js/eventHandlers.js', '/static/main/js/navbar.js', '/static/main/bootstrap/js/bootstrap.bundle.min.js']))
        .then(() => {
            eventHandlers();
            setupNavbar();
        })
        .catch(error => console.error('Error:', error));
}

export function getCsrfToken() {
    return document.cookie.split(';').find(cookie => cookie.trim().startsWith("csrftoken="))?.split('=')[1] ?? null;
}
