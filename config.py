import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the Fake News Detector"""
    
    # API Keys
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
    GOOGLE_CSE_ID = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # API URLs
    NEWS_API_URL = "https://newsapi.org/v2"
    GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    FACT_CHECK_TOOLS_URL = "https://toolbox.google.com/factcheck/explorer/search"
    
    # Credibility scoring thresholds
    HIGH_CREDIBILITY_THRESHOLD = 0.8
    MEDIUM_CREDIBILITY_THRESHOLD = 0.5
    LOW_CREDIBILITY_THRESHOLD = 0.3
    
    # Known reliable news sources (can be expanded)
    RELIABLE_SOURCES = [
        'reuters.com', 'ap.org', 'bbc.com', 'npr.org', 'pbs.org',
        'wsj.com', 'nytimes.com', 'washingtonpost.com', 'theguardian.com',
        'cnn.com', 'abcnews.go.com', 'cbsnews.com', 'nbcnews.com'
    ]
    
    # Known unreliable or biased sources
    UNRELIABLE_SOURCES = [
        'infowars.com', 'breitbart.com', 'theonion.com', 'satirewire.com',
        'clickhole.com', 'reductress.com'  # Some satirical sites included
    ]
    
    # Bias indicators (words that might suggest bias)
    BIAS_INDICATORS = [
        'shocking', 'unbelievable', 'exclusive', 'breaking exclusive',
        'you won\'t believe', 'doctors hate this', 'they don\'t want you to know',
        'mainstream media', 'fake news', 'conspiracy'
    ]
