# News Trend Analyzer

**News Trend Analyzer**  is a web application that streams, processes, and analyzes news articles to uncover trends in sentiment and topics. It features real-time news updates, sentiment analysis, and topic clustering to help visualize and understand emerging news trends. With interactive charts, users can explore how news topics and sentiments change over time.


## Stack

- **FastAPI**
- **SQLAlchemy**
- **NLTK**
- **scikit-learn**
- **Chart.js**
- **[NewsAPI](https://newsapi.org/)**

## Setup Instructions

1. **Clone the Repository**
    ```bash
    git clone https://github.com/bwtman/NewsSentimentCluster.git
    cd NewsSentimentCluster
    ```

2. **Create and Activate Virtual Environment**
    ```bash
    python -m venv venv
    venv\Scripts\activate # on Linux and macOS use: source venv/bin/activate
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Add NewsAPI API Key**
    - Create `.env` file. Open it and add your NewsAPI key:

    ```
    NEWS_API_KEY=your_news_api_key_here
    ```

5. **Run the Application**
    ```bash
    python main.py
    ```

The application will be available at `http://localhost:8000/`.
