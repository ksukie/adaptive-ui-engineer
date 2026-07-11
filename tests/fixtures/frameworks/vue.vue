<script setup lang="ts">
defineProps<{ title: string }>();
</script>

<template>
  <article class="card">
    <h2>{{ title }}</h2>
  </article>
</template>

<style scoped>
.card { min-inline-size: 0; border-radius: var(--radius-card); }
</style>
