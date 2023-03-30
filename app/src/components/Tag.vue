<template>
  <span class="tag" :class="{['tag--' + props.type]: true}">
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
interface Props {
  type?: string,
}

const props = withDefaults(defineProps<Props>(), {
  type: 'normal',
})
</script>

<style lang="scss">
.tag {
  font-family: 'DejaVu Sans Condensed', sans-serif;
  display: inline-block;
  background-color: $color-accent;
  color: #000;
  padding: 0.1rem 0.65rem;
  border-radius: 0.5rem;
  line-height: 1;
  font-size: 0.75rem;
  font-weight: 700;
  margin-right: 0.25rem;
  vertical-align: text-top;

  &--large {
    padding: 0.2rem 0.85rem;
    border-radius: 0.75rem;
    font-size: 0.9rem;
  }
}
</style>
