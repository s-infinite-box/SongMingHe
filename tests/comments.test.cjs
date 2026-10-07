const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync('themes/songminghe/static/js/comments.js', 'utf8');

function browser({url = 'https://example.org/posts/a/', saved, blocked = false} = {}) {
  const listeners = [];
  const storage = new Map(saved ? [['giscus-session', saved]] : []);
  const location = {href: url};
  let currentPath = 'a';
  let dark = false;
  let container;
  const state = {source: 'swup', index: 2};
  const document = {
    body: {classList: {contains: () => dark}},
    querySelector(selector) {
      if (selector === '#comments') return container;
      if (selector === '#giscus-config') return currentPath && {textContent: JSON.stringify({
        repo: 'owner/blog', 'repo-id': 'repo-id', category: 'Announcements', 'category-id': 'category-id',
        term: `SongMingHe/posts/${currentPath}/`, strict: '0', 'reactions-enabled': '1',
        'emit-metadata': '0', 'input-position': 'bottom', lang: 'zh-CN', loading: 'eager',
        lightTheme: 'light', darkTheme: 'dark'
      })};
      return {content: '测试文章简介'};
    },
    createElement(tag) {
      assert.equal(tag, 'iframe');
      const frame = {style: {}, messages: [], events: {}, removed: false,
        setAttribute() {}, addEventListener(type, fn) { this.events[type] = fn; },
        remove() { this.removed = true; }, classList: {remove() {}},
      };
      frame.contentWindow = {postMessage: (message, origin) => frame.messages.push({message, origin})};
      return frame;
    }
  };
  const window = {addEventListener: (type, fn) => { assert.equal(type, 'message'); listeners.push(fn); }};
  const localStorage = {
    getItem(key) { if (blocked) throw Error('存储被禁用'); return storage.get(key) ?? null; },
    setItem(key, value) { if (blocked) throw Error('存储被禁用'); storage.set(key, value); },
    removeItem(key) { if (blocked) throw Error('存储被禁用'); storage.delete(key); }
  };
  const history = {state, replaceState(value, title, href) { this.state = value; location.href = href; }};
  vm.runInNewContext(source, {window, document, location, localStorage, history, URL, URLSearchParams});
  return {
    storage, history, location, listeners, comments: window.blogComments,
    visit(path) {
      currentPath = path;
      location.href = `https://example.org/${path ? `posts/${path}/` : ''}`;
      let created;
      container = path && {append: node => { created = node; }};
      window.blogComments.load();
      return created;
    },
    message(frame, value, origin = 'https://giscus.app') { listeners[0]({source: frame.contentWindow, origin, data: {giscus: value}}); },
    dark() { dark = true; window.blogComments.updateTheme(); }
  };
}

test('慢加载 A→B：旧框及迟到消息不能改变 B 的讨论和登录状态', () => {
  const site = browser({saved: '"test-session"'});
  const a = site.visit('a');
  const b = site.visit('b');
  assert.equal(a.removed, true);
  site.message(a, {resizeHeight: 900, signOut: true});
  a.events.load();
  assert.equal(b.style.height, undefined);
  assert.equal(site.storage.has('giscus-session'), true);
  const params = new URL(b.src).searchParams;
  assert.equal(params.get('term'), 'SongMingHe/posts/b/');
  assert.equal(params.get('origin'), 'https://example.org/posts/b/#comments');
  assert.equal(params.get('backLink'), 'https://example.org/posts/b/');
  assert.equal(b.loading, 'eager');
  assert.equal(b.messages.length, 0);
});

test('连续切页只保留一个消息监听器，无评论页面移除旧框', () => {
  const site = browser();
  let previous;
  for (let i = 0; i < 30; i++) {
    const frame = site.visit(String(i));
    if (previous) assert.equal(previous.removed, true);
    previous = frame;
  }
  assert.equal(site.listeners.length, 1);
  assert.equal(site.visit(null), undefined);
  assert.equal(previous.removed, true);
  site.message(previous, {resizeHeight: 900});
});

test('当前消息调整高度，其他域名被忽略，加载期间切换配色使用最新主题', () => {
  const site = browser();
  const frame = site.visit('a');
  site.message(frame, {resizeHeight: 600}, 'https://other.example');
  assert.equal(frame.style.height, undefined);
  site.message(frame, {resizeHeight: 600});
  assert.equal(frame.style.height, '600px');
  site.dark();
  frame.events.load();
  assert.equal(frame.messages.at(-1).message.giscus.setConfig.theme, 'dark');
});

test('登录返回清除 URL 会话参数，保留原查询、锚点和 Swup 历史', () => {
  const site = browser({url: 'https://example.org/posts/a/?q=1&giscus=test-session#comments'});
  assert.equal(site.location.href, 'https://example.org/posts/a/?q=1#comments');
  assert.equal(site.storage.get('giscus-session'), '"test-session"');
  assert.equal(site.history.state.index, 2);
  const frame = site.visit('b');
  assert.equal(new URL(frame.src).searchParams.get('session'), 'test-session');
});

for (const message of [{signOut: true}, {error: 'Bad credentials'}, {error: 'Invalid state value'}, {error: 'State has expired'}]) {
  test(`退出或会话失效后在当前文章恢复匿名评论：${JSON.stringify(message)}`, () => {
    const site = browser({saved: '"test-session"'});
    site.visit('a');
    const b = site.visit('b');
    site.message(b, message);
    assert.equal(site.storage.has('giscus-session'), false);
    const params = new URL(b.src).searchParams;
    assert.equal(params.has('session'), false);
    assert.equal(params.get('origin'), 'https://example.org/posts/b/#comments');
    assert.equal(params.get('term'), 'SongMingHe/posts/b/');
  });
}

test('存储禁用或损坏不会阻断评论自动加载', () => {
  for (const options of [{blocked: true}, {saved: '{bad json'}, {saved: '123'}]) {
    const site = browser(options);
    const frame = site.visit('a');
    assert.equal(new URL(frame.src).searchParams.get('session'), '');
  }
});
