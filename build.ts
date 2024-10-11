// https://nodejs.org/docs/latest/api/fs.html
import * as fs from 'fs'
import grayMatter from 'gray-matter'
import { createMD, rmdir, formateDate, err_throw } from './buildUtils'

export default (
  srcMDFilePath = `./src/md/`,
  mdPagesPath = 'pages/',
  absMDPagesPath = `./src/assets/${mdPagesPath}`,
  // imgPath = '/pages_img/',
  imgPath = '/',
  absImgPath = `./public${imgPath}`
) => {
  let blogPages = []

  //  创建md解析器
  const md = createMD(imgPath)
  //  清理输出目录
  rmdir(absMDPagesPath)
  // rmdir(absImgPath)

  //  读取md文件夹，处理md文件
  fs.readdirSync(srcMDFilePath).forEach((file) => {
    const filePath = srcMDFilePath + file
    // 非md文件作为静态资源，按路径复制
    if (!file.endsWith('.md')) {
      fs.cpSync(filePath, absImgPath + file, { recursive: true })
      return
    }
    // 读取md文件内容
    const mdContent = fs.readFileSync(filePath, 'utf8')
    const { data, content } = grayMatter(mdContent, { excerpt: false })
    if (data.date) {
      data.date = formateDate(data.date)
    } else {
      data.date = formateDate(new Date())
    }

    const htmlContent = md.render(content)
    fs.writeFile(absMDPagesPath + file.replace('.md', '.html'), htmlContent, err_throw)
    blogPages.push({
      profile: data,
      htmlContent,
      path: `/${mdPagesPath}${file.replace('.md', '.html')}`,
      name: file.replace('.md', '')
    })
  })
  blogPages = blogPages.sort((a, b) =>{return b.profile.date.localeCompare(a.profile.date)})
  fs.writeFileSync(`${absMDPagesPath}blogPages.json`, JSON.stringify(blogPages))
}
