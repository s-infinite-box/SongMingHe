#!/usr/bin/env python3
"""核验正式构建的文章、导出、订阅、搜索、旧链接和本地资源，仅使用标准库。"""
import argparse
import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse
import xml.etree.ElementTree as ET


def published_posts(manifest):
    """使用与构建同一时刻的 Hugo 清单，遵循其发布时间、时区和草稿规则。"""
    with manifest.open(newline='', encoding='utf-8') as source:
        return [row for row in csv.DictReader(source)
                if row['kind'] == 'page' and row['section'] == 'posts']


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
        self.taxonomy_depth = 0
        self.taxonomies = {'categories': False, 'tags': False}
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
            if self.taxonomy_depth:
                self.taxonomy_depth += 1
            elif {'post-meta', 'post-tags'} & set(attrs.get('class', '').split()):
                self.taxonomy_depth = 1
        if tag == 'a' and self.taxonomy_depth:
            for name in self.taxonomies:
                if f'/{name}/' in urlparse(attrs.get('href', '')).path:
                    self.taxonomies[name] = True
        if tag == 'link' and attrs.get('type') == 'application/rss+xml':
            self.feed_nodes.append(attrs.get('href'))

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_metadata = False
            self.in_giscus = False
        if tag == 'div' and self.article_depth:
            self.article_depth -= 1
        if tag == 'div' and self.taxonomy_depth:
            self.taxonomy_depth -= 1

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
    parser.add_argument('--baseline-base-url', help='可选：比对时将旧站点地址前缀替换为当前地址')
    parser.add_argument('--published', default='.build-published.csv', help='同一构建时刻的 hugo list published 清单')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    manifest = Path(args.published)
    if not manifest.is_file():
        parser.error('缺少已发布文章清单；请先运行 make build，或通过 --published 指定同一时刻的 Hugo 清单')
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
            for tag, url in page.links:
                parsed = urlparse(url)
                if parsed.path.endswith(('.css', '.js')) and parsed.netloc in ('', base_url.netloc):
                    resource = output / unquote(parsed.path[len(base_path):])
                    if resource.is_file():
                        expected = hashlib.sha256(resource.read_bytes()).hexdigest()
                        check(parse_qs(parsed.query).get('v') == [expected], f'样式或脚本内容指纹错误：{relative}：{url}')

    for css in output.rglob('*.css'):
        for url in re.findall(r'url\([\"\']?([^\)\"\']+)[\"\']?\)', css.read_text()):
            local_target(url, urljoin(base, str(css.relative_to(output))))

    posts = []
    taxonomy_posts = {'categories': set(), 'tags': set()}
    for entry in published_posts(manifest):
        source = repo / entry['path']
        text = source.read_text()
        frontmatter = text.split('---', 2)[1]
        relative = unquote(urlparse(entry['permalink']).path[len(base_path):]) + 'index.html'
        posts.append(entry['permalink'])
        check(relative in html_pages, f'文章页遗漏：{relative}')
        if relative in html_pages:
            for name, present in html_pages[relative].taxonomies.items():
                if present:
                    taxonomy_posts[name].add(entry['permalink'])
        exported = output / relative.replace('.html', '.md')
        check(exported.is_file(), f'Markdown 导出遗漏：{relative}')
        if exported.is_file():
            content = exported.read_text()
            check(not content.startswith('---'), f'Markdown 导出仍包含元数据：{relative}')
            for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content):
                check(image.startswith(('https://', 'http://', '/', 'data:')), f'Markdown 配图不是绝对地址：{relative}：{image}')
            if args.baseline:
                old = Path(args.baseline) / relative.replace('.html', '.md')
                previous = old.read_bytes() if old.is_file() else None
                if previous is not None and args.baseline_base_url:
                    previous = previous.replace(args.baseline_base_url.encode(), base.encode())
                check(previous == exported.read_bytes(), f'迁移改变了 Markdown 分发内容：{relative}')
        if 'series:' in frontmatter and relative in html_pages:
            check('article-series' in (output / relative).read_text(), f'系列入口遗漏：{relative}')

    items = ET.parse(output / 'index.xml').findall('./channel/item')
    check({item.findtext('link') for item in items} == set(posts), 'RSS 条目不是全部已发布文章')
    for item in items:
        relative = unquote(urlparse(item.findtext('link')).path[len(base_path):]) + 'index.html'
        rendered = re.sub(r'\s+', '', html_pages[relative].article_text)
        description = Page(item.findtext('description', ''))
        subscribed = re.sub(r'\s+', '', description.text)
        check(bool(rendered) and rendered in subscribed, f'RSS 未输出完整正文：{item.findtext("link")}')
        for tag, url in description.links:
            if tag in ('a', 'img', 'source'):
                check(bool(urlparse(url).scheme), f'RSS 正文仍有相对地址：{item.findtext("link")}：{url}')
        if html_pages[relative].giscus:
            config = json.loads(html_pages[relative].giscus)
            check(all(config.get(key) for key in ['repo', 'repo-id', 'category', 'category-id', 'mapping', 'lightTheme', 'darkTheme']), f'评论配置缺失：{relative}')
            check(config.get('repo') == 's-infinite-box/s-infinite-box.github.io', f'评论仓库未更新：{relative}')
            check(config.get('mapping') == 'specific' and config.get('term') == 'SongMingHe/' + relative.removesuffix('index.html'), f'旧评论检索词发生变化：{relative}')
    for path in ['posts/index.xml', 'categories/index.xml', 'tags/index.xml']:
        entries = ET.parse(output / path).findall('./channel/item')
        section = path.split('/')[0]
        expected = taxonomy_posts.get(section, set(posts))
        check({item.findtext('link') for item in entries} == expected, f'汇总订阅与文章实际归属不一致：{path}')
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

    # 根站点必须保留旧项目地址下的页面、导出和所有资源。
    old_root = output / 'SongMingHe'
    old_html = 0
    old_files = 0
    for source in output.rglob('*'):
        if not source.is_file() or source.is_relative_to(old_root):
            continue
        relative = source.relative_to(output)
        target = old_root / relative
        check(target.is_file(), f'旧地址兼容文件遗漏：{relative}')
        if not target.is_file():
            continue
        if source.suffix != '.html':
            check(source.read_bytes() == target.read_bytes(), f'旧地址资源内容改变：{relative}')
            old_files += 1
            continue
        page = html_pages[str(target.relative_to(output))]
        old_html += 1
        check(page.metas.get('robots') == 'noindex,follow' and bool(page.refresh), f'旧页面不是禁止索引的跳转：{relative}')
        check('location.search+location.hash' in target.read_text(), f'旧页面未保留查询和锚点：{relative}')
        redirected = local_target(page.refresh.split('url=', 1)[-1], urljoin(base, str(target.relative_to(output))))
        check(redirected and not redirected[0].is_relative_to(old_root), f'旧页面未跳转到根路径：{relative}')

    result = {'文章数': len(posts), 'HTML页面数': len(html_pages), 'RSS文章数': len(items), '搜索条目数': len(index), '旧分页跳转数': len(legacy), '旧项目页面跳转数': old_html, '旧项目文件数': old_files, '核验本站资源数': len(checked), '失败': errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
