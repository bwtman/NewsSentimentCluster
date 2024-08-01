document.querySelectorAll('input[name="time_range"]').forEach(input => {
    input.addEventListener('change', updateTrendingArticles);
})
async function updateTrendingArticles() {
    const timeRange = document.querySelector('input[name="time_range"]:checked').value;
    
    const response = await fetch(`/api/trends?time_range=${timeRange}`);
    const data = await response.json();
    const trendingArticlesElement = document.getElementById('trendingArticles');
    trendingArticlesElement.innerHTML = '';

    data.trends.forEach(trend => {
        const listItem = document.createElement('li');
        listItem.textContent = `${trend.text} (${trend.count} occurrences)`;
        trendingArticlesElement.appendChild(listItem);
    });
}

updateTrendingArticles();
setInterval(updateTrendingArticles, 5000);