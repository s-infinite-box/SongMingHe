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
        <h3>您好！我是<span style="color: rgb(0, 204, 204)">宋明河</span><br />欢迎来到我的博客</h3>
        <p>
          <el-input
            placeholder="请输入标题或内容"
            v-model="search"
            style="width: 75%"
            @onchange="filterProcessor"
            clearable
          >
          </el-input>
        </p>
        <p>
          <el-button @click="filterProcessor">
            搜索
          </el-button>
          <el-button
            @click="checkTags.clear();checkCategories.clear();search = '';mdList = originalList.blogPages"
          >
            重置
          </el-button>
        </p>
        <el-tag
          v-for="tag in checkTags.keys()"
          type="primary"
          @close="checkTags.delete(tag);filterProcessor();"
          closable
        >
          {{ tag }}
        </el-tag>
        <el-tag
          v-for="category in checkCategories.keys()"
          type="success"
          @close=";checkCategories.delete(category);filterProcessor()"
          closable
        >
          {{ category }}
        </el-tag>
        <h4>选择类别/标签：</h4>
        <el-tag
          v-for="category in categories"
          type="success"
          @click="checkCategories.set(category, '');filterProcessor()"
          effect="dark"
        >
          <a>{{ category }}</a>
        </el-tag>
        <br />
        <el-tag
          v-for="tag in tags"
          @click="checkTags.set(tag, '');filterProcessor()"
          effect="dark"
        >
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
          <el-button type="success" round>
            {{ md.profile.category }}
          </el-button>
          <!-- 标签 -->
          <el-button type="primary" v-for="tag in md.profile.tag" round>{{ tag }}</el-button>
        </template>
        <hr />
        <div v-html="md.htmlContent" class="htmlContent" v-show="md.displayFlag" />
        <br />
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
  margin-top: 0px;
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
