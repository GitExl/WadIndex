<template>
  <div class="app">
    <OffCanvas>
      <template v-slot:off>
        <NavMenu></NavMenu>
      </template>

      <template v-slot:on>

          <!-- <Suspense timeout="2000">
            <template #default> -->
              <NuxtPage></NuxtPage>
            <!-- </template>

            <template #fallback>
              <Layout type="one-column" class="app__loader">
                <img src="@/assets/images/skull.gif" width="150" height=150 />
              </Layout>
            </template>
          </Suspense> -->

        <PageFooter></PageFooter>
      </template>
    </OffCanvas>
  </div>
</template>

<script setup lang="ts">
useHead({
  titleTemplate: (subtitle: string | undefined) => {
    if (subtitle) {
      return subtitle + ' - The WAD Index';
    }
    return 'The WAD Index';
  }
})
</script>

<style lang="scss">
.app {
  width: 100vw;
  min-height: 100vh;

  &__loader {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }
}
</style>
