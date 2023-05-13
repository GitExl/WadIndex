<script setup lang="ts">
</script>

<template>
  <nav class="nav-menu">
    <ul>
      <li><NuxtLink to="/">Home</NuxtLink></li>
      <li><NuxtLink to="/search">Search</NuxtLink></li>
      <li><NuxtLink to="/browse">Browse</NuxtLink></li>
      <li><NuxtLink to="/queue">Music queue</NuxtLink></li>
      <li><NuxtLink to="/about">About</NuxtLink></li>
    </ul>
  </nav>
</template>

<style lang="scss">
$top: 6rem;

.nav-menu {
  padding: 1rem;
  padding-top: $top;
  background-color: rgba($color-primary-dark, 0.66);
  width: $nav-width;
  height: 100%;
  backdrop-filter: blur(1rem);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;

  ul {
    padding: 0;
    margin: 0;
    list-style: none;
  }

  a {
    @include rect;

    display: block;
    padding: 0.625rem;

    text-decoration: none;
    font-family: 'DejaVu Sans', sans-serif;
    font-size: 1rem;
    font-weight: 200;
    line-height: 1;

    &.NuxtLink-active {
      font-weight: 700;
    }
  }
}
</style>
