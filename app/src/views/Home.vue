<script setup lang="ts">
import API from '@/api/API';
import EntryList from '@/components/EntryList.vue';
import type { EntryTeaser } from '@/data/EntryTeaser';
import { onMounted, ref, type Ref } from 'vue';
import EntrySearch from '../components/EntrySearch.vue'

const latest: Ref<EntryTeaser[]> = ref([])

onMounted(async () => {
  latest.value = await API.entries.getLatest();
})
</script>

<template>
  <div class="home">
    <div class="home__header">
      <img src="@/assets/images/logo.svg">
      <EntrySearch />
      <router-link to="/search">Advanced search</router-link>
    </div>

    <h1>Latest entries</h1>
    <EntryList :entries="latest" />
  </div>
</template>

<style lang="scss">
.home__header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 5rem;
  height: 30rem;

  img {
    max-width: 28rem;
    margin-bottom: 3.25rem;
  }
}
</style>
