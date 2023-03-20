<script setup lang="ts">
import API from '@/api/API';
import EntryList from '@/components/EntryList.vue';
import Layout from '@/components/Layout.vue';
import type { EntryTeaserData } from '@/data/EntryTeaser';
import { onMounted, ref, type Ref } from 'vue';
import EntrySearch from '../components/EntrySearch.vue'

const latest: Ref<EntryTeaserData[]> = ref([])
const updated: Ref<EntryTeaserData[]> = ref([])

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
.home__header {
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
</style>
