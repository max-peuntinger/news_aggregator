<script>
  import { onMount } from 'svelte';

  let articles = [];

  onMount(async () => {
    const response = await fetch('http://localhost:8000/articles');
    articles = await response.json(); // Assign the JSON response to the articles variable
  });
</script>

<h1>Latest News Articles</h1>
<ul>
  {#each articles as article}
    <li>
      <a href={article.link} target="_blank">{article.title}</a>
      <p>{@html article.summary}</p> <!-- Use {@html} to render summary as HTML -->
    </li>
  {/each}
</ul>
