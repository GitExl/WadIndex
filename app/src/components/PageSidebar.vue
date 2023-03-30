<template>
  <div class="page-sidebar">
    <ul class="page-sidebar__inset">
      <slot></slot>
    </ul>
  </div>
</template>

<style lang="scss">
.page-sidebar {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  position: sticky;
  top: 3rem;

  &__inset {
    width: 100%;
    max-width: 11rem;
    list-style: none;
    padding: 0;
  }
}
</style>
