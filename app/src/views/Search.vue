<template>
  <div class="search">

    <Layout type="one-column">

      <template v-slot:start>
        <PageSidebar class="search__sidebar">

          <EntrySearch class="search__entry-search" />

          <div class="filters">
            <h3 class="filters__title">Search in</h3>
            <ul class="filters__list">
              <li class="filters__filter">
                <input id="checkbox-1" type="checkbox"> <label for="checkbox-1">Title</label>
              </li>
              <li class="filters__filter">
                <input id="checkbox-2" type="checkbox"> <label for="checkbox-2">Description</label>
              </li>
              <li class="filters__filter">
                <input id="checkbox-3" type="checkbox"> <label for="checkbox-3">Filename</label>
              </li>
              <li class="filters__filter">
                <input id="checkbox-4" type="checkbox"> <label for="checkbox-4">Text file</label>
              </li>
            </ul>
          </div>

        </PageSidebar>
      </template>

      <div class="search__head">
        <h1>Search</h1>
      </div>

    </Layout>

  </div>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue';
import { useRoute } from 'vue-router';
import { useTitle } from 'vue-page-title';
import PageSidebar from '@/components/PageSidebar.vue';
import EntrySearch from '@/components/EntrySearch.vue';

const route = useRoute();

useTitle('Search');
</script>

<style lang="scss">
.search {
  height: 100%;

  &__head {
    margin-bottom: 3rem;

    h1 {
      margin-bottom: 0.625rem;
      margin-top: -0.5rem;
      font-size: 2.75rem;
    }
  }

  &__sidebar {
    > * {
      min-width: 13rem;
      max-width: 16rem;
    }
  }

  &__entry-search {

  }
}
</style>
