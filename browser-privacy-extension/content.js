(() => {
  const PATTERNS = [
    /\blog ?in\b/i,
    /\bsign ?in\b/i,
    /\bsign ?up\b/i,
    /\bregister\b/i,
    /\bauth(?:entication)?\b/i,
    /\bpassword\b/i,
    /\bverification\b/i,
    /\blogin\b/i,
  ];

  const STATE_CLASS = 'zenshare-sensitive-page';

  function isSensitivePage() {
    const title = document.title || '';
    const href = window.location.href || '';
    const bodyText = document.body ? (document.body.innerText || '').slice(0, 2000) : '';
    const haystack = `${title}\n${href}\n${bodyText}`;
    return PATTERNS.some((pattern) => pattern.test(haystack));
  }

  function updateProtection() {
    if (isSensitivePage()) {
      document.documentElement.classList.add(STATE_CLASS);
      return;
    }
    document.documentElement.classList.remove(STATE_CLASS);
  }

  const observer = new MutationObserver(() => updateProtection());
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
    characterData: true,
  });

  updateProtection();
  window.setInterval(updateProtection, 1500);
})();