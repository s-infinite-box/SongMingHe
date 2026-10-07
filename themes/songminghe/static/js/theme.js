(() => {
  'use strict';
  const base = document.body.dataset.base;
  const playlist = JSON.parse(document.querySelector('#playlist-data').textContent);
  let pageEvents;
  let toastTimer;

  function readSetting(key, fallback) {
    try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; }
  }
  function saveSetting(key, value) {
    try { localStorage.setItem(key, value); } catch { /* 存储不可用时保留当前界面状态。 */ }
  }
  function toast(message) {
    const node = document.querySelector('#toast');
    node.textContent = message;
    node.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => node.classList.remove('visible'), 2200);
  }
  function setupPlayer() {
    const container = document.querySelector('#aplayer');
    const probe = document.createElement('audio');
    // 沿用 Reimu 的 APlayer 初始化方式，使用本地歌单并保持左侧栏位置。
    const player = new APlayer({
      container,
      theme: '#5968ad',
      fixed: false,
      autoplay: true,
      loop: 'all',
      order: 'list',
      preload: 'auto',
      volume: 0.75,
      mutex: true,
      listFolded: true,
      listMaxHeight: '160px',
      lrcType: 0,
      storageName: 'songminghe-aplayer-v1',
      audio: playlist.map(track => ({
        name: track.title,
        artist: track.artist,
        url: base + (track.sources.find(source => probe.canPlayType(source.type)) || track.sources[0]).src,
        cover: track.cover?.startsWith('img/') ? document.querySelector('.profile img').src : base + track.cover,
        theme: '#5968ad',
        type: 'normal'
      }))
    });
    // 通过播放器事件同步状态，供辅助功能和本地验收读取。
    function updateState() {
      container.dataset.playing = String(!player.audio.paused);
      container.dataset.playbackTime = String(player.audio.currentTime);
      container.dataset.volume = String(player.audio.volume);
      container.dataset.currentTrack = String(player.list.index);
      const play = container.querySelector('.aplayer-pic .aplayer-button');
      play?.setAttribute('aria-label', player.audio.paused ? '播放音乐' : '暂停音乐');
    }
    for (const event of ['play', 'pause', 'timeupdate', 'volumechange', 'listswitch', 'loadedmetadata']) player.on(event, updateState);
    const labels = {'.aplayer-icon-menu': '展开或收起歌单', '.aplayer-icon-order': '切换播放顺序', '.aplayer-icon-loop': '切换循环模式', '.aplayer-icon-volume-down': '切换静音', '.aplayer-icon-volume-up': '切换静音'};
    for (const [selector, label] of Object.entries(labels)) container.querySelector(selector)?.setAttribute('aria-label', label);
    const toggle = container.querySelector('.aplayer-pic .aplayer-button');
    toggle.setAttribute('role', 'button');
    toggle.tabIndex = 0;
    toggle.addEventListener('keydown', event => {
      if (!['Enter', ' '].includes(event.key)) return;
      event.preventDefault();
      player.toggle();
    });
    updateState();
  }
  function setMobileSidebar(open) {
    document.body.classList.toggle('mobile-sidebar-open', open);
    const toggle = document.querySelector('#sidebar-toggle');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? '收起侧栏' : '展开侧栏');
    toggle.querySelector('span').textContent = open ? '收起菜单' : '展开菜单';
  }
  function setupShell() {
    const backgroundPhotos = {'misty-lake': 'misty-lake.jpg', 'autumn-forest': 'autumn-forest.jpg', coast: 'coast.jpg'};
    const initialTheme = readSetting('blog-theme-v2', 'light');
    document.body.classList.toggle('dark', initialTheme === 'dark');
    const themeToggle = document.querySelector('#theme-toggle');
    themeToggle.setAttribute('aria-pressed', String(document.body.classList.contains('dark')));
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('dark');
      themeToggle.setAttribute('aria-pressed', String(document.body.classList.contains('dark')));
      saveSetting('blog-theme-v2', document.body.classList.contains('dark') ? 'dark' : 'light');
      const config = document.querySelector('#giscus-config');
      if (config) {
        const {lightTheme, darkTheme} = JSON.parse(config.textContent);
        document.querySelector('.giscus-frame')?.contentWindow.postMessage({giscus: {setConfig: {theme: document.body.classList.contains('dark') ? darkTheme : lightTheme}}}, 'https://giscus.app');
      }
    });
    const mobileLayout = matchMedia('(max-width: 720px)');
    document.querySelector('#sidebar-toggle').addEventListener('click', () => {
      const open = !document.body.classList.contains('mobile-sidebar-open');
      setMobileSidebar(open);
      // 从正文中打开菜单时，将新展开的侧栏带入视口。
      if (open) window.scrollTo({top: 0, behavior: 'instant'});
    });
    mobileLayout.addEventListener('change', () => setMobileSidebar(false));
    const backgroundToggle = document.querySelector('#background-toggle');
    const backgroundModes = ['coast', 'landscape', 'misty-lake', 'autumn-forest', 'solid'];
    const backgroundNames = {coast: '海岸浪花', landscape: '简约山景', 'misty-lake': '蓝调雾山', 'autumn-forest': '秋林倒影', solid: '纯色'};
    function updateBackground(mode) {
      document.body.dataset.background = mode;
      if (Object.hasOwn(backgroundPhotos, mode)) {
        document.body.dataset.photo = mode;
        document.body.style.setProperty('--background-photo', `url("${base}media/backgrounds/${backgroundPhotos[mode]}")`);
      } else {
        delete document.body.dataset.photo;
        document.body.style.removeProperty('--background-photo');
      }
      backgroundToggle.title = `当前背景：${backgroundNames[mode]}；点击切换下一张`;
    }
    // 使用新版本外观偏好，先前对比演示的选择不覆盖此次默认值。
    const initialBackground = readSetting('blog-background-v2', 'coast');
    updateBackground(backgroundModes.includes(initialBackground) ? initialBackground : 'coast');
    backgroundToggle.addEventListener('click', () => {
      const index = backgroundModes.indexOf(document.body.dataset.background);
      const mode = backgroundModes[(index + 1) % backgroundModes.length];
      updateBackground(mode);
      saveSetting('blog-background-v2', mode);
    });
    const sidebar = document.querySelector('#sidebar');
    function updateSidebarPosition() {
      // 过高的侧栏先自然滚动至底部再吸顶，保证所有入口可达。
      const top = Math.min(24, innerHeight - sidebar.offsetHeight - 24);
      sidebar.style.setProperty('--sidebar-top', `${top}px`);
    }
    new ResizeObserver(updateSidebarPosition).observe(sidebar);
    window.addEventListener('resize', updateSidebarPosition);
    updateSidebarPosition();
    for (const group of document.querySelectorAll('.sidebar-group')) {
      const preview = group.querySelector('.sidebar-preview');
      const items = [...preview.children];
      const more = group.querySelector('.sidebar-more');
      function updatePreview() {
        if (!group.open) return;
        // 先测量全部条目，再隐藏超出的整行，避免半行截断和不可见的键盘焦点。
        items.forEach(item => { item.hidden = false; });
        const limit = parseFloat(getComputedStyle(preview).maxHeight);
        const top = preview.getBoundingClientRect().top;
        const overflow = items.map(item => item.getBoundingClientRect().bottom - top > limit + 1);
        items.forEach((item, index) => { item.hidden = overflow[index]; });
        more.hidden = !overflow.some(Boolean);
      }
      group.addEventListener('toggle', updatePreview);
      let previousWidth = 0;
      new ResizeObserver(entries => {
        const width = entries[0].contentRect.width;
        if (width === previousWidth) return;
        previousWidth = width;
        updatePreview();
      }).observe(preview);
    }
    const started = new Date(document.body.dataset.started).getTime();
    document.querySelector('#site-age').textContent = `${Math.max(0, Math.floor((Date.now() - started) / 86400000))} 天`;
  }
  function setupSearch(signal) {
    const input = document.querySelector('#search-input');
    if (!input) return;
    const entries = JSON.parse(document.querySelector('#search-data').textContent);
    const index = new Map(entries.map(item => [item.url, item.text.toLowerCase()]));
    input.addEventListener('input', () => {
      const terms = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      let count = 0;
      document.querySelectorAll('#search-results .post-card').forEach(node => {
        node.hidden = !terms.every(term => index.get(node.dataset.articleUrl).includes(term));
        if (!node.hidden) count++;
      });
      document.querySelector('#search-count').textContent = `${count} 篇`;
      document.querySelector('#search-empty').hidden = count > 0;
    }, {signal});
  }
  function setupDirectory(signal) {
    const links = [...document.querySelectorAll('#sidebar-toc #TableOfContents a')];
    const headings = links.map(link => document.getElementById(decodeURIComponent(link.hash.slice(1))));
    const article = document.querySelector('.article-panel[data-current-article]');
    if (!article || !links.length) return;
    function update() {
      let active = 0;
      headings.forEach((heading, i) => { if (heading?.getBoundingClientRect().top <= 120) active = i; });
      links.forEach((link, i) => link.classList.toggle('active', i === active));
      const top = article.getBoundingClientRect().top + scrollY;
      const distance = Math.max(1, article.offsetHeight - innerHeight);
      const progress = Math.max(0, Math.min(100, (scrollY - top) / distance * 100));
      document.querySelector('#reading-percent').textContent = `${Math.round(progress)}%`;
      document.querySelector('#reading-progress').style.width = `${progress}%`;
    }
    window.addEventListener('scroll', update, {signal, passive: true});
    window.addEventListener('resize', update, {signal});
    update();
  }
  function loadComments() {
    const container = document.querySelector('#comments');
    const config = document.querySelector('#giscus-config');
    if (!container || !config || container.querySelector('script,.giscus-frame')) return;
    const script = document.createElement('script');
    script.src = 'https://giscus.app/client.js';
    script.async = true;
    script.crossOrigin = 'anonymous';
    const {lightTheme, darkTheme, ...values} = JSON.parse(config.textContent);
    values.theme = document.body.classList.contains('dark') ? darkTheme : lightTheme;
    for (const [key, value] of Object.entries(values)) script.setAttribute('data-' + key, value);
    container.append(script);
  }
  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    const input = document.createElement('textarea');
    input.value = text;
    document.body.append(input);
    input.select();
    const copied = document.execCommand('copy');
    input.remove();
    if (!copied) throw new Error('复制失败');
  }
  function setupArticle(signal) {
    document.querySelector('[data-article-back]')?.addEventListener('click', event => {
      // Swup 从 1 开始记录本站历史；直接打开文章时使用首页链接。
      if (history.state?.source !== 'swup' || !(history.state.index > 1)) return;
      event.preventDefault();
      history.back();
    }, {signal});
    document.querySelectorAll('.highlight').forEach(node => {
      const button = document.createElement('button');
      button.className = 'code-copy';
      button.textContent = '复制';
      node.append(button);
      button.addEventListener('click', () => {
        const code = node.querySelector('.lntd:last-child code') || node.querySelector('code');
        copyText(code?.textContent || '').then(() => toast('代码已复制')).catch(() => toast('复制失败'));
      }, {signal});
    });
    document.querySelector('[data-copy-markdown]')?.addEventListener('click', async event => {
      try {
        const response = await fetch(event.currentTarget.dataset.copyMarkdown);
        if (!response.ok) throw new Error('导出不可用');
        await copyText(await response.text());
        toast('Markdown 已复制');
      } catch { toast('复制失败'); }
    }, {signal});
    document.querySelector('.back-top')?.addEventListener('click', event => { event.preventDefault(); scrollTo({top: 0, behavior: 'smooth'}); }, {signal});
    document.querySelectorAll('.article-content img').forEach(image => image.addEventListener('click', () => {
      const dialog = document.createElement('dialog');
      dialog.className = 'image-dialog';
      const preview = image.cloneNode();
      const button = document.createElement('button');
      button.textContent = '×';
      button.setAttribute('aria-label', '关闭图片');
      dialog.append(preview, button);
      document.querySelector('#page-content').append(dialog);
      dialog.addEventListener('click', () => dialog.close());
      dialog.addEventListener('close', () => dialog.remove());
      dialog.showModal();
    }, {signal}));
  }
  function updatePageMetadata() {
    const metadata = JSON.parse(document.querySelector('#page-metadata').textContent);
    document.title = metadata.title;
    document.querySelector('link[rel="canonical"]').href = metadata.canonical;
    document.head.querySelectorAll('meta[data-page-meta]').forEach(node => node.remove());
    for (const entry of metadata.metas) {
      const node = document.createElement('meta');
      node.dataset.pageMeta = '';
      node.setAttribute(entry.attribute, entry.key);
      node.content = entry.content;
      document.head.append(node);
    }
  }
  function initializePage() {
    setMobileSidebar(false);
    pageEvents?.abort();
    pageEvents = new AbortController();
    const signal = pageEvents.signal;
    document.querySelectorAll('[data-nav]').forEach(node => {
      const active = node.dataset.nav === location.pathname;
      node.classList.toggle('active', active);
      if (active) node.setAttribute('aria-current', 'page'); else node.removeAttribute('aria-current');
    });
    updatePageMetadata();
    setupSearch(signal);
    setupDirectory(signal);
    setupArticle(signal);
    loadComments();
  }
  setupShell();
  setupPlayer();
  // 独立替换目录，避免切换文章时重建侧栏播放器。
  const swup = new Swup({containers: ['#page-content', '#sidebar-toc'], animationSelector: false, linkSelector: 'a[href]:not([target]):not([download]):not([data-no-swup])'});
  swup.hooks.on('content:replace', () => pageEvents?.abort(), {before: true});
  swup.hooks.on('page:view', initializePage);
  swup.hooks.on('fetch:error', () => toast('页面加载失败，请重试'));
  initializePage();
})();
