<template>

  <div class="level-teaser" :id="'map-' + level.name">

    <router-link :to="link">
      <div class="level-teaser__row level-teaser__header">
        <div class="level-teaser__name">{{ level.name }}</div>
        <div v-if="level.title" class="level-teaser__title">
          {{ level.title }}
        </div>
        <span class="level-teaser__chevron material-icons-outlined">chevron_right</span>
      </div>
    </router-link>

    <div v-if="level.authors.length" class="level-teaser__row level-teaser__content">
      <div>Authors</div>
      <div><AuthorList :authors="level.authors" :limit="2"></AuthorList></div>
    </div>

    <div v-if="level.musicName" class="level-teaser__row level-teaser__content">
      <div>Music</div>
      <div class="level-teaser__music">{{ level.musicName }}</div>
    </div>

    <div v-if="level.next" class="level-teaser__row level-teaser__content">
      <div>Next</div>
      <a class="level-teaser__level" :href="'#map-' + level.next">{{ level.next }}</a>
    </div>

    <div v-if="level.nextSecret" class="level-teaser__row level-teaser__content">
      <div>Next secret</div>
      <a class="level-teaser__level" :href="'#map-' + level.nextSecret">{{ level.nextSecret }}</a>
    </div>
  </div>

</template>

<script setup lang="ts">
import type { LevelTeaserData } from '@/data/LevelTeaser';
import { computed } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import AuthorList from './AuthorList.vue';

const props = defineProps<{
  level: LevelTeaserData
}>()

const link = computed((): RouteLocationRaw => {
  return {
    path: '/maps/' + props.level.collection + '/' + props.level.path + '/' + props.level.name + '/',
  };
})
</script>

<style lang="scss">
.level-teaser {
  width: 100%;
  border: 3px solid $color-primary;

  > a {
    text-decoration: none;
  }

  &:hover {
    @include rect;

    .level-teaser__header {
      @include rect-solid;
    }
  }

  &__row {
    display: grid;
    grid-template-columns: 6rem 1fr;
    position: relative;

    > *:first-child {
      width: 8rem;
    }

    > * {
      padding: 0.25rem 0.5rem;
    }
  }

  &__header {
    background-color: $color-primary;
    color: #fff;

    > * {
      padding: 0.375rem 0.5rem;
    }
  }

  &__chevron {
    position: absolute;
    right: 0;
    color: $color-primary-light;
    font-size: 1.25rem;
  }

  &__name {
    font-family: 'Noto Mono';
    font-size: 0.875rem;
  }

  &__title {
    font-weight: normal;
  }

  &__music {
    font-family: 'Noto Mono';
    font-size: 0.875rem;
  }

  &__level {
    font-family: 'Noto Mono';
    font-size: 0.875rem;
  }
}
</style>
