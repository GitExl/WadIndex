<script setup lang="ts">
import type { Entry } from "@/data/Entry";
import { ref, type Ref } from "vue";
import EntryList from "./EntryList.vue";

let searchTimer: number = 0

const searchTerms: Ref<string> = ref('')
const searching: Ref<boolean> = ref(false)
const results: Ref<Entry[]> = ref([])

async function search() {
  if (!searchTerms) {
    return
  }

  if (searching.value) {
    return
  }
  searching.value = true

  const response = await fetch('http://api.idgames.local/?action=entry_search&collection=idgames&key=' + searchTerms.value)
  if (response) {
    results.value = await response.json()
  }
  searching.value = false
}

function input(event: Event) {
  const target = event.target as HTMLInputElement
  searchTerms.value = target.value

  clearTimeout(searchTimer)
  searchTimer = setTimeout(search, 500)
}

function keyDown(event: Event) {
  const keyboardEvent = event as KeyboardEvent

  if (keyboardEvent.key === 'Enter') {
    clearTimeout(searchTimer)
    search()
  }
}
</script>

<template>
  <div class="entry-search">
    <input type="search" placeholder="Search" @keydown="keyDown" @input="input" />

    <p v-if="searching" class="entry-search__status">Searching...</p>
    <EntryList v-else-if="results.length && searchTerms" :entries="results" />
    <p v-else-if="searchTerms" class="entry-search__status">No results found.</p>
  </div>
</template>

<style lang="scss">
.entry-search {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  input {
    padding: 0.5rem;
    margin: 1rem;
    width: calc(100% - 2rem);
    border: none;
    background-color: #333;
    color: #fff;
    margin-bottom: 1rem;
  }
}

.entry-search__status {
  text-align: center;
  margin: 0;
}
</style>
