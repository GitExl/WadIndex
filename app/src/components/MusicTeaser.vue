<template>

  <InfoBlock :id="'music-' + music.name" class="music-teaser">

    <InfoBlockRow header :to="link">
      <div class="music-teaser__monospaced">{{ music.name }}</div>
      <div>
        &nbsp;
      </div>
    </InfoBlockRow>

    <InfoBlockRow v-if="music.duration">
      <div>Duration</div>
      <div>{{ formattedDuration }}</div>
    </InfoBlockRow>

    <InfoBlockRow>
      <div>Type</div>
      <div>{{ music.type.toUpperCase() }}</div>
    </InfoBlockRow>

  </InfoBlock>

</template>

<script setup lang="ts">
import type { MusicTeaserData } from '@/data/MusicTeaser';
import { computed } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import InfoBlock from './InfoBlock.vue';
import InfoBlockRow from './InfoBlockRow.vue';
import Tag from './Tag.vue';

const props = defineProps<{
  music: MusicTeaserData
}>()

const link = computed((): RouteLocationRaw => {
  return {
    path: '/music/' + props.music.hash + '/',
  };
});

const formattedDuration = computed((): string|undefined => {
  if (!props.music.duration) {
    return undefined;
  }

  const minutes = Math.floor(props.music.duration / 60);
  const seconds = props.music.duration % 60;
  if (seconds < 10) {
    return minutes + ':0' + seconds;
  }

  return minutes + ':' + seconds;
});
</script>

<style lang="scss">
.music-teaser {
  &__monospaced {
    font-family: 'Noto Mono';
    font-size: 0.875rem;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
  }
}
</style>
