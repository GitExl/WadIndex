<template>
  <div class="wide-slider">
      <div ref="container" class="keen-slider">
        <div v-for="slide of slides" :key="slide.key" class="keen-slider__slide">
          <img :src="slide.imageUrl" :width="slide.imageWidth" :height="slide.imageHeight" loading="lazy" :style="{ 'aspect-ratio': slide.aspectRatio ?? 1 }">
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { useKeenSlider, type KeenSliderInstance } from 'keen-slider/vue.es';
import { ref, type Ref, onBeforeUnmount } from 'vue';

export interface WideSliderSlide {
  key: string
  imageUrl: string
  imageWidth: number
  imageHeight: number
  aspectRatio: number
}

let container: Ref<HTMLElement|undefined> = ref();
let slider: Ref<KeenSliderInstance|undefined> = ref();

const props = defineProps<{
  slides: WideSliderSlide[]
}>();

[container, slider] = useKeenSlider({
  loop: true,
  mode: 'snap',

  slides: {
    origin: 'center',
    perView: 1.25,
    spacing: 8,
  },

  breakpoints: {
    '(min-width: 35rem)': {
      slides: {
        origin: 'center',
        perView: 2.25,
        spacing: 16,
      },
    },
    '(min-width: 60rem)': {
      slides: {
        origin: 'center',
        perView: 3.25,
        spacing: 32,
      },
    },
  },
}, []);

onBeforeUnmount(() => {
  slider.value?.destroy();
});
</script>

<style lang="scss">
.wide-slider {
  width: 100vw;
  background-color: rgba($color-primary-dark, 0.33);
  cursor: pointer;

  img {
    width: 100%;
    height: auto;
    image-rendering: pixelated;
  }
}
</style>
