<script setup language="TS">
import BlogPages from '@/assets/pages/blogPages.json?raw'
import { ref } from 'vue'
import BlogItem from '@/views/BlogItem.vue'

const originalList = JSON.parse(BlogPages)
let tags = ref(originalList.tags)
let checkTags = ref(new Map())
let checkCategories = ref(new Map())
let categories = ref(originalList.categories)
let search = ref('')
let mdList = ref(originalList.blogPages)
// 过滤搜索条件方法
const filterProcessor = () => {
  mdList.value = originalList.blogPages.filter((md) => {
    if (search.value && !md.name.includes(search.value) && !md.htmlContent.includes(search.value)) {
      return false
    }
    if (checkTags.value.size) {
      let chechTagskeyFlag = true
      for (let checkTagsKey of checkTags.value.keys()) {
        if (!md.profile.tag.includes(checkTagsKey)) {
          chechTagskeyFlag = false
          break
        }
      }
      if (!chechTagskeyFlag) {
        return false
      }
    }
    if (
      checkCategories.value.size &&
      ![...checkCategories.value.keys()].includes(md.profile.category)
    ) {
      return false
    }
    return true
  })
}

const refresh = () => {
  checkTags.value = new Map()
  checkCategories.value = new Map()
  search.value = ''
  mdList.value = originalList.blogPages

}

// let lastKnownScrollPosition = 0;
// let ticking = false;
// document.addEventListener("scroll", (event) => {
//   lastKnownScrollPosition = window.scrollY;
//   if (!ticking) {
//     window.requestAnimationFrame(() => {
//       alert(lastKnownScrollPosition)
//       ticking = false;
//     });
//
//     ticking = true;
//   }
// });

</script>
<template>
  <el-container direction="horizontal">
    <el-aside width="17%" style="margin: 20px; text-align: center">
      <img
        src="@/assets/IMG_20181124_155151.jpg"
        style="height: 175px; width: 175px; border-radius: 50%"
        alt="img"
      />
      <br />
      <h3>您好！我是<span style="">宋明河</span><br />欢迎来到我的博客</h3>
      <a
        style="text-decoration: none; background-color: transparent"
        href="https://github.com/s-infinite-box"
        target="_blank"
        title="https://github.com/s-infinite-box"
      >
        <img src="@/assets/github-mark.png" alt="GitHub" class="font" />
      </a>
      <a
        style="text-decoration: none; background-color: transparent"
        href="mailto:MingHe.Song@hotmail.com"
        target="_blank"
        title="MingHe.Song@hotmail.com"
      >
        <img src="@/assets/mail.png" alt="邮箱" class="font" style="border-radius: 50%" />
      </a>
      <hr style="margin-top: 7px">

    </el-aside>
    <el-container>
      <el-main style="max-width: 775px" width="75%">
        <p style="margin-bottom: 5px">
          <el-input
            placeholder="请输入标题或内容"
            v-model="search"
            style="width: 200px"
            @change="filterProcessor"
            size="large"
            clearable
          />
          <!--          <el-select-->
          <!--            v-model="checkTags"-->
          <!--            multiple-->
          <!--            placeholder="选择标签"-->
          <!--            size="large"-->
          <!--            multiple-limit=3-->
          <!--            style="width: 200px"-->
          <!--            @change="filterProcessor"-->
          <!--          >-->
          <!--            <el-option-->
          <!--              v-for="item in tags"-->
          <!--              :value="item"/>-->
          <!--          </el-select>-->
          <!--          <el-select-->
          <!--            v-model="checkCategories"-->
          <!--            @change="(v)=>{filterProcessor()}"-->
          <!--            multiple-->
          <!--            placeholder="选择类别"-->
          <!--            size="large"-->
          <!--            multiple-limit=3-->
          <!--            style="width: 200px"-->
          <!--            remove-tag="remove-tag"-->
          <!--          >-->
          <!--            <el-option-->
          <!--              v-for="item in categories"-->
          <!--              :value="item"/>-->
          <!--          </el-select>-->
          <!--          <br>-->
          <!--          <el-tag-->
          <!--            v-for="category in categories"-->
          <!--            type="success"-->
          <!--            @click="checkCategories.set(category, '');filterProcessor()"-->
          <!--            effect="dark"-->
          <!--          >-->
          <!--            <a>{{ category }}</a>-->
          <!--          </el-tag>-->
          <!--          <br />-->
          <!--          <el-tag-->
          <!--            v-for="tag in tags"-->
          <!--            @click="checkTags.get(tag);checkTags.set(tag, '');filterProcessor()"-->
          <!--            effect="dark"-->
          <!--          >-->
          <!--            <a>{{ tag }}</a>-->
          <!--          </el-tag>-->


          <!-- 展示已选择的类别和标签 -->
          <!--          <el-tag-->
          <!--            v-for="category in checkCategories.keys()"-->
          <!--            type="success"-->
          <!--            @close=";checkCategories.delete(category);filterProcessor()"-->
          <!--            closable-->
          <!--          >-->
          <!--            {{ category }}-->
          <!--          </el-tag>-->
          <!--          <el-tag-->
          <!--            v-for="tag in checkTags.keys()"-->
          <!--            type="primary"-->
          <!--            @close="checkTags.delete(tag);filterProcessor();"-->
          <!--            closable-->
          <!--          >-->
          <!--            {{ tag }}-->
          <!--          </el-tag>-->
        </p>
        <BlogItem v-for="(md, i) in mdList">
          <template #heading>
            <!-- 名称 -->
            <a @click="mdList[i].displayFlag = !mdList[i].displayFlag">
              {{ md.profile.date }} &emsp;{{ md.name }}
            </a>
            <br />
            <!-- 类别 -->
            <el-button type="success" round>{{ md.profile.category }}</el-button>
            <!-- 标签 -->
            <el-button type="primary" v-for="tag in md.profile.tag" round>{{ tag }}</el-button>
          </template>
          <hr style="max-width: 475px;margin-left: 0" />
          <div v-html="md.htmlContent"  class="htmlContent" v-show="md.displayFlag" />
          <br />
        </BlogItem>
      </el-main>
      <el-footer>
        <el-button circle @click="refresh">&circlearrowleft;</el-button>
        <el-button circle @click="mdList.forEach(md=>md.displayFlag=false)">↑</el-button>
      </el-footer>
    </el-container>
  </el-container>


</template>

<style scoped>
.htmlContent img {
  //width: 100%;
  width: 100px;
}

.font {
  font-size: 20px;
  width: 35px;
  height: 35px;
}
</style>
