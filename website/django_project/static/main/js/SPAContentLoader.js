import { eventHandlers } from "./eventHandlers.js";
import { setupNavbar } from "./navbar.js";
import { showQueueUI } from "./queue.js";
import { queueSocket } from "/static/matchmaking/js/matchmaking.js";
import { clearCanvas } from "/static/pong_app/js/draw.js";
import { getGame } from "/static/pong_app/js/pong.js";
import { tournamentWebSocketConnection } from "/static/tournaments/js/tournaments.js";

export function adjustPageContainerHeight() {
  const navbarHeight = document.querySelector(".navbar").offsetHeight;
  document.getElementById(
    "pageContainer"
  ).style.height = `calc(100vh - ${navbarHeight}px)`;
}

export async function loadView(viewPath, updateHistory = true) {
  if (viewPath === "/") viewPath = "/home/";

  const language = getLanguage();
  if (!viewPath.includes("?language="))
    viewPath = `${viewPath}?language=${language}`;

  const baseUrl = window.location.origin;
  const fullUrl = new URL(viewPath, baseUrl).href;

  console.log("Loading view:", fullUrl);
  clearPage();

  if (updateHistory) history.pushState({ path: viewPath }, "", viewPath);

  // Include an Accept header in the fetch request
  return fetch(fullUrl, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "Cache-Control": "no-cache",
    },
  })
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("pageContainer").innerHTML = data;
    })
    .then(() => {
      underlineNavbar(viewPath);
    })
    .catch((error) => console.error("Error loading view:", error));
}

export async function loadGame(sessionId) {
  if (!sessionId) return;

  try {
    hideUI();
    await loadView(`/pong/${sessionId}/`);
    await loadScript("/static/pong_app/p5/p5.js");
    await getGame(sessionId);
  } catch (error) {
    console.error("Error:", error);
  }
}

function hideUI() {
  document.getElementById("navbarContainer").classList.add("d-none");
}

export function showUI() {
  document.getElementById("navbarContainer").classList.remove("d-none");
}

export function loadScripts(scriptUrls) {
  removeExistingScripts(scriptUrls);
  return scriptUrls.reduce(
    (promise, scriptUrl) => promise.then(() => loadScript(scriptUrl)),
    Promise.resolve()
  );
}

function removeExistingScripts(scriptUrls) {
  scriptUrls.forEach((url) => {
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

    const script = document.createElement("script");
    script.src = fullSrc;
    script.type = "module";
    script.className = "dynamic-script";
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

export function clearPage() {
  if (typeof clearCanvas === "function") clearCanvas();
  document.getElementById("pageContainer").innerHTML = "";
}

export function updateNavbar() {
  fetch(`/navbar/?language=${getLanguage()}`, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.text())
    .then((navbarHtml) => {
      document.getElementById("navbarContainer").innerHTML = navbarHtml;
    })
    .then(() => {
      loadScript("/static/main/js/navbar.js").catch((error) =>
        console.error("Error:", error)
      );
      setupNavbar();
    })
    .catch((error) => console.error("Error:", error));
}

export async function updatePage(viewURL = null) {
  console.log("Updating page");
  clearPage();

  try {
    const response = await fetch(`/?language=${getLanguage()}`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    const pageHtml = await response.text();
    document.body.innerHTML = pageHtml;

    await loadScripts([
      "/static/main/js/eventHandlers.js",
      "/static/main/js/navbar.js",
      "/static/tournaments/js/tournaments.js",
    ]);

    adjustPageContainerHeight();
    setupNavbar();
    eventHandlers();

    const sessionID = await getSessionId();
    console.log("Session ID:", sessionID);
    if (sessionID)
      await loadGame(sessionID).catch((error) =>
        console.error("Error:", error)
      );

    const tournamentId = await getTournamentId();
    tournamentWebSocketConnection(tournamentId);
    if (queueSocket) showQueueUI(); // TO-DO: Can be improved by using database queueEntry time for timer.
  } catch (error) {
    console.error("Error:", error);
  }
}

async function fetchSessionId() {
  // Fetch the main page HTML
  return fetch(`/?language=${getLanguage()}`, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "Cache-Control": "no-cache",
    },
  })
    .then((response) => response.text())
    .then((pageHtml) => {
      // Parse the fetched HTML to find the session ID meta tag
      const parser = new DOMParser();
      const doc = parser.parseFromString(pageHtml, "text/html");
      const sessionIdMeta = doc.querySelector('meta[name="user-session-id"]');

      return sessionIdMeta ? sessionIdMeta.getAttribute("content") : null;
    })
    .catch((error) => console.error("Error fetching session ID:", error));
}

export async function getSessionId() {
  let sessionId;
  try {
    sessionId = await fetchSessionId();
  } catch (error) {
    console.error("Failed to fetch session ID:", error);
  }
  return sessionId;
}

export async function fetchTournamentId() {
  // Fetch the main page HTML
  return fetch(`/?language=${getLanguage()}`, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "Cache-Control": "no-cache",
    },
  })
    .then((response) => response.text())
    .then((pageHtml) => {
      // Parse the fetched HTML to find the session ID meta tag
      const parser = new DOMParser();
      const doc = parser.parseFromString(pageHtml, "text/html");
      const tournamentIdMeta = doc.querySelector(
        'meta[name="user-tournament-id"]'
      );

      return tournamentIdMeta ? tournamentIdMeta.getAttribute("content") : null;
    })
    .catch((error) => console.error("Error fetching tournament ID:", error));
}

export async function getTournamentId() {
  let tournamentId;
  try {
    tournamentId = await fetchTournamentId();
  } catch (error) {
    console.error("Failed to fetch tournament ID:", error);
  }
  return tournamentId;
}

export function getCsrfToken() {
  return (
    document.cookie
      .split(";")
      .find((cookie) => cookie.trim().startsWith("csrftoken="))
      ?.split("=")[1] ?? null
  );
}

export function getLanguage() {
  switch (localStorage.getItem("lang")) {
    case "fr":
      return "fr";
    case "es":
      return "es";
    default:
      return "en";
  }
}

export function setLanguage(event, value = null) {
  event.preventDefault();
  if (!value) {
    value = event.target.getAttribute("lan");
    console.log(value);
  }
  if ((value !== "es" && value !== "fr") || !value)
    localStorage.setItem("lang", "en");
  else localStorage.setItem("lang", value);
  updatePage().catch((error) => console.error("Error:", error));
}

export function underlineNavbar(path) {
  // Get all navbar links
  const buttons = document.querySelectorAll(".navbar-nav .nav-link");

  // Remove the 'active' class from all buttons
  buttons.forEach((button) => button.classList.remove("active"));

  // Logic to determine which button to activate
  if (path.includes("tournaments")) {
    const tournamentsButton = document.getElementById("tournamentsListButton");
    if (tournamentsButton) {
      tournamentsButton.classList.add("active");
    } else {
      const tournamentButton = document.getElementById("tournamentButton");
      if (tournamentButton) tournamentButton.classList.add("active");
    }
  } else if (path.includes("login")) {
    const loginButton = document.getElementById("loginButton");
    if (loginButton) loginButton.classList.add("active");
    else underlineHomeButton();
  } else underlineHomeButton();
}

function underlineHomeButton() {
  const homeButton = document.getElementById("homeButton");
  if (homeButton) homeButton.classList.add("active");
}
