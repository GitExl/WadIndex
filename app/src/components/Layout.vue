<template>
  <div class="layout" :class="{['layout--' + props.type]: true}">
    <div class="layout__start"><slot name="start"></slot></div>
    <div class="layout__middle"><slot></slot></div>
    <div class="layout__end"><slot name="end"></slot></div>
  </div>
</template>

<script setup lang="ts">
export interface Props {
  type?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'one-column',
});
</script>

<style lang="scss">
.layout {
  display: grid;
  grid-template-columns: 1fr minmax(0, $layout-max-width) 1fr;
  grid-template-rows: 1fr;
  grid-column-gap: 2.5rem;
  grid-row-gap: 0px;
  width: 100%;
  padding-left: $nav-width;

  @media (min-width: 100rem) {
    grid-column-gap: 5rem;
  }

  &__left {
    grid-area: 1 / 1 / 2 / 2;
  }

  &__right {
    grid-area: 1 / 3 / 2 / 4;
  }

  &__middle {
    grid-area: 1 / 2 / 6 / 3;
    gap: 0.5rem;
    columns: 1;
    display: relative;

    @media (min-width: 60rem) {
      gap: 1rem;
    }
  }

  &--two-column {
    @media (min-width: 100rem) {
      grid-template-columns: 1fr minmax(0, $layout-max-width-wide) 1fr;
    }

    .layout__middle {
      columns: 2;

      @media (min-width: 100rem) {
        max-width: 100rem;
        display: flex;
        flex-direction: row;

        > * {
          width: 50%;
        }
      }
    }
  }

}
</style>
