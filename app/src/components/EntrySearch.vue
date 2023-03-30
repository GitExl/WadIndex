<script setup lang="ts">
import type { EntryTeaserData } from "@/data/EntryTeaser";
import { ref, type Ref } from "vue";

let searchTimer: number = 0

const searchTerms: Ref<string> = ref('')
const searching: Ref<boolean> = ref(false)
const results: Ref<EntryTeaserData[]> = ref([])

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
    <input type="search" placeholder="Search all entries" @keydown="keyDown" @input="input" />
  </div>
</template>

<style lang="scss">
.entry-search {
  width: 100%;
  max-width: 26rem;
  display: flex;
  flex-direction: column;

  input {
    margin: 1rem;
    width: calc(100% - 2rem);
    margin-bottom: 1rem;
  }
}
</style>
