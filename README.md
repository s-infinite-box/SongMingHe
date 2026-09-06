# 宋明河的博客

基于 [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 主题的静态博客，通过 GitHub Actions 自动部署到 GitHub Pages。

在线地址：<https://s-infinite-box.github.io/SongMingHe/>

## 目录结构

```
.
├─ hugo.yaml                      # 站点配置（标题、菜单、主题参数）
├─ content/
│  ├─ posts/                      # 文章，每篇一个目录（page bundle）
│  │  └─ <slug>/
│  │     ├─ index.md              # 正文
│  │     └─ *.png                 # 该文章用到的图片，正文中直接写 ![](xxx.png)
│  ├─ archives.md                 # 归档页
│  └─ search.md                   # 搜索页
├─ layouts/
│  ├─ single.markdown.md          # 文章的 Markdown 输出模板（供"复制 Markdown"使用）
│  └─ _partials/
│     ├─ comments.html            # giscus 评论
│     └─ extend_post_content.html # 文章底部"复制 Markdown"工具栏
├─ assets/css/extended/custom.css # 自定义样式
├─ static/images/                 # 头像等全局静态资源
├─ themes/PaperMod/               # 主题（git submodule）
└─ .github/workflows/hugo.yml     # 构建 + 部署
```

## 本地预览

安装 Hugo extended 版（>= 0.146）：

```bash
# Fedora
sudo dnf install hugo
# 或从 https://github.com/gohugoio/hugo/releases 下载 hugo_extended_*_linux-amd64.tar.gz
```

首次克隆后拉取主题：

```bash
git submodule update --init --recursive
```

启动预览（默认 <http://localhost:1313/SongMingHe/>）：

```bash
hugo server -D   # -D 同时渲染草稿
```

## 写文章

```bash
hugo new posts/my-post/index.md
```

会在 `content/posts/my-post/index.md` 生成文件，补上 frontmatter 后开始写正文：

```yaml
---
title: "文章标题"
date: 2026-09-06T18:00:00+08:00
categories:
  - 学习拓展          # 一篇一个分类
tags:
  - linux             # 可多个
draft: false          # true 时不会发布
---
```

- 目录名（slug）用英文，它会成为 URL：`/posts/my-post/`
- 图片放在文章同一目录下，正文中用相对路径引用：`![说明](pic.png)`
- 单篇关闭评论：frontmatter 加 `comments: false`

## 发布

推送到 `main` 分支后，GitHub Actions 自动构建并发布到 GitHub Pages，约 1 分钟生效。

## 同步到 CSDN 等平台

每篇文章底部有「复制 Markdown」按钮，点击后剪贴板中是去掉 frontmatter 的正文，图片已改写为绝对 URL，可直接粘贴到 CSDN、掘金等平台的 Markdown 编辑器。也可以访问 `/posts/<slug>/index.md` 直接查看源文件。

## 评论

评论基于 [giscus](https://giscus.app)（GitHub Discussions），配置在 `layouts/_partials/comments.html`，数据存放在本仓库的 Discussions 中。

## 升级主题

```bash
git submodule update --remote --merge themes/PaperMod
```
