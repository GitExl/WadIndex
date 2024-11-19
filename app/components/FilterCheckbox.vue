<template>
  <li class="filter-checkbox">
    <input :id="name + '-' + value" :name="name" type="checkbox" v-model="model" :value="value">
    <label :for="name + '-' + value">{{ label }}</label>
  </li>
</template>

<script setup lang="ts">
const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
  value: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Array<string>,
  }
});

const emit = defineEmits(['update:modelValue']);

const model = computed({
  get: () => props.modelValue,
  set: item => emit('update:modelValue', item)
});
</script>

<style lang="scss">
.filter-checkbox {
  margin: 0.25rem 0;

  label {
    color: $color-primary-light;
    margin-left: 0.5rem;
    cursor: pointer;
  }

  input {
    cursor: pointer;
  }
}
</style>
