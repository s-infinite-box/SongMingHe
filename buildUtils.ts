import MarkdownIt from 'markdown-it'
import * as fs from 'fs'

const formateDate = (srcDate: Date | string): string => {
  let srcDateObj = srcDate
  if (typeof srcDate === 'string') {
    srcDateObj = new Date(Date.parse(srcDate))
  }
  // let hours = String(srcDateObj.getHours()).padStart(2, '0')
  // let minutes = String(srcDateObj.getMinutes()).padStart(2, '0')
  // let seconds = String(srcDateObj.getSeconds()).padStart(2, '0')

  return `${srcDateObj.getFullYear()}-${String(srcDateObj.getMonth() + 1).padStart(2, '0')}-${String(srcDateObj.getDate()).padStart(2, '0')}`
}

//  清理目录
const rmdir = (rmdirPath) => {
  try {
    fs.rmSync(rmdirPath, { recursive: true })
  } catch (err) {
    if (err && err.code !== 'ENOENT') {
      throw err
    }
  }
  //  重新创建目录
  fs.mkdirSync(rmdirPath)
}
const createMD = (imgPath: string): MarkdownIt => {
  return MarkdownIt({
    html: true, // 在源码中启用 HTML 标签
    xhtmlOut: false, // 使用 '/' 来闭合单标签 （比如 <br />）。
    // 这个选项只对完全的 CommonMark 模式兼容。
    breaks: false, // 转换段落里的 '\n' 到 <br>。
    langPrefix: 'language-', // 给围栏代码块的 CSS 语言前缀。对于额外的高亮代码非常有用。
    linkify: false, // 将类似 URL 的文本自动转换为链接。

    // 启用一些语言中立的替换 + 引号美化
    typographer: false,

    // 双 + 单引号替换对，当 typographer 启用时。
    // 或者智能引号等，可以是 String 或 Array。
    //
    // 比方说，你可以支持 '«»„“' 给俄罗斯人使用， '„“‚‘'  给德国人使用。
    // 还有 ['«\xA0', '\xA0»', '‹\xA0', '\xA0›'] 给法国人使用（包括 nbsp）。
    quotes: '“”‘’',

    // 高亮函数，会返回转义的HTML。
    // 或 '' 如果源字符串未更改，则应在外部进行转义。
    // 如果结果以 <pre ... 开头，内部包装器则会跳过。
    highlight: function (/*str, lang*/) {
      return ''
    }
  })
  // 图片路径处理插件
  md.use((md) => {
    // wrap raw image renderer rule
    const rawImageRule = md.renderer.rules.image!
    md.renderer.rules.image = (tokens, idx, options, env: MarkdownEnv, self) => {
      const token = tokens[idx]

      // get the image link
      const link = token.attrGet('src')

      if (link) {
        // replace the original link with resolved link
        token.attrSet('src', imgPath + link)
      }

      return rawImageRule(tokens, idx, options, env, self)
    }

    // wrap raw html renderer rule
    const createHtmlRule =
      (rawHtmlRule: RenderRule): RenderRule =>
      (tokens, idx, options, env: MarkdownEnv, self) => {
        // replace the original link with resolved link
        tokens[idx].content = tokens[idx].content
          // handle src
          .replace(
            /(<img\b.*?src=)(['"])(.*?)\2/gs,
            (_, prefix: string, quote: string, src: string) =>
              `${prefix}${quote}${imgPath + src.trim()}${quote}`
          )
          // handle srcset
          .replace(
            /(<img\b.*?srcset=)(['"])(.*?)\2/gs,
            (_, prefix: string, quote: string, srcset: string) =>
              `${prefix}${quote}${srcset
                .split(',')
                .map((item) =>
                  item
                    .trim()
                    .replace(
                      /^([^ ]*?)([ \n].*)?$/,
                      (__, url: string, descriptor: string | undefined = '') =>
                        `${imgPath + url.trim()}${descriptor.replace(/[ \n]+/g, ' ').trimEnd()}`
                    )
                )
                .join(', ')}${quote}`
          )

        return rawHtmlRule(tokens, idx, options, env, self)
      }
    const rawHtmlBlockRule = md.renderer.rules.html_block!
    const rawHtmlInlineRule = md.renderer.rules.html_inline!
    md.renderer.rules.html_block = createHtmlRule(rawHtmlBlockRule)
    md.renderer.rules.html_inline = createHtmlRule(rawHtmlInlineRule)
  })
}

// 异常处理回调函数
const err_throw = (error) => {
  if (error) {
    console.error(error)
    throw error
  }
}

export { createMD, rmdir, formateDate, err_throw }
