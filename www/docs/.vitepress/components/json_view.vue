<template>
  <json-viewer
    :value="value"
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
defineProps<PropDef>();
</script>
