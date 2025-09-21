import requests
import json
import time
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus, urlparse
from config import Config

class NewsAPIClient:
    """Client for NewsAPI.org - provides news articles and sources"""
    
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = Config.NEWS_API_URL
    
    def search_articles(self, query: str, language: str = 'en', page_size: int = 10) -> Dict[str, Any]:
        """Search for news articles related to a query"""
        if not self.api_key:
            return {"status": "error", "message": "NewsAPI key not configured"}
        
        url = f"{self.base_url}/everything"
        params = {
            'q': query,
            'language': language,
            'pageSize': page_size,
            'sortBy': 'publishedAt',
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"NewsAPI request failed: {str(e)}"}
    
    def get_sources(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get available news sources"""
        if not self.api_key:
            return {"status": "error", "message": "NewsAPI key not configured"}
        
        url = f"{self.base_url}/sources"
        params = {'apiKey': self.api_key}
        if category:
            params['category'] = category
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"NewsAPI sources request failed: {str(e)}"}

class GoogleFactCheckClient:
    """Client for Google Fact Check Tools API"""
    
    def __init__(self):
        self.api_key = Config.GOOGLE_CSE_API_KEY
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    def search_fact_checks(self, query: str, language_code: str = 'en') -> Dict[str, Any]:
        """Search for fact checks related to a claim"""
        if not self.api_key:
            return {"status": "error", "message": "Google API key not configured"}
        
        params = {
            'query': query,
            'languageCode': language_code,
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"Fact check request failed: {str(e)}"}

class GoogleCustomSearchClient:
    """Client for Google Custom Search API"""
    
    def __init__(self):
        self.api_key = Config.GOOGLE_CSE_API_KEY
        self.cse_id = Config.GOOGLE_CSE_ID
        self.base_url = Config.GOOGLE_CSE_URL
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Search for information using Google Custom Search"""
        if not self.api_key or not self.cse_id:
            return {"status": "error", "message": "Google Custom Search not configured"}
        
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': min(num_results, 10)  # Max 10 per request for free tier
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"Google search request failed: {str(e)}"}

class FreeTextAnalysisClient:
    """Client for free text analysis using local processing and free APIs"""
    
    @staticmethod
    def analyze_sentiment_textblob(text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob (free local processing)"""
        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
            subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "confidence": abs(polarity)
            }
        except Exception as e:
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
        """Extract keywords using NLTK (free local processing)"""
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from nltk.probability import FreqDist
            from collections import Counter
            
            # Download required NLTK data (if not already present)
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
            
            # Tokenize and remove stopwords
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
            
            # Get most frequent words
            freq_dist = Counter(filtered_tokens)
            keywords = [word for word, _ in freq_dist.most_common(num_keywords)]
            
            return keywords
        except Exception as e:
            print(f"Keyword extraction failed: {str(e)}")
            return []

class MediaBiasFactCheckClient:
    """Client for checking media bias using free web scraping"""
    
    @staticmethod
    def check_source_bias(domain: str) -> Dict[str, Any]:
        """
        Check media bias by analyzing source domain
        This is a simplified implementation that could be enhanced with web scraping
        """
        try:
            # Check against known reliable/unreliable sources
            if any(reliable in domain.lower() for reliable in Config.RELIABLE_SOURCES):
                return {
                    "bias_rating": "minimal",
                    "credibility": "high",
                    "confidence": 0.8
                }
            elif any(unreliable in domain.lower() for unreliable in Config.UNRELIABLE_SOURCES):
                return {
                    "bias_rating": "high",
                    "credibility": "low",
                    "confidence": 0.9
                }
            else:
                return {
                    "bias_rating": "unknown",
                    "credibility": "unknown",
                    "confidence": 0.3
                }
        except Exception as e:
            return {"error": f"Bias check failed: {str(e)}"}

class CrossReferenceClient:
    """Client for cross-referencing news across multiple sources"""
    
    def __init__(self):
        self.news_api = NewsAPIClient()
        self.google_search = GoogleCustomSearchClient()
    
    def cross_reference_story(self, headline: str, content: str) -> Dict[str, Any]:
        """Cross-reference a news story across multiple sources"""
        results = {
            "similar_articles": [],
            "contradiction_indicators": [],
            "consensus_score": 0.0,
            "source_diversity": 0
        }
        
        try:
            # Search for similar articles using NewsAPI
            news_results = self.news_api.search_articles(headline)
            
            if news_results.get("status") == "ok" and news_results.get("articles"):
                similar_count = 0
                sources = set()
                
                for article in news_results["articles"][:10]:
                    if article.get("title") and article.get("source"):
                        sources.add(article["source"]["name"])
                        similar_count += 1
                        
                        results["similar_articles"].append({
                            "title": article["title"],
                            "source": article["source"]["name"],
                            "url": article["url"],
                            "published_at": article.get("publishedAt")
                        })
                
                results["source_diversity"] = len(sources)
                results["consensus_score"] = min(similar_count / 5.0, 1.0)  # Normalize to 0-1
            
            # Additional Google search for broader context
            search_results = self.google_search.search(headline)
            if search_results.get("items"):
                for item in search_results["items"][:5]:
                    domain = urlparse(item["link"]).netlify
                    results["similar_articles"].append({
                        "title": item["title"],
                        "source": domain,
                        "url": item["link"],
                        "snippet": item.get("snippet", "")
                    })
        
        except Exception as e:
            results["error"] = f"Cross-reference failed: {str(e)}"
        
        return results
