<template>

  <InfoBlock :id="'map-' + level.name" class="level-teaser">

    <InfoBlockRow header :to="link">
      <div class="level-teaser__monospaced">{{ level.name }}</div>
      <div v-if="level.title" class="level-teaser__title">
        {{ level.title }}
      </div>
    </InfoBlockRow>

    <InfoBlockRow v-if="level.authors.length">
      <div>Authors</div>
      <div><AuthorList :authors="level.authors" :limit="2"></AuthorList></div>
    </InfoBlockRow>

    <InfoBlockRow v-if="level.musicName">
      <div>Music</div>
      <a class="level-teaser__monospaced" :href="'#music-' + level.musicName">{{ level.musicName }}</a>
    </InfoBlockRow>

    <InfoBlockRow v-if="level.next">
      <div>Next</div>
      <a class="level-teaser__monospaced" :href="'#map-' + level.next">{{ level.next }}</a>
    </InfoBlockRow>

    <InfoBlockRow v-if="level.nextSecret">
      <div>Next secret</div>
      <a class="level-teaser__monospaced" :href="'#map-' + level.nextSecret">{{ level.nextSecret }}</a>
    </InfoBlockRow>

  </InfoBlock>

</template>

<script setup lang="ts">
import type { LevelTeaserData } from '@/data/LevelTeaser';
import { computed } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import AuthorList from './AuthorList.vue';
import InfoBlock from './InfoBlock.vue';
import InfoBlockRow from './InfoBlockRow.vue';

const props = defineProps<{
  level: LevelTeaserData
}>()

const link = computed((): RouteLocationRaw => {
  return {
    path: '/map/' + props.level.collection + '/' + props.level.path + '/' + props.level.name + '/',
  };
})
</script>

<style lang="scss">
.level-teaser {
  &__monospaced {
    font-family: 'Noto Mono';
    font-size: 0.875rem;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
  }
}
</style>
