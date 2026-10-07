const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync('themes/songminghe/static/js/theme.js', 'utf8');
const search = source.slice(source.indexOf('  function setupSearch('), source.indexOf('  function setupDirectory('));

function page(url) {
  const entries = [{url:'/posts/a/',text:'Linux Rust 内核'}, {url:'/posts/b/',text:'Java 软件工程'}];
  const cards = entries.map(item => ({dataset:{articleUrl:item.url},hidden:false}));
  const location = {href:url};
  const history = {state:{source:'swup',index:2,random:0.5},calls:0,
    replaceState(state, title, path) { this.state=state; this.calls++; location.href=new URL(path,location.href).href; }
  };
  const input = {value:'',events:[],addEventListener(type, handler, {signal}) {
    const record={handler,active:true}; this.events.push(record);
    signal.addEventListener('abort',()=>{record.active=false;});
  }};
  const count = {}, empty = {};
  const context = {
    document:{querySelector(selector) {
      return {'#search-input':input,'#search-count':count,'#search-empty':empty,
        '#search-data':{textContent:JSON.stringify(entries)}}[selector];
    },querySelectorAll:()=>cards}, location,history,URL
  };
  vm.createContext(context);
  vm.runInContext(search,context);
  return {input,cards,count,empty,history,location,
    initialize() { const controller=new AbortController(); context.signal=controller.signal;vm.runInContext('setupSearch(signal)',context);return controller; },
    type(value) { input.value=value;input.events.filter(record=>record.active).forEach(record=>record.handler()); }
  };
}

test('直接打开查询链接时恢复关键词并筛选，支持大小写与多个词',()=>{
  const site=page('https://example.org/search/?q=linux+RUST'); site.initialize();
  assert.equal(site.input.value,'linux RUST');
  assert.equal(site.count.textContent,'1 篇');
  assert.equal(site.cards[0].hidden,false);assert.equal(site.cards[1].hidden,true);
  assert.equal(site.history.calls,0);
});

test('输入关键词更新当前历史，保留其他参数、锚点和 Swup 状态',()=>{
  const site=page('https://example.org/search/?view=all#results'); site.initialize();
  site.type('中文 & C++ #Rust');
  const url=new URL(site.location.href);
  assert.equal(url.searchParams.get('q'),'中文 & C++ #Rust');
  assert.equal(url.searchParams.get('view'),'all');assert.equal(url.hash,'#results');
  assert.equal(site.history.state.index,2);assert.equal(site.history.state.source,'swup');
  assert.equal(site.history.state.random,0.5);
  assert.equal(site.history.state.url,url.pathname+url.search+url.hash);
  assert.equal(site.count.textContent,'0 篇');assert.equal(site.empty.hidden,false);
});

test('清空搜索恢复全部结果并移除 q，保留其他参数',()=>{
  const site=page('https://example.org/search/?view=all&q=Linux');site.initialize();site.type('');
  const url=new URL(site.location.href);
  assert.equal(url.searchParams.has('q'),false);assert.equal(url.searchParams.get('view'),'all');
  assert.equal(site.count.textContent,'2 篇');assert.equal(site.empty.hidden,true);
});

test('离开页面解除旧监听器，返回和前进时按各自 URL 还原',()=>{
  const site=page('https://example.org/search/');let controller=site.initialize();site.type('Linux Rust');
  const saved=site.location.href;controller.abort();
  site.location.href=saved;controller=site.initialize();
  assert.equal(site.input.value,'Linux Rust');assert.equal(site.count.textContent,'1 篇');
  const before=site.history.calls;site.type('Java');assert.equal(site.history.calls,before+1);
  controller.abort();site.location.href=saved;site.initialize();
  assert.equal(site.input.value,'Linux Rust');assert.equal(site.count.textContent,'1 篇');
});
