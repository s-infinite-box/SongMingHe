# 宋明河的博客

基于 [Hugo](https://gohugo.io/) + [Stack](https://stack.jimmycai.com/) 主题（卡片式三栏布局）的静态博客，通过 GitHub Actions 自动部署到 GitHub Pages。

在线地址：<https://s-infinite-box.github.io/SongMingHe/>

## 目录结构

```
.
├─ hugo.yaml                      # 站点配置（标题、菜单、侧栏、小组件、评论）
├─ content/
│  ├─ _index.md                   # 首页（只声明菜单项）
│  ├─ posts/                      # 文章，每篇一个目录（page bundle）
│  │  └─ <slug>/
│  │     ├─ index.md              # 正文
│  │     └─ *.png                 # 该文章用到的图片，正文中直接写 ![](xxx.png)
│  └─ page/                       # 独立页面：归档、搜索、关于（URL 直接挂在根路径）
├─ layouts/
│  ├─ single.markdown.md          # 文章的 Markdown 输出模板（供"复制 Markdown"使用）
│  └─ _partials/article/components/
│     ├─ markdown-tools.html      # 文章底部"复制 Markdown"工具栏
│     └─ footer.html              # 覆盖主题的文章页脚，用于插入上面的工具栏
├─ assets/
│  ├─ scss/custom.scss            # 自定义样式（主题自动引入）
│  ├─ icons/mail.svg              # 侧栏邮箱图标（主题内置图标之外的补充）
│  └─ img/
│     ├─ avatar.jpg               # 头像
│     └─ covers/                  # 按技术区分的共用文章封面
├─ themes/hugo-theme-stack/       # 主题（git submodule）
└─ .github/workflows/hugo.yml     # 构建 + 部署
```

## 本地预览

安装 Hugo extended 版（>= 0.157）：

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
description: "一句话摘要，显示在列表卡片上（可选）"
date: 2026-09-06T18:00:00+08:00
image: cover.png      # 封面图，放在文章目录下（可选，不写则卡片无图）
categories:
  - Linux内核         # 一篇一个主题分类
tags:
  - Linux             # 按文章的具体技术与主题填写
draft: false          # true 时不会发布
---
```

- 目录名（slug）用英文，它会成为 URL：`/posts/my-post/`
- 图片放在文章同一目录下，正文中用相对路径引用：`![说明](pic.png)`
- 单篇关闭评论：frontmatter 加 `comments: false`
- 单篇关闭目录：frontmatter 加 `toc: false`

### 分类、标签与系列

每篇文章选择一个分类，按主要讨论的主题归档。故障排查、实践记录和学习思考是文章的写法，不单独作为分类。

| 分类 | 内容范围 |
| --- | --- |
| Linux内核 | 内核学习、进程与线程、IO 等操作系统机制 |
| 云原生 | 云原生应用、Kubernetes、容器网络与服务治理 |
| 编程语言 | 语言特性、宏与类型系统、编程语言学习方法 |
| 软件工程 | 研发流程、架构设计与工程实践 |
| 工具与自动化 | 工具使用、SDK 集成与任务自动化 |
| 系统环境 | Ubuntu、Windows、WSL、磁盘与主机环境配置及排障 |
| 硬件实践 | 硬件改装、散热与设备使用 |

标签用于关联具体技术和主题，通常选 2–5 个；内容较短的文章可以只用一个。技术名统一使用常见写法，例如 `Linux`、`Windows`、`Ubuntu`、`Kubernetes`、`Rust`、`Go`、`eBPF`、`systemd`、`NTFS`，避免大小写混用。学习方法统一用 `学习方法`，研发工作流程统一用 `研发流程`。

标签按文章重点选择，不因为正文提到某项技术就添加标签。`Cilium`、`syn`、`ClipCascade` 等具体技术标签可以保留；版本号只在版本差异或学习基线是文章重点时使用，如 `Linux 0.11`、`Linux 6.18`。

连续更新的一组文章使用 `series` 串联；现有内核学习系列保持 `aa-kernel-study`。系列不替代主题分类，零散文章无需创建系列。

旧分类中拆分到多个主题的入口跳转到分类总览；能够直接对应的旧分类和合并后的旧标签保留跳转，兼容已有链接。

### 共用技术封面

原 `_pphome/blog/icon/` 的封面统一保存在 `assets/img/covers/`。文章可以引用同一张封面，无需在每个文章目录重复保存：

```yaml
image: img/covers/rust.jpg
```

常用封面包括 `go.png`、`rust.jpg`、`k8s.png`、`cilium.jpg`、`nvidia.jpg`、`Linux.webp`、`linux_windows.jpg`、`feishu.jpg` 和 `Python.png`。优先使用横向图片作封面；方形徽标和小尺寸图标也保留在同一目录。文件名区分大小写。

当前内核学习、进程与线程、IO 模型文章使用 `image: img/covers/Linux.webp`。各篇文章的封面以 frontmatter 中的 `image` 设置为准。

`layouts/_partials/helper/image.html` 在文章目录中找不到图片时，会从 `assets/` 查找共用资源，因此封面仍能生成响应式图片，并适配 GitHub Pages 的 `/SongMingHe/` 路径。

### 旧博客合并

`_pphome/blog/` 的 8 篇旧文已合并到 `content/posts/`，涵盖飞书 Go SDK、Rust 过程宏、WSL、ClipCascade、Cilium、Kubernetes 升级和 Tesla T10 散热改装。正文配图存放在各自的文章目录中，旧的图片外链和 `/assets/` 路径已改为相对引用。

旧文没有声明发布时间；这批文章的 `date` 暂用旧目录首次进入 Git 的时间 `2026-04-14T15:18:15+08:00`。正文中的技术版本和操作记录按旧稿保留。

## 发布

推送到 `main` 分支后，GitHub Actions 自动构建并发布到 GitHub Pages，约 1 分钟生效。

## 同步到 CSDN 等平台

每篇文章底部有「复制 Markdown」按钮，点击后剪贴板中是去掉 frontmatter 的正文，图片已改写为绝对 URL，可直接粘贴到 CSDN、掘金等平台的 Markdown 编辑器。也可以访问 `/posts/<slug>/index.md` 直接查看源文件。

## 评论

评论基于 [giscus](https://giscus.app)（GitHub Discussions），使用 Stack 主题内置的 giscus 支持，配置在 `hugo.yaml` 的 `params.comments.giscus` 下，数据存放在本仓库的 Discussions 中。切换暗色模式时评论区配色会跟随。

## 升级主题

```bash
git submodule update --remote --merge themes/hugo-theme-stack
```

升级后请对照主题的 `layouts/_partials/article/components/footer.html` 检查本仓库的同名覆盖文件是否需要同步。

同时检查 `layouts/_partials/helper/image.html`，保留共用封面的资源查找逻辑。
