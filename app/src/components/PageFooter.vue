<template>
  <footer class="page-footer">
    <div class="page-footer__content">
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
        labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
        laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
        voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
        cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>

      <p>&copy; 2023 Dennis Meuwissen</p>
    </div>
  </footer>
</template>

<style lang="scss">
.page-footer {
  background-color: #000;
  padding: 2rem 0;
  margin-left: $nav-width;

  &__content {
    margin: 0 auto;
    max-width: $layout-max-width;
    font-size: 0.75rem;
    color: #666;
  }

  p {
    margin-bottom: 2rem;

    &:last-child {
      margin-bottom: 0;
    }
  }
}
</style>
