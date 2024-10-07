<script setup lang="ts">
import BlogItem from './BlogItem.vue'
import BlogPages from '../assets/pages/blogPages.json?raw'
import { ref } from 'vue'

const orginalList = JSON.parse(BlogPages)
const mdList = ref(orginalList)
const displayFlag = ref(false)
</script>

<template>
  <button
    style="
      width: 80px;
      border-radius: 8px;
      background-color: turquoise;
      height: 25px;
      font-size: 14px;
    "
    @click="displayFlag = !displayFlag"
  >
    {{ displayFlag ? '隐藏正文' : '展示正文' }}
  </button>
  <!-- 博客列表 -->
  <BlogItem v-for="md in mdList">
    <template #heading>
      <a :href="md.profile.path">
        <!-- 名称 -->
        {{ md.name }} <span style="text-align: right">{{ md.profile.date }}</span>
        <br />
        <!-- 类别 -->
        <el-button type="success" v-for="category in md.profile.category" round
          >{{ category }}
        </el-button>
        <!-- 标签 -->
        <el-button type="primary" v-for="tag in md.profile.tag" round>{{ tag }}</el-button>
      </a>
    </template>
    <el-divider border-style="dashed" />
    <div v-html="md.htmlContent" class="htmlContent" v-show="displayFlag"></div>
    <el-divider v-show="displayFlag"></el-divider>
  </BlogItem>
</template>
<style>
.htmlContent img {
  width: 700px;
}
</style>
