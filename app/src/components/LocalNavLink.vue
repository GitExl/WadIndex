<template>
  <li class="local-nav-link">
    <a :href="href">
      <span v-if="icon" class="local-nav-link__icon material-icons-outlined">{{ icon }}</span>
      <span class="local-nav-link__link"><slot></slot></span>
      <span v-if="counter" class="local-nav-link__counter">{{ counter }}</span>
    </a>
  </li>
</template>

<script setup lang="ts">
export interface Props {
  href: string,
  icon?: string,
  counter?: number
}

const props = withDefaults(defineProps<Props>(), {
  icon: undefined,
  counter: undefined
});
</script>

<style lang="scss">
.local-nav-link {
  position: relative;

  a {
    display: block;
    text-decoration: none;
    padding: 0.425rem 2.5rem;
  }

  &__link {
    text-decoration: underline;
  }

  &__counter {
    font-size: 0.75rem;
    color: $color-accent;
    font-weight: 700;
    background-color: rgba($color-accent, 0.33);
    display: inline-block;
    line-height: 1;
    padding: 0.25rem 0.5rem 0.2rem 0.5rem;
    border-radius: 0.5rem;
    position: absolute;
    right: 0;
  }

  &__icon {
    font-size: 1.25rem;
    vertical-align: middle;
    color: $color-primary-light;
    margin-right: 0.75rem;
    position: absolute;
    left: 0;
  }
}
</style>
