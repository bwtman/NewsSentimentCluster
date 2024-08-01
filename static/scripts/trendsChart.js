let trendsChart;

document.querySelectorAll('input[name="time_range"]').forEach(input => {
    input.addEventListener('change', updateCharts);
});

function getFirstWords(text) {
    const words = text.split(' ');
    return words.length <= 4 ? text : words.slice(0, 4).join(' ') + '...';
}

function getEmotionalTone(score) {
    if (score >= 0.05) {
        return 'Emotional tone - Positive';
    } else if (score > -0.05 && score < 0.05) {
        return 'Emotional tone - Neutral';
    } else {
        return 'Emotional tone - Negative';
    }
}

async function updateCharts() {
    const timeRange = document.querySelector('input[name="time_range"]:checked').value;

    const trendsResponse = await fetch(`/api/trends?time_range=${timeRange}`);
    const trendsData = await trendsResponse.json();

    const sentimentResponse = await fetch(`/api/sentiment?time_range=${timeRange}`);
    const sentimentData = await sentimentResponse.json();

    const labels = trendsData.trends.map(t => ({
        label: getFirstWords(t.text),
        fullText: t.text,
        score: t.avg_sentiment
    }));
    const counts = trendsData.trends.map(t => t.count);
    const sentiments = trendsData.trends.map(t => t.avg_sentiment);

    if (trendsChart) {
        trendsChart.data.labels = labels.map(l => l.label);
        trendsChart.data.datasets[0].data = counts;
        trendsChart.data.datasets[1].data = sentiments;
        trendsChart.update();
    } else {
        const ctx = document.getElementById('trendsChart').getContext('2d');
        trendsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.map(l => l.label),
                datasets: [{
                    label: 'Number of occurrences',
                    data: counts,
                    backgroundColor: 'rgba(60, 98, 194, 0.63)',
                    borderColor: 'rgba(60, 98, 194, 1)',
                    borderWidth: 1,
                    yAxisID: 'y-axis-1',
                }, {
                    label: 'Average Sentiment',
                    data: sentiments,
                    type: 'line',
                    backgroundColor: 'rgba(228, 10, 0, 0.33)',
                    borderColor: 'rgba(228, 10, 0, 0.63)',
                    borderWidth: 1.5,
                    yAxisID: 'y-axis-2',

                }]
            },
            options: {
                scales: {
                    'y-axis-1': {
                        type: 'linear',
                        position: 'left',
                    },
                    'y-axis-2': {
                        type: 'linear',
                        position: 'right',
                        ticks: {
                            max: 1,
                            min: -1
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                const index = tooltipItems[0].dataIndex;
                                const fullText = labels[index].fullText;
                                const score = labels[index].score;
                                const tone = getEmotionalTone(score);

                                const words = fullText.split(' ');
                                let lines = [];
                                let line = '';
                                for (let i = 0; i < words.length; i++) {
                                    if (line.length + words[i].length > 30) {
                                        lines.push(line);
                                        line = '';
                                    }
                                    line += (line ? ' ' : '') + words[i];
                                }
                                if (line) {
                                    lines.push(line);
                                }
                                lines.push('');
                                lines.push(tone);
                                return lines;
                            }
                        }
                    }
                }
            }
        });
    }

    const sentimentElement = document.getElementById('sentiment');
    if (sentimentData.average_sentiment !== null && sentimentData.average_sentiment !== undefined) {
        sentimentElement.textContent = sentimentData.average_sentiment.toFixed(2);
    } else {
        sentimentElement.textContent = 'No data';
    }
}

updateCharts();
setInterval(updateCharts, 5000);