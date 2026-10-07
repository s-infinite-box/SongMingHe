#!/usr/bin/env python3
"""为根站点构建补齐旧 /SongMingHe/ 页面跳转和文件地址。"""
import argparse
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urljoin


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', default='public')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    if output == repo or not (output / 'index.html').is_file():
        parser.error('必须指定已完成 Hugo 构建的产物目录')
    base = re.search(r'^baseURL:\s*(\S+)', (repo / 'hugo.yaml').read_text(), re.M).group(1)
    legacy = output / 'SongMingHe'
    # 此目录只保存由本脚本生成的兼容产物，每次构建重新生成以清除旧文件。
    if legacy.exists():
        shutil.rmtree(legacy)
    sources = sorted(path for path in output.rglob('*') if path.is_file())
    redirects = 0
    resources = 0
    for source in sources:
        relative = source.relative_to(output)
        destination = legacy / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix != '.html':
            shutil.copyfile(source, destination)
            resources += 1
            continue
        target = quote('/' + relative.as_posix(), safe='/')
        if target.endswith('/index.html'):
            target = target.removesuffix('index.html')
        # 原分页也是跳转页，直接落到相应完整列表，减少一次中转。
        if re.search(r'/page/\d+/index\.html$', '/' + relative.as_posix()):
            target = urljoin(target, '../../')
        canonical = html.escape(urljoin(base, target), quote=True)
        escaped = html.escape(target, quote=True)
        script_target = json.dumps(target)
        destination.write_text(
            '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex,follow">'
            f'<link rel="canonical" href="{canonical}">'
            f'<meta http-equiv="refresh" content="0;url={escaped}">'
            '<title>博客地址已更新</title>'
            f'<script>location.replace({script_target}+location.search+location.hash)</script>'
            f'</head><body><a href="{escaped}">前往新的博客地址</a></body></html>')
        redirects += 1
    print(json.dumps({'旧页面跳转': redirects, '旧地址文件': resources}, ensure_ascii=False))


if __name__ == '__main__':
    main()
