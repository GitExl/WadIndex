<template>
  <div class="playlist">
    <ul>
      <li class="playlist__item">
        <span class="playlist__item-status"></span>
        <h3>Title of Track or name or whatever</h3>
        <span>3:11</span>
        <span class="playlist__item-menu">⋯</span>
      </li>
      <li class="playlist__item">
        <span class="playlist__item-status"></span>
        <h3>Title of Track or name or whatever</h3>
        <span>3:11</span>
        <span class="playlist__item-menu">⋯</span>
      </li>
      <li class="playlist__item">
        <span class="playlist__item-status"></span>
        <h3>Title of Track or name or whatever</h3>
        <span>3:11</span>
        <span class="playlist__item-menu">⋯</span>
      </li>
      <li class="playlist__item playlist__item--selected">
        <span class="playlist__item-status"></span>
        <h3>Title of Track or name or whatever</h3>
        <span>3:11</span>
        <span class="playlist__item-menu">⋯</span>
      </li>
      <li class="playlist__item">
        <span class="playlist__item-status"></span>
        <h3>Title of Track or name or whatever</h3>
        <span>3:11</span>
        <span class="playlist__item-menu">⋯</span>
      </li>
      <li class="playlist__item">
        <span class="playlist__item-status">⏵</span>
        <h3>Title of Track or name or whatever</h3>
        <span>3:11</span>
        <span class="playlist__item-menu">⋯</span>
      </li>
      <li class="playlist__item">
        <span class="playlist__item-status"></span>
        <h3>Title of Track or name or whatever</h3>
        <span>3:11</span>
        <span class="playlist__item-menu">⋯</span>
      </li>
    </ul>
  </div>
</template>

<style lang="scss">
.playlist {
  width: 100%;
  height: 100%;
  max-width: 40rem;

  ul {
    padding: 0;
    list-style: none;
  }

  .playlist__item {
    padding: 0.25rem 0.5rem;
    display: flex;
    flex-direction: row;
    cursor: pointer;

    &:hover {
      background-color: #124;

      .playlist__item-menu {
        visibility: visible;
      }
    }

    &--selected {
      background-color: #248;
    }
  }

  .playlist__item-status {
    width: 1.5rem;
    text-align: center;
  }

  .playlist__item-menu {
    width: 1.5rem;
    text-align: center;
    margin-left: 0.5rem;
    visibility: hidden;
  }

  h3 {
    font-size: 1rem;
    font-weight: 300;
    margin: 0;
    flex: 1;
  }

  span {
    margin: 0;
  }
}
</style>
