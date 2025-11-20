let dockButton;

const BRAND = '#00AFD7';
const WHITE = '#ffffff';

const MESSAGES_SQUARE_SVG = `
<svg xmlns="http://www.w3.org/2000/svg"
     width="24" height="24" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round"
     aria-hidden="true" focusable="false">
  <path d="M16 10a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 14.286V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
  <path d="M20 9a2 2 0 0 1 2 2v10.286a.71.71 0 0 1-1.212.502l-2.202-2.202A2 2 0 0 0 17.172 19H10a2 2 0 0 1-2-2v-1"/>
</svg>`;

function styleDockButton(btn) {
  btn.setAttribute('aria-label', 'Chat öffnen');
  btn.style.width = '56px';
  btn.style.height = '56px';
  btn.style.minWidth = '0';
  btn.style.minHeight = '0';
  btn.style.aspectRatio = '1 / 1';
  btn.style.padding = '0';
  btn.style.margin = '0';
  btn.style.lineHeight = '0';
  btn.style.boxSizing = 'border-box';
  btn.style.cursor = 'pointer';
  btn.style.position = 'fixed';
  btn.style.bottom = '20px';
  btn.style.right = '20px';
  btn.style.zIndex = '10000';
  btn.style.background = WHITE;
  btn.style.border = `2px solid ${BRAND}`;
  btn.style.borderRadius = '50%';
  btn.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
  btn.style.display = 'grid';
  btn.style.placeItems = 'center';
  btn.style.transition = 'background 0.2s ease, transform 0.2s ease, color 0.2s ease';
  btn.style.color = BRAND;
}

function createDockButton(onClick) {
  if (dockButton) return dockButton;
  dockButton = document.createElement('button');
  styleDockButton(dockButton);
  dockButton.innerHTML = MESSAGES_SQUARE_SVG;
  dockButton.addEventListener('mouseenter', () => {
    dockButton.style.background = BRAND;
    dockButton.style.color = WHITE;
    dockButton.style.transform = 'translateY(-2px)';
  });
  dockButton.addEventListener('mouseleave', () => {
    dockButton.style.background = WHITE;
    dockButton.style.color = BRAND;
    dockButton.style.transform = 'translateY(0)';
  });
  dockButton.onclick = onClick;
  return dockButton;
}

function programFromPath() {
  const path = window.location.pathname.toLowerCase();
  if (path.includes('/btb')) return 'BTB';
  if (path.includes('/bmt')) return 'BMT';
  if (path.includes('/mmi')) return 'MMI';
  if (path.includes('/bdaisy')) return 'BDAISY';
  if (path.includes('/bcsim')) return 'BCSIM';
  if (path.includes('/mar')) return 'MAR';
  if (path.includes('/bmi')) return 'BMI';
  return 'default';
}

function openLightbox(url) {
  const overlay = document.createElement('div');
  overlay.style.position = 'fixed';
  overlay.style.backgroundColor = '#fff';
  overlay.style.zIndex = '9999';
  overlay.style.borderRadius = '8px';
  overlay.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
  overlay.style.transition = 'all 0.3s ease';
  overlay.id = 'lightbox-overlay';

  const updateOverlaySize = () => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
      overlay.style.top = '0';
      overlay.style.left = '0';
      overlay.style.right = '0';
      overlay.style.width = '100%';
      overlay.style.height = '100%';
      overlay.style.borderRadius = '0';
    } else {
      overlay.style.top = '10%';
      overlay.style.right = '20px';
      overlay.style.left = '';
      overlay.style.width = '28%';
      overlay.style.height = '80%';
      overlay.style.borderRadius = '8px';
    }
  };
  updateOverlaySize();
  window.addEventListener('resize', updateOverlaySize);

  const iframe = document.createElement('iframe');
  iframe.src = url;
  iframe.style.width = '100%';
  iframe.style.height = '100%';
  iframe.style.border = 'none';
  iframe.style.borderRadius = '8px';
  overlay.appendChild(iframe);

  document.body.appendChild(overlay);
  if (dockButton) dockButton.style.display = 'none';

  let minimized = false;

  const restoreChatbot = () => {
    if (!minimized) return;
    minimized = false;
    overlay.style.display = 'block';
    if (dockButton) dockButton.style.display = 'none';
    try { iframe.contentWindow?.postMessage({ type: 'restored' }, '*'); } catch {}
  };

  const minimizeChatbot = () => {
    if (minimized) return;
    minimized = true;
    overlay.style.display = 'none';
    if (dockButton) {
      dockButton.style.display = 'grid';
      dockButton.onclick = restoreChatbot;
    }
  };

  const closeChatbot = () => {
    if (document.body.contains(overlay)) document.body.removeChild(overlay);
    window.removeEventListener('resize', updateOverlaySize);
    minimized = false;
    if (dockButton) {
      dockButton.style.display = 'grid';
      dockButton.onclick = defaultOpenHandler;
    }
  };

  const messageHandler = (event) => {
    if (!event.data || typeof event.data !== 'object') return;
    if (event.data.type === 'close') closeChatbot();
    else if (event.data.type === 'minimize') minimizeChatbot();
    else if (event.data.type === 'restore') restoreChatbot();
  };
  window.addEventListener('message', messageHandler);

  const cleanupObserver = new MutationObserver(() => {
    if (!document.body.contains(overlay)) {
      window.removeEventListener('message', messageHandler);
      cleanupObserver.disconnect();
    }
  });
  cleanupObserver.observe(document.body, { childList: true });

  const sendProgram = () => {
    const program = programFromPath();
    iframe?.contentWindow?.postMessage({ program }, '*');
  };
  iframe.addEventListener('load', sendProgram);
  setTimeout(sendProgram, 700);
}

function defaultOpenHandler() {
  openLightbox('https://marmann.hosting.medien.hs-duesseldorf.de/2026-FBM-Web-KI-Chatbot/');
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = createDockButton(defaultOpenHandler);
  document.body.appendChild(btn);
  btn.style.display = 'grid';
});
