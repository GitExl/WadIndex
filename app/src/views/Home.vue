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
        <EntrySearch />
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
import API from '@/api/API';
import EntryList from '@/components/EntryList.vue';
import Layout from '@/components/Layout.vue';
import type { EntryTeaserData } from '@/data/EntryTeaser';
import type { IndexImage } from '@/data/IndexImage';
import { ref, type Ref, computed } from 'vue';
import { useTitle } from 'vue-page-title';
import EntrySearch from '../components/EntrySearch.vue'

const random: Ref<IndexImage[]> = ref([])
const latest: Ref<EntryTeaserData[]> = ref([])
const updated: Ref<EntryTeaserData[]> = ref([])

useTitle('');

const results = await Promise.all([
  API.graphics.getRandom(),
  API.entries.getLatest(),
  API.entries.getUpdated(),
]);

random.value = results[0];
latest.value = results[1];
updated.value = results[2];

const randomSplit = computed(() => {
  if (!random.value.length) {
    return [[], []];
  }

  const half = random.value.length / 2 + 1;
  return [
    random.value.slice(0, half),
    random.value.slice(half),
  ];
});

const storageBaseUrl = import.meta.env.VITE_STORAGE_BASE_URL;
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
      margin-bottom: 3.25rem;
    }
  }

  &__background {
    position: absolute;
    top: 0;
    right: 0;
    width: calc(100% - $nav-width);
    left: $nav-width;
    overflow-x: hidden;
    padding: 0.25rem;
    opacity: 0.25;
    z-index: -10;
  }

  &__background-row {
    display: flex;
    flex-direction: row;
    justify-content: center;
    width: 100%;
    position: relative;

    img {
      width: auto;
      height: 14rem;
      margin: 0.5rem;
      display: block;
      image-rendering: pixelated;
    }
  }
}
</style>
