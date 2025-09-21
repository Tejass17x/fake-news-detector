#!/usr/bin/env python3
"""
Professional Flask Web Application for Fake News Detector
Enhanced with real-time live news detection and professional UI
"""

from flask import Flask, render_template, request, jsonify, flash
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import schedule

from news_analyzer import NewsAnalyzer, NewsAnalysisResult
from config import Config
from logger import FakeNewsDetectorLogger

app = Flask(__name__)
app.secret_key = 'professional-fake-news-detector-2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
analyzer = NewsAnalyzer()
logger = FakeNewsDetectorLogger()

# Global variables for live monitoring
live_monitoring_active = False
monitored_sources = [
    {'name': 'BBC News', 'rss': 'http://feeds.bbci.co.uk/news/rss.xml', 'domain': 'bbc.com'},
    {'name': 'Reuters', 'rss': 'https://www.reuters.com/rssFeed/topNews', 'domain': 'reuters.com'},
    {'name': 'AP News', 'rss': 'https://rssfeed.app/rss/ap-news-top-stories', 'domain': 'apnews.com'},
    {'name': 'CNN', 'rss': 'http://rss.cnn.com/rss/edition.rss', 'domain': 'cnn.com'},
    {'name': 'NPR', 'rss': 'https://feeds.npr.org/1001/rss.xml', 'domain': 'npr.org'}
]

recent_analyses = []
live_stats = {
    'total_analyzed': 0,
    'high_credibility': 0,
    'medium_credibility': 0,
    'low_credibility': 0,
    'warnings_detected': 0,
    'bias_indicators': 0
}

@app.route('/')
def dashboard():
    """Professional dashboard with live monitoring"""
    return render_template('dashboard.html', 
                         live_stats=live_stats,
                         recent_analyses=recent_analyses[-10:],  # Show last 10
                         monitored_sources=monitored_sources)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Enhanced analysis endpoint with better error handling"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        analysis_type = data.get('type')
        
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
        
        # Log the analysis
        logger.log_analysis_complete(result, analysis_type, 
                                   url=data.get('url'), 
                                   title=title if 'title' in locals() else data.get('title'),
                                   content_length=len(content) if 'content' in locals() else 0)
        
        # Update live stats
        update_live_stats(result)
        
        # Add to recent analyses for dashboard
        add_to_recent_analyses(result, analysis_type, 
                             url=data.get('url'), 
                             title=title if 'title' in locals() else data.get('title'))
        
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
        
        # Emit real-time update to dashboard
        socketio.emit('new_analysis', {
            'result': result_dict,
            'stats': live_stats,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'result': result_dict
        })
    
    except Exception as e:
        logger.log_error(e, "analysis endpoint")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/live-monitoring', methods=['POST'])
def toggle_live_monitoring():
    """Start/stop live news monitoring"""
    global live_monitoring_active
    
    action = request.json.get('action')
    
    if action == 'start':
        live_monitoring_active = True
        start_live_monitoring()
        return jsonify({'status': 'started', 'message': 'Live monitoring started'})
    elif action == 'stop':
        live_monitoring_active = False
        return jsonify({'status': 'stopped', 'message': 'Live monitoring stopped'})
    else:
        return jsonify({'error': 'Invalid action. Use "start" or "stop"'}), 400

@app.route('/stats')
def get_stats():
    """Get current statistics"""
    return jsonify(live_stats)

@app.route('/recent-analyses')
def get_recent_analyses():
    """Get recent analyses"""
    return jsonify(recent_analyses[-20:])  # Last 20 analyses

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'message': 'Connected to Fake News Detector', 'stats': live_stats})

@socketio.on('request_stats')
def handle_stats_request():
    """Send current stats to client"""
    emit('stats_update', live_stats)

def extract_article_from_url(url: str) -> tuple:
    """Enhanced content extraction with better error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Enhanced title extraction
        title = None
        title_selectors = [
            'title', 'h1', '.title', '.headline', '.entry-title',
            '[property="og:title"]', '[name="twitter:title"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 10:  # Ensure meaningful title
                    break
        
        # Enhanced content extraction
        content = None
        content_selectors = [
            'article', '.article-content', '.post-content', '.entry-content',
            '.story-content', '.article-body', 'main', '.main-content', 
            '.content', '.story', '.post-body'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove unwanted elements
                for unwanted in element.select('script, style, nav, footer, header, .advertisement, .ads, .social-share'):
                    unwanted.decompose()
                content = element.get_text().strip()
                if content and len(content) > 100:  # Ensure substantial content
                    break
        
        # Fallback to paragraphs if no content found
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text().strip() for p in paragraphs[:15]])
        
        return title, content
        
    except Exception as e:
        logger.log_error(e, f"URL extraction: {url}")
        return None, None

def is_valid_url(url: str) -> bool:
    """Enhanced URL validation"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

