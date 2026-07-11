<script lang="ts">
  export let title: string;
</script>

<article class="card">
  <h2>{title}</h2>
</article>

<style>
  .card { min-inline-size: 0; border-radius: var(--radius-card); }
</style>
