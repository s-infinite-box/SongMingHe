// 按 giscus 官方 iframe 协议管理评论，避免异步客户端在切页后覆盖新文章。
(() => {
  'use strict';
  const origin = 'https://giscus.app';
  const sessionKey = 'giscus-session';
  let frame;
  let config;

  function clearSession() {
    try { localStorage.removeItem(sessionKey); } catch { /* 存储不可用时仍可匿名评论。 */ }
  }
  function readSession() {
    const url = new URL(location.href);
    const returned = url.searchParams.get('giscus');
    if (returned) {
      try { localStorage.setItem(sessionKey, JSON.stringify(returned)); } catch { /* 本次登录仍然有效。 */ }
      url.searchParams.delete('giscus');
      history.replaceState(history.state, '', url.href);
      return returned;
    }
    try {
      const value = JSON.parse(localStorage.getItem(sessionKey) || '""');
      if (typeof value === 'string') return value;
    } catch { /* 无效会话按未登录处理。 */ }
    clearSession();
    return '';
  }
  let session = readSession();

  function updateTheme() {
    if (!frame) return;
    const theme = document.body.classList.contains('dark') ? config.darkTheme : config.lightTheme;
    frame.contentWindow?.postMessage({giscus: {setConfig: {theme}}}, origin);
  }
  function dispose() {
    frame?.remove();
    frame = undefined;
    config = undefined;
  }
  function load() {
    dispose();
    const container = document.querySelector('#comments');
    const data = document.querySelector('#giscus-config');
    if (!container || !data) return;
    config = JSON.parse(data.textContent);
    const page = new URL(location.href);
    page.hash = '';
    const params = new URLSearchParams({
      origin: page.href + '#comments', backLink: page.href, session,
      repo: config.repo, repoId: config['repo-id'],
      category: config.category, categoryId: config['category-id'],
      term: config.term, strict: config.strict,
      reactionsEnabled: config['reactions-enabled'], emitMetadata: config['emit-metadata'],
      inputPosition: config['input-position'],
      theme: document.body.classList.contains('dark') ? config.darkTheme : config.lightTheme,
      description: document.querySelector('meta[name="description"]')?.content || ''
    });
    const current = document.createElement('iframe');
    current.className = 'giscus-frame giscus-frame--loading';
    current.title = '文章评论';
    current.setAttribute('allow', 'clipboard-write');
    current.setAttribute('scrolling', 'no');
    current.loading = config.loading === 'lazy' ? 'lazy' : 'eager';
    current.src = `${origin}/${config.lang}/widget?${params}`;
    current.addEventListener('load', () => {
      if (frame !== current) return;
      current.classList.remove('giscus-frame--loading');
      // 下载过程中可能切换明暗模式，加载完成后使用最新配色。
      updateTheme();
    });
    frame = current;
    container.append(current);
  }
  window.addEventListener('message', event => {
    // 旧文章即使迟到，也不能调整当前评论框或清除当前登录状态。
    if (!frame || event.origin !== origin || event.source !== frame.contentWindow) return;
    const message = event.data?.giscus;
    if (!message || typeof message !== 'object') return;
    const height = Number(message.resizeHeight);
    if (Number.isFinite(height) && height > 0) frame.style.height = `${height}px`;
    const expired = /Bad credentials|Invalid state value|State has expired/.test(message.error || '');
    if (!message.signOut && !(expired && session)) return;
    session = '';
    clearSession();
    const url = new URL(frame.src);
    url.searchParams.delete('session');
    frame.src = url.href;
  });
  window.blogComments = {load, dispose, updateTheme};
})();
