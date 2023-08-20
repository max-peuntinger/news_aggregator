<script>
  import { onMount } from 'svelte';

  let articles = [];
  let selectedCategory = 'All';
  let categories = ['All'];

  onMount(async () => {
    const response = await fetch('http://localhost:8000/articles');
    articles = await response.json();
    categories = ['All', ...new Set(articles.map(article => formatCategory(article.topic.split('/').pop())).filter(Boolean))];
  });

  $: filteredArticles = selectedCategory === 'All'
    ? articles
    : articles.filter(article => formatCategory(article.topic.split('/').pop()) === selectedCategory);

  function formatCategory(category) {
    return category
      .replace(/_/g, ' ')
      .replace(/\b\w/g, char => char.toUpperCase());
  }
</script>

<div>
  <select bind:value={selectedCategory}>
    {#each categories as category}
      <option value={category}>{category}</option>
    {/each}
  </select>
</div>
<div class="container">
  <h1>Latest News Articles</h1>
  {#each filteredArticles as article}
    <div class="row">
      <span class="category">{formatCategory(article.topic.split('/').pop())}</span> <!-- Display formatted category -->
      <div>
        <a href={article.link} target="_blank">{article.title}</a>
        <p>{@html article.summary}</p>
      </div>
    </div>
  {/each}
</div>

<!-- Optional styling for the category -->
<style>
  .category {
    font-weight: bold;
    margin-right: 10px;
  }
</style>
