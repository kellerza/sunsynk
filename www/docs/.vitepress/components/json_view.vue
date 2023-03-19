<template>
  <json-viewer
    :value="props.value"
    copyable
    boxed
    expanded
    :expand-depth="4"
    theme="dark"
  />
</template>
<script setup lang="ts">
export interface PropDef {
  value: any;
}
const props = defineProps<PropDef>();
</script>
