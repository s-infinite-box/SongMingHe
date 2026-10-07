const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync('themes/songminghe/static/js/theme.js', 'utf8');
const directory = source.slice(source.indexOf('  function setupDirectory('), source.indexOf('  async function copyText('));

test('目录连续滚动和缩放每帧只测量一次，切页取消旧帧', () => {
  let measurements = 0;
  let nextFrame = 0;
  const callbacks = new Map();
  const listeners = {};
  const nodes = {'#reading-percent': {}, '#reading-progress': {style: {}}};
  const link = {hash: '#heading', classList: {toggle() {}}};
  const article = {offsetHeight: 2000, getBoundingClientRect: () => ({top: -500})};
  const controller = new AbortController();
  const context = {
    document: {
      querySelectorAll: () => [link],
      getElementById: () => ({getBoundingClientRect() { measurements++; return {top: 50}; }}),
      querySelector: key => key.startsWith('.article-panel') ? article : nodes[key]
    },
    window: {addEventListener: (event, fn) => { listeners[event] = fn; }},
    requestAnimationFrame(fn) { callbacks.set(++nextFrame, fn); return nextFrame; },
    cancelAnimationFrame(id) { callbacks.delete(id); }, scrollY: 500, innerHeight: 800,
    signal: controller.signal
  };
  vm.runInNewContext(directory + '\nsetupDirectory(signal);', context);
  assert.equal(measurements, 1);
  for (let i = 0; i < 20; i++) { listeners.scroll(); listeners.resize(); }
  assert.equal(callbacks.size, 1);
  const [id, callback] = callbacks.entries().next().value;
  callbacks.delete(id);
  callback();
  assert.equal(measurements, 2);
  assert.equal(nodes['#reading-percent'].textContent, '42%');
  listeners.scroll();
  controller.abort();
  assert.equal(callbacks.size, 0);
  assert.equal(measurements, 2);
});
