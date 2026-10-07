#!/usr/bin/env python3
"""核验正式构建的文章、导出、订阅、搜索、旧链接和本地资源，仅使用标准库。"""
import argparse
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.metas = {}
        self.navigation = []
        self.refresh = None
        self.metadata = ''
        self.in_metadata = False
        self.in_giscus = False
        self.giscus = ''
        self.article_depth = 0
        self.article_text = ''
        self.text = ''
        self.feed_nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append((tag, attrs[key]))
        if tag == 'meta':
            key = attrs.get('property') or attrs.get('name')
            if key:
                self.metas[key] = attrs.get('content', '')
            if attrs.get('http-equiv', '').lower() == 'refresh':
                self.refresh = attrs.get('content', '')
        if tag == 'a' and 'data-nav' in attrs:
            self.navigation.append(attrs['href'])
        if tag == 'script':
            self.in_metadata = attrs.get('id') == 'page-metadata'
            self.in_giscus = attrs.get('id') == 'giscus-config'
        if tag == 'div':
            if self.article_depth:
                self.article_depth += 1
            elif 'article-content' in attrs.get('class', '').split():
                self.article_depth = 1
        if tag == 'link' and attrs.get('type') == 'application/rss+xml':
            self.feed_nodes.append(attrs.get('href'))

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_metadata = False
            self.in_giscus = False
        if tag == 'div' and self.article_depth:
            self.article_depth -= 1

    def handle_data(self, data):
        self.text += data
        if self.in_metadata:
            self.metadata += data
        if self.in_giscus:
            self.giscus += data
        if self.article_depth:
            self.article_text += data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', default='public', help='构建产物目录')
    parser.add_argument('--baseline', help='可选：迁移前构建目录，用于比较 Markdown 内容')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    base = re.search(r'^baseURL:\s*(\S+)', (repo / 'hugo.yaml').read_text(), re.M).group(1)
    base_url = urlparse(base)
    base_path = base_url.path
    errors = []
    checked = set()
    html_pages = {str(p.relative_to(output)): Page(p.read_text()) for p in output.rglob('*.html')}

    def check(condition, message):
        if not condition:
            errors.append(message)

    def local_target(url, origin):
        parsed = urlparse(urljoin(origin, url))
        if parsed.scheme not in ('http', 'https') or parsed.netloc != base_url.netloc:
            return None
        path = unquote(parsed.path)
        if not path.startswith(base_path):
            errors.append(f'地址缺少博客子路径：{url}，来源 {origin}')
            return None
        relative = path[len(base_path):]
        target = output / relative
        if target.is_dir() or path.endswith('/'):
            target /= 'index.html'
        checked.add(str(target))
        check(target.is_file(), f'本站链接或资源不存在：{url}，来源 {origin}')
        return target, unquote(parsed.fragment)

    for relative, page in html_pages.items():
        origin = urljoin(base, relative)
        for tag, url in page.links:
            target = local_target(url, origin)
            if tag == 'a' and target and target[1] and target[0].suffix == '.html':
                target_page = html_pages.get(str(target[0].relative_to(output)))
                if target_page:
                    check(target[1] in target_page.ids, f'锚点不存在：{url}，来源 {relative}')
        if page.metadata:
            metadata = json.loads(page.metadata)
            check(metadata['canonical'].startswith(base), f'页面元信息域名错误：{relative}')
            check(bool(page.metas.get('og:image')), f'分享封面缺失：{relative}')
            check(page.metas.get('og:title') == metadata['title'], f'分享标题与导航数据不一致：{relative}')
            local_target(page.metas['og:image'], origin)
            check(len(page.navigation) == 5, f'主导航不是五项：{relative}')
            check(len(page.feed_nodes) == 1, f'RSS 发现入口缺失或重复：{relative}')

    for css in output.rglob('*.css'):
        for url in re.findall(r'url\([\"\']?([^\)\"\']+)[\"\']?\)', css.read_text()):
            local_target(url, urljoin(base, str(css.relative_to(output))))

    today = datetime.now(ZoneInfo('Asia/Shanghai')).date()
    posts = []
    for source in (repo / 'content/posts').glob('*/index.md'):
        text = source.read_text()
        frontmatter = text.split('---', 2)[1]
        date = re.search(r'^date:\s*[\"\']?(\d{4}-\d{2}-\d{2})', frontmatter, re.M)
        if re.search(r'^draft:\s*true\s*$', frontmatter, re.M) or (date and datetime.fromisoformat(date.group(1)).date() > today):
            continue
        relative = f'posts/{source.parent.name}/index.html'
        posts.append(urljoin(base, relative.removesuffix('index.html')))
        check(relative in html_pages, f'文章页遗漏：{relative}')
        exported = output / relative.replace('.html', '.md')
        check(exported.is_file(), f'Markdown 导出遗漏：{relative}')
        if exported.is_file():
            content = exported.read_text()
            check(not content.startswith('---'), f'Markdown 导出仍包含元数据：{relative}')
            for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content):
                check(image.startswith(('https://', 'http://', '/', 'data:')), f'Markdown 配图不是绝对地址：{relative}：{image}')
            if args.baseline:
                old = Path(args.baseline) / relative.replace('.html', '.md')
                check(old.is_file() and old.read_bytes() == exported.read_bytes(), f'迁移改变了 Markdown 分发内容：{relative}')
        if 'series:' in frontmatter and relative in html_pages:
            check('article-series' in (output / relative).read_text(), f'系列入口遗漏：{relative}')

    items = ET.parse(output / 'index.xml').findall('./channel/item')
    check({item.findtext('link') for item in items} == set(posts), 'RSS 条目不是全部已发布文章')
    for item in items:
        relative = unquote(urlparse(item.findtext('link')).path[len(base_path):]) + 'index.html'
        rendered = re.sub(r'\s+', '', html_pages[relative].article_text)
        subscribed = re.sub(r'\s+', '', Page(item.findtext('description', '')).text)
        check(bool(rendered) and rendered in subscribed, f'RSS 未输出完整正文：{item.findtext("link")}')
        if html_pages[relative].giscus:
            config = json.loads(html_pages[relative].giscus)
            check(all(config.get(key) for key in ['repo', 'repo-id', 'category', 'category-id', 'mapping', 'lightTheme', 'darkTheme']), f'评论配置缺失：{relative}')
    for path in ['posts/index.xml', 'categories/index.xml', 'tags/index.xml']:
        entries = ET.parse(output / path).findall('./channel/item')
        check({item.findtext('link') for item in entries} == set(posts), f'汇总订阅未覆盖全部文章：{path}')
    index = json.loads((output / 'search/index.json').read_text())
    check({urljoin(base, entry['permalink']) for entry in index} == set(posts), '搜索 JSON 未覆盖全部文章')
    check(all({'title', 'date', 'permalink', 'content'} <= entry.keys() for entry in index), '搜索 JSON 字段不兼容')

    legacy = json.loads((repo / 'scripts/legacy-pages.json').read_text())
    for relative in legacy:
        page = html_pages.get(relative)
        check(page is not None and page.refresh == '0;url=../../', f'旧分页跳转遗漏：{relative}')
        if page:
            local_target('../../', urljoin(base, relative))

    data = json.loads((repo / 'data/blog.json').read_text())
    for track in data['playlist']:
        local_target(track['cover'], base)
        for audio in track['sources']:
            path = local_target(audio['src'], base)
            check(path and path[0].is_file() and path[0].stat().st_size > 1024, f'音频资源无效：{track["title"]}')

    result = {'文章数': len(posts), 'HTML页面数': len(html_pages), 'RSS文章数': len(items), '搜索条目数': len(index), '旧分页跳转数': len(legacy), '核验本站资源数': len(checked), '失败': errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
