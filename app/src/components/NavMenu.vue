<script setup lang="ts">
</script>

<template>
  <div class="nav-menu">
    <ul>
      <li><router-link to="/">Home</router-link></li>
      <li><router-link to="/search">Search</router-link></li>
      <li><router-link to="/browse">Browse</router-link></li>
      <li><router-link to="/queue">Music queue</router-link></li>
      <li><router-link to="/about">About</router-link></li>
    </ul>
  </div>
</template>

<style lang="scss">
$top: 6rem;

.nav-menu {
  padding: 1rem;
  padding-top: $top;
  background-color: rgba($color-primary-dark, 0.8);
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

    &.router-link-active {
      font-weight: 700;
    }
  }
}
</style>
