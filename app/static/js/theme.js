// Theme preference handling: system / light / dark
(function() {
  const STORAGE_KEY = 'theme-preference';
  const docEl = document.documentElement;
  const metaTheme = document.querySelector('meta[name="theme-color"]');
  const media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function getPreference() {
    try {
      return localStorage.getItem(STORAGE_KEY) || 'system';
    } catch (_) {
      return 'system';
    }
  }

  function setPreference(value) {
    try { localStorage.setItem(STORAGE_KEY, value); } catch(_) {}
  }

  function computeIsDark(pref) {
    if (pref === 'dark') return true;
    if (pref === 'light') return false;
    return media ? media.matches : false;
  }

  function applyTheme(pref) {
    const isDark = computeIsDark(pref);
    docEl.setAttribute('data-theme', isDark ? 'dark' : 'light');
    // Update meta theme color from CSS var if available
    try {
      const themeColor = getCSSVar('--theme-color');
      if (metaTheme && themeColor) metaTheme.setAttribute('content', themeColor);
    } catch(_) {}
    updateUI(pref);
  }

  function getCSSVar(name) {
    return String(getComputedStyle(docEl).getPropertyValue(name) || '').trim();
  }

  function updateUI(pref) {
    const toggle = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-toggle-icon');
    const menu = document.getElementById('theme-menu');
    if (!toggle || !icon || !menu) return;

    // Set icon by effective theme or pref
    const isDark = computeIsDark(pref);
    icon.textContent = pref === 'system' ? '💻' : (isDark ? '🌙' : '☀️');

    // Mark checked item and ensure no disabled state leaks in
    menu.querySelectorAll('.theme-option').forEach(btn => {
      const checked = btn.getAttribute('data-theme') === pref;
      btn.setAttribute('aria-checked', checked ? 'true' : 'false');
      try { btn.disabled = false; } catch(_) {}
    });
  }

  function initUI() {
    const toggle = document.getElementById('theme-toggle');
    const menu = document.getElementById('theme-menu');
    if (!toggle || !menu) return;

    function closeMenu() {
      menu.hidden = true;
      toggle.setAttribute('aria-expanded', 'false');
    }
    function openMenu() {
      menu.hidden = false;
      toggle.setAttribute('aria-expanded', 'true');
    }

    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      if (menu.hidden) openMenu(); else closeMenu();
    });

    // Click away to close
    document.addEventListener('click', (e) => {
      if (menu.hidden) return;
      // Ignore clicks on the toggle or any of its children
      if (toggle.contains(e.target)) return;
      // Ignore clicks inside the menu
      if (menu.contains(e.target)) return;
      closeMenu();
    });

    // Keyboard escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeMenu();
    });

    menu.addEventListener('click', (e) => {
      const target = e.target.closest('.theme-option');
      if (!target) return;
      const pref = target.getAttribute('data-theme');
      setPreference(pref);
      applyTheme(pref);
      closeMenu();
    });
  }

  // Initialize
  const pref = getPreference();
  applyTheme(pref);
  initUI();

  // React to system changes when in system mode
  if (media && media.addEventListener) {
    media.addEventListener('change', () => {
      if (getPreference() === 'system') applyTheme('system');
    });
  } else if (media && media.addListener) {
    media.addListener(() => {
      if (getPreference() === 'system') applyTheme('system');
    });
  }
})();
