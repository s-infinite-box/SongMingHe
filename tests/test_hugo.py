"""用实际 Hugo 构建核验发布时间、系列顺序及资源版本。"""
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, unquote, urlparse
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verify_build', REPO / 'scripts/verify-build.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class HugoRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ.get('TEST_TMPDIR', REPO.parents[1] / '.tmp/blog-theme-review-fixes'))
        root.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix='hugo-regression-', dir=root)
        cls.root = Path(cls.temporary.name)
        cls.env = dict(os.environ, HUGO_CACHEDIR=str(cls.root / 'cache'), HUGO_ENVIRONMENT='production')
        cls.hugo = os.environ.get('HUGO', 'hugo')
        cls.source = cls.root / 'source'
        cls.source.mkdir()
        (cls.source / 'hugo.yaml').write_text(
            'baseURL: https://example.org/\ntimeZone: Asia/Shanghai\ntitle: 测试博客\n'
            'theme: songminghe\ntaxonomies:\n  series: series\n  category: categories\n  tag: tags\n'
            'params:\n  favicon: favicon.svg\n  rssFullContent: true\n')
        layouts = cls.source / 'themes/songminghe/layouts'
        (layouts / '_partials').mkdir(parents=True)
        for name in ['list.html', 'page.html', 'search.html', 'search.json', 'rss.xml', '_partials/head.html',
                     '_partials/rss-content.html', '_partials/cover.html', '_markup/render-link.html']:
            (layouts / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / 'themes/songminghe/layouts' / name, layouts / name)
        (layouts / 'baseof.html').write_text('<html><head>{{ partial "head.html" . }}</head><body>{{ block "main" . }}{{ end }}</body></html>')
        (layouts / 'home.html').write_text('{{ define "main" }}首页{{ end }}')
        (layouts / '_partials/card.html').write_text('<a href="{{ .page.RelPermalink }}">{{ .page.Title }}</a>')
        (layouts / '_partials/icon.html').write_text('<svg></svg>')
        (layouts / '_partials/metadata.html').write_text('{{ return (dict "title" .Title "canonical" .Permalink "metas" slice) }}')
        assets = cls.source / 'assets'
        assets.mkdir()
        (assets / 'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        static = cls.source / 'themes/songminghe/static'
        for folder in ['css', 'js', 'vendor/aplayer']:
            shutil.copytree(REPO / 'themes/songminghe/static' / folder, static / folder)
        fixtures = {
            'same-day-future': 'date: 2026-10-08T23:59:00+08:00',
            'published': 'date: 2026-10-07T10:00:00+08:00',
            'publish-future': 'date: 2026-10-07T10:00:00+08:00\npublishDate: 2026-10-08T23:59:00+08:00',
            'publish-past': 'date: 2026-10-09T10:00:00+08:00\npublishDate: 2026-10-07T10:00:00+08:00',
            'zone-future': 'date: 2026-10-07T17:30:00Z',
            'zone-past': 'date: 2026-10-07T16:30:00Z',
            'date-only': 'date: 2026-10-08',
            'draft': 'date: 2026-10-07T10:00:00+08:00\ndraft: true',
            'expired': 'date: 2026-10-07T10:00:00+08:00\nexpiryDate: 2026-10-07T23:59:00+08:00',
            'series-two': 'date: 2026-10-07T10:00:00+08:00\nseries: [test]\nseries_order: 2',
            'series-one': 'date: 2026-10-06T10:00:00+08:00\nseries: [test]\nseries_order: 1',
            'series-unordered': 'date: 2026-10-07T11:00:00+08:00\nseries: [test]',
            'missing-both': 'date: 2026-10-07T10:00:00+08:00',
            'missing-categories': 'date: 2026-10-07T10:00:00+08:00\ntags: [test]',
            'missing-tags': 'date: 2026-10-07T10:00:00+08:00\ncategories: [test]',
            'empty-taxonomies': 'date: 2026-10-07T10:00:00+08:00\ntags: []\ncategories: []',
        }
        for slug, matter in fixtures.items():
            bundle = cls.source / 'content/posts' / slug
            bundle.mkdir(parents=True)
            (bundle / 'index.md').write_text(f'---\ntitle: {slug}\n{matter}\n---\n\n测试正文。\n')
        links = cls.source / 'content/posts/published/index.md'
        links.write_text(links.read_text() + '\n## 目标标题\n\n[内部锚点](#目标标题)\n\n'
                         '[相邻文章](../series-one/)\n\n[根路径](/posts/series-two/)\n\n'
                         '[查询](?q=x&lang=zh)\n\n[价格](../series-one/?price=$1&lang=zh)\n\n'
                         '[外链](https://outside.example/a)\n\n[协议相对](//cdn.example/a)\n\n'
                         '[邮箱](mailto:test@example.org)\n\n![相对配图](./pic.svg)\n\n'
                         '![根路径配图](/shared.svg)\n\n```html\n<a href="../code-example/">代码示例</a>\n```\n')
        search = cls.source / 'content/search'
        search.mkdir()
        (search / '_index.md').write_text('---\ntitle: 搜索\nlayout: search\noutputs: [HTML, JSON]\n---\n')
        cls.output = cls.root / 'public'
        cls.build()
        listed = cls.run_hugo('list', 'published')
        cls.manifest = cls.root / 'published.csv'
        cls.manifest.write_text(listed)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    @classmethod
    def run_hugo(cls, *arguments):
        return subprocess.run([cls.hugo, *arguments, '--source', str(cls.source),
                               '--clock', '2026-10-08T01:00:00+08:00'],
                              check=True, text=True, capture_output=True, env=cls.env).stdout

    @classmethod
    def build(cls):
        cls.run_hugo('--destination', str(cls.output), '--cleanDestinationDir', '--quiet')

    def test_publication_matches_actual_build(self):
        expected = {'published', 'publish-past', 'zone-past', 'date-only',
                    'series-one', 'series-two', 'series-unordered', 'missing-both',
                    'missing-categories', 'missing-tags', 'empty-taxonomies'}
        rows = verify.published_posts(self.manifest)
        selected = {Path(row['path']).parent.name for row in rows}
        self.assertEqual(selected, expected)
        rendered = {p.parent.name for p in (self.output / 'posts').glob('*/index.html')}
        self.assertEqual(rendered, selected)

    def test_series_order_precedes_date(self):
        text = (self.output / 'series/test/index.html').read_text()
        titles = ['series-one', 'series-two', 'series-unordered']
        positions = [text.index(f'>{title}</a>') for title in titles]
        self.assertEqual(positions, sorted(positions))
        ordinary = (self.output / 'posts/index.html').read_text()
        self.assertLess(ordinary.index('>series-two</a>'), ordinary.index('>series-one</a>'))

    def test_resource_versions_change_with_content(self):
        def version():
            page = verify.Page((self.output / 'index.html').read_text())
            url = next(url for _, url in page.links if urlparse(url).path == '/css/theme.css')
            return parse_qs(urlparse(url).query)['v'][0]

        css = self.source / 'themes/songminghe/static/css/theme.css'
        original = css.read_bytes()
        self.assertEqual(version(), hashlib.sha256(original).hexdigest())
        css.write_bytes(original + b'\n.test { color: red; }\n')
        self.build()
        self.assertNotEqual(version(), hashlib.sha256(original).hexdigest())
        self.assertEqual(version(), hashlib.sha256(css.read_bytes()).hexdigest())

    def test_optional_taxonomies_build_search_and_feeds(self):
        text = (self.output / 'search/index.html').read_text()
        content = re.search(r'<script[^>]*id="search-data"[^>]*>(.*?)</script>', text, re.S).group(1)
        entries = json.loads(content)
        urls = {entry['url'] for entry in entries}
        exported = json.loads((self.output / 'search/index.json').read_text())
        subscribed = {item.findtext('link') for item in ET.parse(self.output / 'index.xml').findall('./channel/item')}
        cases = {'missing-both': (False, False), 'missing-categories': (False, True),
                 'missing-tags': (True, False), 'empty-taxonomies': (False, False)}
        for slug in ['missing-both', 'missing-categories', 'missing-tags', 'empty-taxonomies']:
            self.assertIn(f'/posts/{slug}/', urls)
            self.assertTrue(any(entry['permalink'] == f'/posts/{slug}/' for entry in exported))
            self.assertIn(f'https://example.org/posts/{slug}/', subscribed)
            article = verify.Page((self.output / f'posts/{slug}/index.html').read_text())
            self.assertEqual(tuple(article.taxonomies.values()), cases[slug])
            for name, present in article.taxonomies.items():
                feed = ET.parse(self.output / f'{name}/index.xml').findall('./channel/item')
                self.assertEqual(any(item.findtext('link') == f'https://example.org/posts/{slug}/' for item in feed), present)
        sidebar_only = verify.Page('<aside><a href="/categories/test/">分类</a><a href="/tags/test/">标签</a></aside>')
        self.assertFalse(any(sidebar_only.taxonomies.values()))

    def test_rss_xml_valid_with_and_without_minification(self):
        for flags in [[], ['--minify']]:
            with self.subTest(flags=flags):
                self.run_hugo('--destination', str(self.output), '--cleanDestinationDir', '--quiet', *flags)
                feeds = list(self.output.rglob('*.xml'))
                self.assertGreater(len(feeds), 1)
                for feed in feeds:
                    self.assertTrue(feed.read_bytes().startswith(b'<?xml'), str(feed))
                    ET.parse(feed)

    def test_rss_resolves_article_links_and_images(self):
        item = next(item for item in ET.parse(self.output / 'index.xml').findall('./channel/item')
                    if item.findtext('title') == 'published')
        html = item.findtext('description')
        links = {unquote(url) for _, url in verify.Page(html).links}
        expected = {'https://example.org/posts/published/#目标标题',
                    'https://example.org/posts/series-one/', 'https://example.org/posts/series-two/',
                    'https://example.org/posts/published/?q=x&lang=zh',
                    'https://example.org/posts/series-one/?price=$1&lang=zh',
                    'https://outside.example/a', 'https://cdn.example/a', 'mailto:test@example.org',
                    'https://example.org/posts/published/pic.svg', 'https://example.org/shared.svg'}
        self.assertLessEqual(expected, links)
        self.assertIn('<a href="../code-example/">代码示例</a>', verify.Page(html).text)
