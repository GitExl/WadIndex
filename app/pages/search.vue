<template>
  <div class="search">

    <Layout type="one-column">

      <template v-slot:start>
        <PageSidebar class="search__sidebar">

          <EntrySearch class="search__entry-search" />

          <SearchFilters title="Search in">
            <FilterCheckbox name="in-title" title="Title"></FilterCheckbox>
            <FilterCheckbox name="in-description" title="Description"></FilterCheckbox>
            <FilterCheckbox name="in-filename" title="Filename"></FilterCheckbox>
            <FilterCheckbox name="in-textfile" title="Text file"></FilterCheckbox>
          </SearchFilters>

          <SearchFilters title="Gameplay">
            <FilterCheckbox name="gameplay-any" title="Any"></FilterCheckbox>
            <FilterCheckbox name="gameplay-sp" title="Singleplayer"></FilterCheckbox>
            <FilterCheckbox name="gameplay-dm" title="Deathmatch"></FilterCheckbox>
            <FilterCheckbox name="gameplay-coop" title="Cooperative"></FilterCheckbox>
          </SearchFilters>

          <SearchFilters title="Game">
            <FilterCheckbox name="game-any" title="Any"></FilterCheckbox>
            <FilterCheckbox name="game-doom" title="Doom"></FilterCheckbox>
            <FilterCheckbox name="game-doom2" title="Doom 2"></FilterCheckbox>
            <FilterCheckbox name="game-tnt" title="TNT"></FilterCheckbox>
            <FilterCheckbox name="game-putonia" title="Plutonia"></FilterCheckbox>
            <FilterCheckbox name="game-heretic" title="Heretic"></FilterCheckbox>
            <FilterCheckbox name="game-hexen" title="Hexen"></FilterCheckbox>
          </SearchFilters>

        </PageSidebar>
      </template>

      <div class="search__head">
        <h1>Search</h1>
      </div>

      <div class="search__info">
        <EntryList v-if="results" :entries="results?.entries" />
      </div>

    </Layout>

  </div>
</template>

<script setup lang="ts">
import { ref, type Ref } from 'vue';
import type { SearchResults } from '@/api/EntriesAPI';

const results: Ref<SearchResults|undefined> = ref();

useSeoMeta({
  title: 'Search',
});

const api = useApi();

results.value = await api.entries.search('alien', ['idgames'], [], [], []);
</script>

<style lang="scss">
.search {
  height: 100%;
  padding-top: 3rem;

  &__head {
    h1 {
      margin-bottom: 0.625rem;
      margin-top: -0.5rem;
      margin-left: 1rem;
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
