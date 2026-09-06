{{- /*
  文章的 Markdown 输出格式（对应 hugo.yaml 中 outputFormats.markdown）。
  产物为 /posts/<slug>/index.md：
    - 内容为去掉 frontmatter 的正文（.RawContent）
    - 相对路径的图片改写为绝对 URL，方便直接粘贴到 CSDN、掘金等平台
    - 已经是 http(s):// 或以 / 开头的图片路径保持不变
*/ -}}
{{- $base := .Permalink -}}
{{- $content := .RawContent -}}
{{- /* ![alt](./img.png) -> ![alt](img.png) */ -}}
{{- $content = replaceRE `!\[([^\]]*)\]\(\./` "![$1](" $content -}}
{{- /* ![alt](img.png) -> ![alt](https://.../posts/<slug>/img.png) */ -}}
{{- $content = replaceRE `!\[([^\]]*)\]\(([^):/][^):]*)\)` (printf "![$1](%s$2)" $base) $content -}}
{{- /* <img src="img.png"> 同样处理 */ -}}
{{- $content = replaceRE `(<img[^>]*\ssrc=["'])(?:\./)?([^"':/][^"':]*)(["'])` (printf "${1}%s${2}${3}" $base) $content -}}
{{- $content | strings.TrimSpace }}
