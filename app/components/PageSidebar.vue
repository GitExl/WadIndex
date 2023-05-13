<template>
  <aside class="page-sidebar">
    <slot></slot>
  </aside>
</template>

<style lang="scss">
.page-sidebar {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  position: sticky;
  top: 3rem;
}
</style>
