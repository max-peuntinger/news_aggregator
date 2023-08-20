<script>
  import { onMount } from 'svelte';

  let articles = [];

  onMount(async () => {
    const response = await fetch('http://localhost:8000/articles');
    articles = await response.json();
  });
</script>

<div class="container">
  <h1>Latest News Articles</h1>
  {#each articles as article}
    <div class="row">
      <div>
        <a href={article.link} target="_blank">{article.title}</a>
        <p>{@html article.summary}</p>
      </div>
    </div>
  {/each}
</div>
