# 根地址迁移

## 目录

1. 目标与实现
2. 兼容与验证
3. 发布结果

## 目标与实现

用户于 2026-10-08 授权把博客迁到 `https://s-infinite-box.github.io/`。将原仓库改名为 `s-infinite-box.github.io`，保留提交历史、仓库 ID 和 Discussions；本地工作目录仍为 `_sub_mod/SongMingHe`。

Hugo baseURL 和预览地址使用根路径，Pages 工作流沿用。giscus 仓库名更新，使用 specific 检索词 `SongMingHe/posts/<slug>/`，与原 pathname 生成的检索词一致，避免因文章 URL 改变而丢失评论关联。

## 兼容与验证

构建后为原 `/SongMingHe/` 命名空间生成兼容产物：HTML 跳转到相应根路径，保留查询参数与锚点；音频、配图、Markdown、RSS 等文件保留原地址可访问。兼容文件仅生成到 public，不复制进源码。旧分页跳转直接导向完整文章列表。

使用 Hugo 0.165.0 构建，核验 17 篇文章、RSS、搜索、旧分页、分享信息、资源以及旧命名空间的跳转/文件一致性；Markdown 比对只允许站点地址前缀变化。部署后验证根首页、旧文章链接及配图、默认 No Worries 与连续播放、giscus 加载和检索词。

## 发布结果

完成后将线上证据登记在父项目 `_followups/` 对应事项中。
