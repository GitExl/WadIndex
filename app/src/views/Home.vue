<script setup lang="ts">
import API from '@/api/API';
import EntryList from '@/components/EntryList.vue';
import Layout from '@/components/Layout.vue';
import type { EntryTeaserData } from '@/data/EntryTeaser';
import { onMounted, ref, type Ref } from 'vue';
import { useTitle } from 'vue-page-title';
import EntrySearch from '../components/EntrySearch.vue'

const latest: Ref<EntryTeaserData[]> = ref([])
const updated: Ref<EntryTeaserData[]> = ref([])

useTitle('');

onMounted(async () => {
  const results = await Promise.all([
    API.entries.getLatest(),
    API.entries.getUpdated(),
  ]);

  latest.value = results[0];
  updated.value = results[1];
})
</script>

<template>
  <div class="home">
    <div class="home__background">
      <div class="home__background-row home__background-row--1">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/btsx_e1_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/biowar_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/dcv_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/abyss24a_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/longtrek_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/projectunity_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/rlmchaos_titlepic_thumb.webp">
      </div>
      <div class="home__background-row home__background-row--2">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/tmmc2_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/toon2b_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/v64_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/world_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/techwars_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/dot_titlepic_thumb.webp">
        <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/requiem_titlepic_thumb.webp">
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
    left: 0;
    right: 0;
    width: 100%;
    overflow-x: hidden;
    padding: 0.25rem;
    opacity: 0.25;
    z-index: -10;
  }

  &__background-row {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    width: 150%;

    img {
      width: auto;
      height: 14rem;
      margin: 0.5rem;
      display: block;
      image-rendering: pixelated;
    }

    &--2 {
      left: -25%;
    }
  }
}
</style>
