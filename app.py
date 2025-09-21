#!/usr/bin/env python3
"""
Flask Web Application for Fake News Detector
Provides a web interface for analyzing news articles
"""

from flask import Flask, render_template, request, jsonify, flash
import json
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from news_analyzer import NewsAnalyzer, NewsAnalysisResult
from config import Config

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize the analyzer
analyzer = NewsAnalyzer()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze news article endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        analysis_type = data.get('type')  # 'url' or 'text'
        
        if analysis_type == 'url':
            url = data.get('url', '').strip()
            if not url:
                return jsonify({'error': 'URL is required'}), 400
            
            if not is_valid_url(url):
                return jsonify({'error': 'Invalid URL format'}), 400
            
            # Extract content from URL
            title, content = extract_article_from_url(url)
            
            if not title and not content:
                return jsonify({'error': 'Could not extract content from URL'}), 400
            
            # Analyze the article
            result = analyzer.analyze_article(url=url, title=title, content=content)
            
        elif analysis_type == 'text':
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
            if not title and not content:
                return jsonify({'error': 'Either title or content is required'}), 400
            
            # Analyze the text
            result = analyzer.analyze_article(title=title, content=content)
        
        else:
            return jsonify({'error': 'Invalid analysis type. Use "url" or "text"'}), 400
        
        # Convert result to dictionary for JSON response
        result_dict = {
            'overall_credibility_score': result.overall_credibility_score,
            'credibility_level': result.credibility_level,
            'sentiment_analysis': result.sentiment_analysis,
            'source_credibility': result.source_credibility,
            'content_analysis': result.content_analysis,
            'cross_reference_results': result.cross_reference_results,
            'fact_check_results': result.fact_check_results,
            'ai_analysis': result.ai_analysis,
            'bias_indicators': result.bias_indicators,
            'warning_flags': result.warning_flags,
            'recommendations': result.recommendations,
            'confidence_score': result.confidence_score,
            'analysis_timestamp': result.analysis_timestamp
        }
        
        return jsonify({
            'success': True,
            'result': result_dict
        })
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

def extract_article_from_url(url: str) -> tuple:
    """Extract title and content from a news article URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract title
        title = None
        title_tags = ['title', 'h1', '.title', '.headline', '[property="og:title"]']
        for tag in title_tags:
            element = soup.select_one(tag)
            if element:
                title = element.get_text().strip()
                break
        
        # Try to extract main content
        content = None
        content_selectors = [
            'article', '.article-content', '.post-content', '.entry-content',
            '.story-content', 'main', '.main-content', '.content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove unwanted elements
                for unwanted in element.select('script, style, nav, footer, header, .advertisement'):
                    unwanted.decompose()
                content = element.get_text().strip()
                break
        
        # If no content found, try paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text().strip() for p in paragraphs[:10]])  # First 10 paragraphs
        
        return title, content
        
    except Exception as e:
        print(f"Error extracting article from URL: {str(e)}")
        return None, None

def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )
