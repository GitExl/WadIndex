<template>
  <div class="home">

    <div class="home__background">
      <div class="home__background-row home__background-row--1">
        <img v-for="image of randomSplit[0]" :src="storageBaseUrl + '/' + image.hrefThumbnail" :width="image.width" :height="image.height" :style="{ 'aspect-ratio': image.aspectRatio }">
      </div>
      <div class="home__background-row home__background-row--2">
        <img v-for="image of randomSplit[1]" :src="storageBaseUrl + '/' + image.hrefThumbnail" :width="image.width" :height="image.height" :style="{ 'aspect-ratio': image.aspectRatio }">
      </div>
    </div>

    <Layout type="one-column">
      <div class="home__header">
        <img src="@/assets/images/logo.svg">
        <EntrySearch class="home__entry-search" />
        <router-link to="/search">Advanced search</router-link>
      </div>
    </Layout>

    <Layout type="two-column">
      <div>
        <h1>New entries</h1>
        <EntryList :entries="latest" />
      </div>

      <div>
        <h1>Recently updated</h1>
        <EntryList :entries="updated" />
      </div>
    </Layout>

  </div>
</template>

<script setup lang="ts">
const runtimeConfig = useRuntimeConfig();
const api = useApi();
const storageBaseUrl = runtimeConfig.public.otherUrl;

useSeoMeta({
  title: '',
});

const randomSplit = computed(() => {
  if (!random.value || !random.value.length) {
    return [[], []];
  }

  const half = random.value.length / 2 + 1;
  return [
    random.value.slice(0, half),
    random.value.slice(half),
  ];
});

const [{ data: random }, { data: latest }, { data: updated }] = await Promise.all([
  useAsyncData(() => api.graphics.getRandom()),
  useAsyncData(() => api.entries.getLatest()),
  useAsyncData(() => api.entries.getUpdated()),
]);
</script>

<style lang="scss">
.home {
  h1 {
    margin: 3rem 1rem 1rem 1rem;
  }

  &__header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 30rem;

    img {
      max-width: 28rem;
      margin-bottom: 2.25rem;
    }
  }

  &__background {
    position: absolute;
    top: 0;
    right: 0;
    width: 100%;
    left: 0;
    overflow-x: hidden;
    padding: 0.25rem;
    opacity: 0.2;
    z-index: -10;
  }

  &__background-row {
    display: flex;
    flex-direction: row;
    justify-content: center;
    width: calc(100% - $nav-width);
    position: relative;
    left: $nav-width;

    img {
      width: auto;
      height: 14rem;
      margin: 0.5rem;
      display: block;
      image-rendering: pixelated;
    }
  }

  &__entry-search {
    margin: 1rem;
  }
}
</style>
