from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from news_stream import start_stream
from nlp_processor import get_sentiment
from database import SessionLocal, Article
from clustering_utils import TfidfVectorizer, KMeans, Counter, nlp

from sqlalchemy import func
import asyncio
from contextlib import asynccontextmanager
import hashlib
from datetime import datetime, timedelta
import traceback

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

async def process_articles():
    print("Starting to process articles.....")
    db = SessionLocal()
    try:
        async for article_data in start_stream():
            article_text = article_data['text']
            article_source = article_data['source']
            
            article_hash = hashlib.md5(f"{article_text}{article_source}".encode()).hexdigest()
            
            existing_article = db.query(Article).filter(Article.hash == article_hash).first()
            
            if not existing_article:
                sentiment = get_sentiment(article_text)
                
                db_article = Article(
                    hash=article_hash,
                    text=article_text[:500],
                    sentiment=sentiment['compound'],
                    source=article_source
                )
                db.add(db_article)
                db.commit()
    except:
        print(traceback.format_exc())
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(process_articles())
    yield
    task.cancel()
    await task

app.router.lifespan_context = lifespan


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/trends")
async def trends(request: Request):
    return templates.TemplateResponse("trends.html", {"request": request})


@app.get("/sentiment")
async def sentiment(request: Request):
    return templates.TemplateResponse("sentiment.html", {"request": request})


@app.get("/topic-clusters")
async def topic_clusters(request: Request):
    return templates.TemplateResponse("topic_clusters.html", {"request": request})


@app.get("/api/trends")
async def getTrends(time_range: str = Query("1_day", pattern="^(1_day|1_week|1_month)$")):
    db = SessionLocal()
    try:
        if time_range == "1_day":
            from_date = datetime.now() - timedelta(days = 1)
        elif time_range == "1_week":
            from_date = datetime.now() - timedelta(weeks = 1)
        else:
            from_date = datetime.now() - timedelta(weeks = 4)
        trends = db.query(
            func.substring(Article.text, 1, 32).label('hash'),
            func.count(Article.id).label('count'),
            func.avg(Article.sentiment).label('avg_sentiment'),
            Article.source 
        ).filter(Article.timestamp >= from_date).group_by(func.substring(Article.text, 1, 32)).order_by(func.count(Article.id).desc()).limit(10).all()
        
        result = []
        for trend in trends:
            article = db.query(Article).filter(Article.text.like(f"{trend.hash}%")).first()
            if article:
                result.append({
                    "text": article.text,  
                    "count": trend.count,
                    "avg_sentiment": float(trend.avg_sentiment),
                    "source": trend.source  
                })
        return {"trends": result}
    finally:
        db.close()


@app.get("/api/sentiment")
async def getSentiment(time_range: str = Query("1_day", pattern="^(1_day|1_week|1_month)$")):
    db = SessionLocal()
    if time_range == "1_day":
        from_date = datetime.now() - timedelta(days = 1)
    elif time_range == "1_week":
        from_date = datetime.now() - timedelta(weeks = 1)
    else:
        from_date = datetime.now() - timedelta(weeks = 4)
    avg_sentiment = db.query(func.avg(Article.sentiment)).filter(Article.timestamp >= from_date).scalar()
    db.close()
    result = {"average_sentiment": avg_sentiment if avg_sentiment is not None else None}
    return result


@app.get("/api/topic-clusters")
async def getTopicClusters(
    n_clusters: int = 5, 
    top_n_words: int = 10,
    time_range: str = Query("1_day", pattern="^(1_day|1_week|1_month)$")):
    db = SessionLocal()
    try:

        if time_range == "1_day":
            from_date = datetime.now() - timedelta(days = 1)
        elif time_range == "1_week":
            from_date = datetime.now() - timedelta(weeks = 1)
        else:
            from_date = datetime.now() - timedelta(weeks = 4)


        articles = db.query(Article.text).filter(Article.timestamp >= from_date).all()
        texts = [article.text for article in articles]
        
        # Create a TF-IDF Vectorizer
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names_out()
        
        clusters = []
        for i in range(n_clusters):
            cluster_terms = [terms[ind] for ind in order_centroids[i, :top_n_words]]
            
            cluster_articles = [text for j, text in enumerate(texts) if kmeans.labels_[j] == i]
            
            entities = Counter()
            for article in cluster_articles:
                doc = nlp(article)
                entities.update([ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE']])
            
            top_entities = [{'entity': entity, 'count': count} 
                            for entity, count in entities.most_common(5)]
            
            clusters.append({
                "id": i,
                "terms": cluster_terms,
                "top_entities": top_entities,
                "article_count": len(cluster_articles)
            })
        
        return {"clusters": clusters}
    finally:
        db.close()

@app.get("/api/cluster-articles/{cluster_id}")
async def getClusterArticles(cluster_id: int, limit: int = 10):
    db = SessionLocal()
    try:
        articles = db.query(Article.text).all()
        texts = [article.text for article in articles]
        
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(X)
        
        cluster_articles = [text for i, text in enumerate(texts) if kmeans.labels_[i] == cluster_id]
        
        return {"articles": cluster_articles[:limit]}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)