def update_live_stats(result: NewsAnalysisResult):
    """Update live statistics"""
    global live_stats
    
    live_stats['total_analyzed'] += 1
    
    # Update credibility distribution
    if result.credibility_level == 'High':
        live_stats['high_credibility'] += 1
    elif result.credibility_level == 'Medium':
        live_stats['medium_credibility'] += 1
    else:
        live_stats['low_credibility'] += 1
    
    # Update warning and bias counts
    live_stats['warnings_detected'] += len(result.warning_flags)
    live_stats['bias_indicators'] += len(result.bias_indicators)

def add_to_recent_analyses(result: NewsAnalysisResult, analysis_type: str, url: str = None, title: str = None):
    """Add analysis to recent analyses list"""
    global recent_analyses
    
    analysis_summary = {
        'timestamp': result.analysis_timestamp,
        'type': analysis_type,
        'url': url,
        'title': title[:100] + '...' if title and len(title) > 100 else title,
        'credibility_level': result.credibility_level,
        'credibility_score': result.overall_credibility_score,
        'warning_count': len(result.warning_flags),
        'bias_count': len(result.bias_indicators)
    }
    
    recent_analyses.append(analysis_summary)
    
    # Keep only last 100 analyses
    if len(recent_analyses) > 100:
        recent_analyses = recent_analyses[-100:]

def fetch_rss_headlines(rss_url: str, source_name: str) -> list:
    """Fetch headlines from RSS feed"""
    try:
        import feedparser
        
        feed = feedparser.parse(rss_url)
        headlines = []
        
        for entry in feed.entries[:10]:  # Get latest 10 entries
            headlines.append({
                'title': entry.title,
                'link': entry.link if hasattr(entry, 'link') else '',
                'published': entry.published if hasattr(entry, 'published') else str(datetime.now()),
                'source': source_name
            })
        
        return headlines
    except Exception as e:
        logger.log_error(e, f"RSS fetch: {rss_url}")
        return []

def analyze_live_news():
    """Analyze live news from RSS feeds"""
    global live_monitoring_active
    
    while live_monitoring_active:
        try:
            for source in monitored_sources:
                if not live_monitoring_active:
                    break
                
                headlines = fetch_rss_headlines(source['rss'], source['name'])
                
                for headline in headlines[:3]:  # Analyze top 3 from each source
                    if not live_monitoring_active:
                        break
                    
                    try:
                        # Analyze the headline
                        result = analyzer.analyze_article(title=headline['title'])
                        
                        # Update stats
                        update_live_stats(result)
                        
                        # Add to recent analyses
                        add_to_recent_analyses(result, 'live_monitoring', 
                                             url=headline['link'], 
                                             title=headline['title'])
                        
                        # Emit real-time update
                        socketio.emit('live_analysis', {
                            'headline': headline,
                            'result': {
                                'credibility_level': result.credibility_level,
                                'credibility_score': result.overall_credibility_score,
                                'warning_flags': result.warning_flags,
                                'bias_indicators': result.bias_indicators
                            },
                            'stats': live_stats,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Rate limiting to avoid overwhelming APIs
                        time.sleep(5)
                        
                    except Exception as e:
                        logger.log_error(e, f"Live analysis: {headline['title']}")
                        continue
                
                # Wait between sources
                time.sleep(10)
            
            # Wait 5 minutes before next cycle
            if live_monitoring_active:
                time.sleep(300)
                
        except Exception as e:
            logger.log_error(e, "Live monitoring")
            time.sleep(60)

def start_live_monitoring():
    """Start live monitoring in background thread"""
    if not live_monitoring_active:
        return
    
    monitoring_thread = threading.Thread(target=analyze_live_news, daemon=True)
    monitoring_thread.start()

# Install feedparser if not already installed
try:
    import feedparser
except ImportError:
    print("Installing feedparser for RSS support...")
    import subprocess
    subprocess.check_call(["pip", "install", "feedparser"])
    import feedparser

if __name__ == '__main__':
    print("🚀 Starting Professional Fake News Detector with Live Monitoring...")
    print(f"📡 Dashboard available at: http://localhost:{Config.PORT}")
    print("🔴 Live monitoring ready - start from dashboard")
    print("🛑 Press Ctrl+C to stop")
    
    socketio.run(app, 
                host='0.0.0.0', 
                port=Config.PORT, 
                debug=Config.DEBUG,
                allow_unsafe_werkzeug=True)
