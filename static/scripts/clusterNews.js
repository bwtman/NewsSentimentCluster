document.addEventListener('DOMContentLoaded', () => {
    const timeRangeInputs = document.querySelectorAll('input[name="time_range"]');
    timeRangeInputs.forEach(input => input.addEventListener('change', updateTopicClusters));

    async function fetchTopicClusters(timeRange) {
        document.getElementById('loadingMessage').style.display = 'block';
        const response = await fetch(`/api/topic-clusters?time_range=${timeRange}`);
        const data = await response.json();
        document.getElementById('loadingMessage').style.display = 'none';
        return data.clusters;
    }

    async function updateTopicClusters() {
        document.getElementById('loadingMessage').style.display = 'block';

        const container = document.getElementById('clusterContainer');
        container.innerHTML = '';

        const timeRange = document.querySelector('input[name="time_range"]:checked').value;
        const data = await fetchTopicClusters(timeRange);

        data.forEach(cluster => {
            const clusterDiv = document.createElement('div');
            clusterDiv.className = 'cluster';
            
            const title = document.createElement('h2');
            title.textContent = `Cluster ${cluster.id + 1}`;
            clusterDiv.appendChild(title);
            
            const terms = document.createElement('p');
            terms.textContent = `Top terms: ${cluster.terms.join(', ')}`;
            clusterDiv.appendChild(terms);
            
            const entities = document.createElement('p');
            entities.textContent = `Top entities: ${cluster.top_entities.map(e => `${e.entity} (${e.count})`).join(', ')}`;
            clusterDiv.appendChild(entities);
            
            const count = document.createElement('p');
            count.textContent = `Articles in this cluster: ${cluster.article_count}`;
            clusterDiv.appendChild(count);
            
            const button = document.createElement('button');
            button.textContent = 'View Articles';
            button.onclick = () => viewClusterArticles(cluster.id);
            clusterDiv.appendChild(button);
            
            container.appendChild(clusterDiv);
        });

        document.getElementById('loadingMessage').style.display = 'none';
    }

    async function viewClusterArticles(clusterId) {
        const response = await fetch(`/api/cluster-articles/${clusterId}`);
        const data = await response.json();
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        
        const content = document.createElement('div');
        content.className = 'modal-content';
        
        const close = document.createElement('span');
        close.className = 'close';
        close.textContent = '×';
        close.onclick = () => modal.remove();
        content.appendChild(close);
        
        const title = document.createElement('h2');
        title.textContent = `Articles in Cluster ${clusterId + 1}`;
        content.appendChild(title);
        
        const list = document.createElement('ul');
        data.articles.forEach(article => {
            const item = document.createElement('li');
            item.textContent = article;
            list.appendChild(item);
        });
        content.appendChild(list);
        
        modal.appendChild(content);
        document.body.appendChild(modal);
    }
    
    updateTopicClusters();
});