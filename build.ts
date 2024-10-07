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
  const blogPages = []

  //  创建md解析器
  const md = createMD(imgPath)
  //  清理输出目录
  rmdir(absMDPagesPath)
  // rmdir(absImgPath)

  //  读取md文件夹，处理md文件
  fs.readdirSync(srcMDFilePath).forEach((file) => {
    const filePath = srcMDFilePath + file
    if (!file.endsWith('.md')) {
      fs.cpSync(filePath, absImgPath + file, { recursive: true })
      return
    }
    // 读取md文件内容
    const mdContent = fs.readFileSync(filePath, 'utf8')
    const { data, content } = grayMatter(mdContent, { excerpt: false })
    data.date = formateDate(data.date)

    const htmlContent = md.render(content)
    fs.writeFile(absMDPagesPath + file.replace('.md', '.html'), htmlContent, err_throw)
    blogPages.push({
      profile: data,
      htmlContent,
      path: `/${mdPagesPath}${file.replace('.md', '.html')}`,
      name: file.replace('.md', '')
    })
  })
  fs.writeFileSync(`${absMDPagesPath}blogPages.json`, JSON.stringify(blogPages))
}
