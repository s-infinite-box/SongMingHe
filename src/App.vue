<script setup>

import BlogPages from '@/assets/pages/blogPages.json?raw'
import { ref } from 'vue'
import BlogItem from '@/views/BlogItem.vue'

const originalList = JSON.parse(BlogPages)
let tags = ref(originalList.tags)
let checkTags = ref([])
let checkCategories = ref([])
let categories = ref(originalList.categories)
let search = ref('')
let mdList = ref(originalList.blogPages)
const filterProcessor = () => {
  mdList.value = originalList.blogPages.filter(md => {
    if (search.value && !md.name.includes(search.value) && !md.htmlContent.includes(search.value)) {
      return false
    }
    if (checkTags.value.length) {
      let chechTagskeyFlag = true
      checkTags.value.forEach(checkTagsKey => {
        if (md.profile.tag.includes(checkTagsKey)) {
          chechTagskeyFlag = false
          return
        }
      })

      if (chechTagskeyFlag) {
        return false
      }
    }
    if (checkCategories.value.length && !checkCategories.value.includes(md.profile.category)) {
      return false
    }
    return true
  })

}

</script>

<template>
  <!-- 顶层容器 -->
  <div class="container">
    <div class="container-left">
      <div style="margin: 20px; text-align: center">
        <img
          src="@/assets/IMG_20181124_155151.jpg"
          style="height: 175px; width: 175px; border-radius: 50%"
          alt="img"
        />
        <br />
        <a style="  text-decoration: none;background-color: transparent;"
           href="https://github.com/s-infinite-box"
           target="_blank"
           title="https://github.com/s-infinite-box">
          <img src="@/assets/github-mark.png" alt="GitHub" class="font" />
        </a>
        <a style="  text-decoration: none;background-color: transparent;"
           href="mailto:MingHe.Song@hotmail.com"
           target="_blank"
           title="MingHe.Song@hotmail.com">
          <img src="@/assets/mail.png" alt="邮箱" class="font" style="border-radius: 50%" />
        </a>
        <h3>您好！我是<span style="color: rgb(0, 204, 204)">宋明河</span><br>欢迎来到我的博客</h3>
        <br>
        <el-input
          placeholder="请输入标题或内容"
          v-model="search"
          style="width: 75%"
          @onchange="filterProcessor"
          clearable>
        </el-input>

        <el-button @click="filterProcessor">
          搜索
          <!--          <svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">-->
          <!--            <path-->
          <!--              d="M15.7955 15.8111L21 21M18 10.5C18 14.6421 14.6421 18 10.5 18C6.35786 18 3 14.6421 3 10.5C3 6.35786 6.35786 3 10.5 3C14.6421 3 18 6.35786 18 10.5Z"-->
          <!--              stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />-->
          <!--          </svg>-->
        </el-button>
        <el-button @click="search='';checkTags=[];checkCategories=[];mdList = originalList.blogPages">
          重置
          <!--          <svg width="100%" height="100%" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">-->
          <!--            <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">-->
          <!--              <g id="Icon-Set-Filled" transform="translate(-154.000000, -1141.000000)" fill="#000000">-->
          <!--                <path-->
          <!--                  d="M184.858,1143.56 C185.397,1143.02 186.009,1142.55 186.009,1142 C186.009,1141.45 185.562,1141 185.009,1141 L175.009,1141 C174.888,1141 174.009,1141 174.009,1142 L174.009,1152 C174.009,1152.55 174.457,1153 175.009,1153 C175.562,1153 175.947,1152.47 176.373,1152.05 L179.152,1149.27 C180.922,1151.36 182,1154.05 182,1157 C182,1163.63 176.627,1169 170,1169 C163.373,1169 158,1163.63 158,1157 C158,1151.06 162.327,1146.13 168,1145.18 L168,1141.14 C160.109,1142.12 154,1148.84 154,1157 C154,1165.84 161.164,1173 170,1173 C178.836,1173 186,1165.84 186,1157 C186,1152.94 184.484,1149.25 181.993,1146.43 L184.858,1143.56"-->
          <!--                  id="refresh"></path>-->
          <!--              </g>-->
          <!--            </g>-->
          <!--          </svg>-->
        </el-button>
        <el-tag
          v-for="tag in checkTags"
          type="primary"
          @close="checkTags.splice(checkTags.indexOf(tag), 1);filterProcessor()"
          closable>
          {{ tag }}
        </el-tag>
        <el-tag
          v-for="category in checkCategories"
          type="success"
          @close="checkCategories.splice(checkCategories.indexOf(category), 1);filterProcessor()"
          closable>
          {{ category }}
        </el-tag>
        <h4>选择类别/标签：</h4>
        <el-tag
          v-for="category in categories"
          type="success"
          @click="checkCategories.push(category);filterProcessor()"
          effect="dark">
          <a>{{ category }}</a>
        </el-tag>
        <br>
        <el-tag
          v-for="tag in tags"
          @click="checkTags.push(tag);filterProcessor()"
          effect="dark">
          <a>{{ tag }}</a>
        </el-tag>
      </div>
      <br />
    </div>
    <div>
      <BlogItem v-for="(md, i) in mdList">
        <template #heading>
          <!-- 名称 -->
          <a @click="mdList[i].displayFlag = !mdList[i].displayFlag">
            {{ md.profile.date }} &emsp;{{ md.name }}
          </a>
          <br />
          <!-- 类别 -->
          <el-button
            type="success"
            round
          >
            {{ md.profile.category }}
          </el-button>
          <!-- 标签 -->
          <el-button
            type="primary"
            v-for="tag in md.profile.tag"
            round
          >{{ tag }}
          </el-button>

        </template>
        <hr />
        <div v-html="md.htmlContent" class="htmlContent" v-show="md.displayFlag" />
        <br>
      </BlogItem>
    </div>
  </div>
</template>

<style scoped>
.font {
  font-size: 20px;
  width: 35px;
  height: 35px;
}

.container-left {
  /* 边框线 */
  //border: 1px solid #000;
  /* 圆角 */
  //border-radius: 20px;
  //display: inline;
  width: 225px;
  //width: 15%;
  //height: 625px;
  //height: 345px;
  //background-color: rgb(255, 255, 204);
  //border-right: thick ridge #000;
}

.container {
  display: grid;
  grid-template-columns: 225px 775px;
  //grid-template-rows: 25% 65%;
  grid-gap: 20px 20px;
}

.pic {
  border-radius: 20px;
  vertical-align: middle;
  text-align: center;
  display: inline;
}

a {

}

/* 下面是VUE自带的style，暂时保留 */
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
