(function () {
  // ─── CONFIG ───────────────────────────────────────────────
  const CHATBOT_URL = "https://chatbot-camping-eychecadous.onrender.com";
  const BUBBLE_COLOR = "#E87722"; // orange MP Solutions IA
  const BUBBLE_SIZE = "60px";
  // ──────────────────────────────────────────────────────────

  // Évite de charger deux fois
  if (document.getElementById("mpia-widget-container")) return;

  // ── STYLES ────────────────────────────────────────────────
  const style = document.createElement("style");
  style.textContent = `
    #mpia-bubble {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: ${BUBBLE_SIZE};
      height: ${BUBBLE_SIZE};
      background: ${BUBBLE_COLOR};
      border-radius: 50%;
      cursor: pointer;
      box-shadow: 0 4px 16px rgba(0,0,0,0.25);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 99999;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    #mpia-bubble:hover {
      transform: scale(1.08);
      box-shadow: 0 6px 20px rgba(0,0,0,0.32);
    }
    #mpia-bubble svg {
      width: 28px;
      height: 28px;
      fill: white;
    }
    #mpia-iframe-container {
      position: fixed;
      bottom: 100px;
      right: 24px;
      width: 380px;
      height: 560px;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.22);
      overflow: hidden;
      z-index: 99998;
      display: none;
      border: none;
      background: white;
    }
    #mpia-iframe-container iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
    @media (max-width: 480px) {
      #mpia-iframe-container {
        width: calc(100vw - 16px);
        height: 70vh;
        right: 8px;
        bottom: 90px;
      }
    }
  `;
  document.head.appendChild(style);

  // ── BULLE ─────────────────────────────────────────────────
  const bubble = document.createElement("div");
  bubble.id = "mpia-bubble";
  bubble.title = "Discuter avec l'assistant du camping";
  bubble.innerHTML = `
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 12H6l-2 2V4h16v10z"/>
    </svg>
  `;

  // ── FENÊTRE IFRAME ────────────────────────────────────────
  const iframeContainer = document.createElement("div");
  iframeContainer.id = "mpia-iframe-container";

  const iframe = document.createElement("iframe");
  iframe.src = CHATBOT_URL;
  iframe.title = "Assistant Camping Les Eychecadous";
  iframe.allow = "microphone";
  iframeContainer.appendChild(iframe);

  // ── WRAPPER ───────────────────────────────────────────────
  const wrapper = document.createElement("div");
  wrapper.id = "mpia-widget-container";
  wrapper.appendChild(iframeContainer);
  wrapper.appendChild(bubble);
  document.body.appendChild(wrapper);

  // ── TOGGLE OUVERTURE / FERMETURE ─────────────────────────
  let isOpen = false;
  bubble.addEventListener("click", function () {
    isOpen = !isOpen;
    iframeContainer.style.display = isOpen ? "block" : "none";
    bubble.innerHTML = isOpen
      ? `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
           <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
         </svg>`
      : `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
           <path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 12H6l-2 2V4h16v10z"/>
         </svg>`;
  });
})();
