"""用实际 Hugo 构建核验发布时间、系列顺序及资源版本。"""
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse

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
            'theme: songminghe\ntaxonomies:\n  series: series\nparams:\n  favicon: favicon.svg\n')
        layouts = cls.source / 'themes/songminghe/layouts'
        (layouts / '_partials').mkdir(parents=True)
        for name in ['list.html', '_partials/head.html']:
            shutil.copyfile(REPO / 'themes/songminghe/layouts' / name, layouts / name)
        (layouts / 'baseof.html').write_text('<html><head>{{ partial "head.html" . }}</head><body>{{ block "main" . }}{{ end }}</body></html>')
        (layouts / 'home.html').write_text('{{ define "main" }}首页{{ end }}')
        (layouts / 'page.html').write_text('{{ define "main" }}{{ .Content }}{{ end }}')
        (layouts / '_partials/card.html').write_text('<a href="{{ .page.RelPermalink }}">{{ .page.Title }}</a>')
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
        }
        for slug, matter in fixtures.items():
            bundle = cls.source / 'content/posts' / slug
            bundle.mkdir(parents=True)
            (bundle / 'index.md').write_text(f'---\ntitle: {slug}\n{matter}\n---\n\n测试正文。\n')
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
                    'series-one', 'series-two', 'series-unordered'}
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
