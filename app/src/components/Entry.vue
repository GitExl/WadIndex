<script setup lang="ts">
interface MusicTrackData {
  id: number
  name: string
  url: string
  title: string
  authors: string[]
}

interface EntryData {
  title: string
  path: string
  authors: string[]
  description: string
  engine: string
  game: string
  musicTracks: MusicTrackData[]
}

const props = defineProps<{
  entry: EntryData
}>()
</script>

<template>
  <div class="entry">
    <h2>{{ entry.title }}</h2>
    <p class="entry__authors">By {{ entry.authors }}</p>
    <p class="entry__path">{{ entry.path }}</p>

    <ul class="entry-tags">
      <li>{{ entry.engine }}</li>
      <li>{{ entry.game }}</li>
    </ul>

    <p>{{ entry.description }}</p>

    <!-- <TrackList :tracks="entry.musicTracks" /> -->
  </div>
</template>

<style lang="scss">
.entry {

}
</style>
