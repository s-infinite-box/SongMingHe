<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <!-- 顶层容器 -->
  <div class="container">
    <div class="container-left">
      <div style="margin: 20px; text-align: center">
        <a href="/">
          <img
            src="@/assets/IMG_20181124_155151.jpg"
            style="height: 175px; width: 175px; border-radius: 50%"
            alt="img"
          />
        </a>

        <br />
        <a href="https://github.com/s-infinite-box" target="_blank">
          <img src="@/assets/github-mark.png" alt="GitHub" class="font" />
          <!--          <span class="font">GitHub;</span>-->
        </a>
        <a href="mailto:MingHe.Song@hotmail.com" target="_blank">
          <img src="@/assets/mail.png" alt="邮箱" class="font" />
          <!--          <span class="font">邮箱;</span>-->
        </a>
        <h2>您好！我是<span style="color: rgb(0, 204, 204)">宋明河</span></h2>
        <h2>欢迎来到我的博客</h2>
      </div>
      <br />
    </div>
    <div>
      <img
        alt="SongMingHe blog background"
        width="100%"
        class="pic"
        src="@/assets/polar_bear.jpg"
      />
      <nav style="margin: auto">
        <!--        <RouterLink to="/welcome"><h2>Welcome</h2></RouterLink>-->
        <RouterLink to="/"><h2>博客</h2></RouterLink>
      </nav>
      <RouterView style="" />
    </div>
  </div>
</template>

<style scoped>
.font {
  font-size: 20px;
  width: 20px;
  height: 20px;
}

.container-left {
  /* 边框线 */
  border: 1px solid #000;
  /* 圆角 */
  border-radius: 20px;
  //display: inline;
  width: 225px;
  //width: 15%;
  //height: 625px;
  height: 345px;
}

.container {
  display: grid;
  grid-template-columns: 225px 775px;
  //grid-template-rows: 25% 65%;
  grid-gap: 20px 20px;
  margin: 0 auto;
}

.pic {
  border-radius: 20px;
  vertical-align: middle;
  text-align: center;
  display: inline;
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
