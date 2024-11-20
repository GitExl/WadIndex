<template>
  <div class="search">

    <Layout type="one-column">

      <template v-slot:start>
        <PageSidebar class="search__sidebar">

          <EntrySearch class="search__entry-search" v-model="search" />

          <SearchSort title="Sort by" :options="sortOptions" name="sort" v-model="sort" />

          <SearchFilters title="Search in">
            <FilterCheckbox name="in" value="title" label="Title" v-model="filterIn"></FilterCheckbox>
            <FilterCheckbox name="in" value="filename" label="Filename" v-model="filterIn"></FilterCheckbox>
            <FilterCheckbox name="in" value="description" label="Description" v-model="filterIn"></FilterCheckbox>
            <FilterCheckbox name="in" value="textfile" label="Text file" v-model="filterIn"></FilterCheckbox>
          </SearchFilters>

          <SearchFilters title="Gameplay">
            <FilterCheckbox name="gameplay" value="singleplayer" label="Singleplayer" v-model="filterGameplay"></FilterCheckbox>
            <FilterCheckbox name="gameplay" value="deathmatch" label="Deathmatch" v-model="filterGameplay"></FilterCheckbox>
            <FilterCheckbox name="gameplay" value="cooperative" label="Cooperative" v-model="filterGameplay"></FilterCheckbox>
          </SearchFilters>

          <SearchFilters title="Game">
            <FilterCheckbox name="game" value="doom" label="Doom" v-model="filterGame"></FilterCheckbox>
            <FilterCheckbox name="game" value="doom2" label="Doom 2" v-model="filterGame"></FilterCheckbox>
            <FilterCheckbox name="game" value="tnt" label="TNT" v-model="filterGame"></FilterCheckbox>
            <FilterCheckbox name="game" value="plutonia" label="Plutonia" v-model="filterGame"></FilterCheckbox>
            <FilterCheckbox name="game" value="heretic" label="Heretic" v-model="filterGame"></FilterCheckbox>
            <FilterCheckbox name="game" value="hexen" label="Hexen" v-model="filterGame"></FilterCheckbox>
          </SearchFilters>

        </PageSidebar>
      </template>

      <div class="search__head">
        <h1>Search</h1>
      </div>

      <div class="search__info">
        <template v-if="status === 'pending'">
          Loading...
        </template>
        <EntryList v-else-if="results?.entries.length" :entries="results?.entries" />
        <template v-else-if="search">
          No entries found.
        </template>
      </div>

    </Layout>

  </div>
</template>

<script setup lang="ts">
import debounce from 'lodash.debounce'
import type { SearchSortOptions } from '~/components/SearchSort.vue'

const api = useApi();
const router = useRouter();
const route = useRoute();

const sortOptions: SearchSortOptions = {
  relevance: {
    title: 'Relevance',
    field: 'relevance',
    order: 'desc',
  },
  titleAZ: {
    title: 'Title A-Z',
    field: 'title',
    order: 'asc',
  },
  titleZA: {
    title: 'Title Z-A',
    field: 'title',
    order: 'desc',
  },
  newest: {
    title: 'Newest first',
    field: 'updated',
    order: 'desc',
  },
  oldest: {
    title: 'Oldest first',
    field: 'updated',
    order: 'asc',
  },
}

declare type LocationQueryValue = string | null;
function parseQueryArray(input: LocationQueryValue | LocationQueryValue[]): string[] {
  if (!input) {
    return [];
  }
  if (Array.isArray(input)) {
    return input as string[];
  }
  return [input as string];
}

function parseQueryString(input: LocationQueryValue | LocationQueryValue[], def: string = ''): string {
  if (!input) {
    return def;
  }
  if (Array.isArray(input)) {
    return (input as string[])[0];
  }
  return input;
}

const search: Ref<string> = ref(parseQueryString(route.query.search));
const sort: Ref<string> = ref(parseQueryString(route.query.sort, 'relevance'));
const filterIn: Ref<string[]> = ref(parseQueryArray(route.query.filterIn));
const filterGameplay: Ref<string[]> = ref(parseQueryArray(route.query.filterGameplay));
const filterGame: Ref<string[]> = ref(parseQueryArray(route.query.filterGame));

const sortOption = computed(() => {
  return sortOptions[sort.value];
});

const { data: results, refresh, status } = useAsyncData(
  () => api.entries.search(
    search.value,
    ['idgames'],
    filterIn.value,
    filterGameplay.value,
    filterGame.value,
    sortOption.value.field,
    sortOption.value.order
  )
);

watch(() => route.query, newQuery => {
  search.value = parseQueryString(newQuery.search);
  sort.value = parseQueryString(newQuery.sort, 'relevance');
  filterIn.value = parseQueryArray(newQuery.filterIn);
  filterGameplay.value = parseQueryArray(newQuery.filterGameplay);
  filterGame.value = parseQueryArray(newQuery.filterGame);
  refresh();
});

function updateArgs() {
  router.replace({
    name: route.name,
    query: {
      search: search.value,
      sort: sort.value,
      filterIn: filterIn.value,
      filterGameplay: filterGameplay.value,
      filterGame: filterGame.value,
    }
  })
}
const updateArgsDebounced = debounce(updateArgs, 500);

watch([search, sort, filterIn, filterGameplay, filterGame], () => {
  updateArgsDebounced();
})

useSeoMeta({
  title: 'Search',
});
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
