#!/usr/bin/env python3
"""
Command Line Interface for Fake News Detector
Provides interactive CLI for analyzing news articles
"""

import argparse
import sys
import json
from typing import Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from news_analyzer import NewsAnalyzer, NewsAnalysisResult
from config import Config

class NewsDetectorCLI:
    """Command line interface for the fake news detector"""
    
    def __init__(self):
        self.analyzer = NewsAnalyzer()
    
    def extract_article_from_url(self, url: str) -> tuple[Optional[str], Optional[str]]:
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
    
    def format_analysis_result(self, result: NewsAnalysisResult) -> str:
        """Format the analysis result for display"""
        output = []
        output.append("=" * 80)
        output.append("FAKE NEWS DETECTOR - ANALYSIS RESULTS")
        output.append("=" * 80)
        
        # Overall score
        output.append(f"\n📊 OVERALL CREDIBILITY: {result.credibility_level.upper()}")
        output.append(f"📈 Credibility Score: {result.overall_credibility_score:.2f}/1.00")
        output.append(f"🔍 Confidence Level: {result.confidence_score:.2f}/1.00")
        
        # Warning flags
        if result.warning_flags:
            output.append("\n⚠️  WARNING FLAGS:")
            for flag in result.warning_flags:
                output.append(f"   • {flag}")
        
        # Source analysis
        if result.source_credibility:
            output.append("\n🌐 SOURCE ANALYSIS:")
            source = result.source_credibility
            if 'domain' in source:
                output.append(f"   Domain: {source['domain']}")
            if 'is_https' in source:
                output.append(f"   HTTPS: {'✓' if source['is_https'] else '✗'}")
            if 'bias_check' in source:
                bias = source['bias_check']
                output.append(f"   Credibility: {bias.get('credibility', 'Unknown')}")
                output.append(f"   Bias Rating: {bias.get('bias_rating', 'Unknown')}")
        
        # Content analysis
        if result.content_analysis:
            output.append("\n📝 CONTENT ANALYSIS:")
            content = result.content_analysis
            output.append(f"   Word Count: {content.get('word_count', 'Unknown')}")
            output.append(f"   Sentence Count: {content.get('sentence_count', 'Unknown')}")
            
            if content.get('keywords'):
                output.append(f"   Keywords: {', '.join(content['keywords'][:5])}")
            
            if content.get('suspicious_patterns'):
                output.append("   Suspicious Patterns:")
                for pattern in content['suspicious_patterns']:
                    output.append(f"     • {pattern}")
        
        # Sentiment analysis
        if result.sentiment_analysis and not result.sentiment_analysis.get('error'):
            output.append("\n💭 SENTIMENT ANALYSIS:")
            sentiment = result.sentiment_analysis
            output.append(f"   Overall Sentiment: {sentiment.get('sentiment', 'Unknown').title()}")
            output.append(f"   Polarity: {sentiment.get('polarity', 0):.2f} (-1 to 1)")
            output.append(f"   Subjectivity: {sentiment.get('subjectivity', 0):.2f} (0 to 1)")
        
        # Cross-reference results
        if result.cross_reference_results and not result.cross_reference_results.get('error'):
            output.append("\n🔄 CROSS-REFERENCE CHECK:")
            cross_ref = result.cross_reference_results
            output.append(f"   Consensus Score: {cross_ref.get('consensus_score', 0):.2f}/1.00")
            output.append(f"   Source Diversity: {cross_ref.get('source_diversity', 0)} sources")
            
            similar = cross_ref.get('similar_articles', [])
            if similar:
                output.append(f"   Similar Articles Found: {len(similar)}")
                for i, article in enumerate(similar[:3], 1):
                    output.append(f"     {i}. {article.get('source', 'Unknown')}: {article.get('title', '')[:60]}...")
        
        # AI Analysis Results
        if result.ai_analysis and result.ai_analysis.get('status') == 'success':
            output.append("\n🤖 AI ANALYSIS:")
            ai = result.ai_analysis
            if 'credibility_level' in ai:
                output.append(f"   AI Assessment: {ai['credibility_level']}")
            if 'credibility_score' in ai:
                output.append(f"   AI Score: {ai['credibility_score']:.2f}/1.00")
            if 'key_findings' in ai and ai['key_findings']:
                output.append("   Key Findings:")
                for finding in ai['key_findings'][:3]:
                    output.append(f"     • {finding}")
            if 'red_flags' in ai and ai['red_flags']:
                output.append("   AI Red Flags:")
                for flag in ai['red_flags'][:3]:
                    output.append(f"     • {flag}")
        
        # Bias indicators
        if result.bias_indicators:
            output.append("\n🎯 BIAS INDICATORS:")
            for indicator in result.bias_indicators[:5]:
                output.append(f"   • {indicator}")
            if len(result.bias_indicators) > 5:
                output.append(f"   ... and {len(result.bias_indicators) - 5} more")
        
        # Recommendations
        output.append("\n💡 RECOMMENDATIONS:")
        for rec in result.recommendations:
            output.append(f"   • {rec}")
        
        # Timestamp
        output.append(f"\n⏰ Analysis completed at: {result.analysis_timestamp}")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def analyze_url(self, url: str) -> None:
        """Analyze a news article from URL"""
        print(f"\n🔍 Analyzing article from: {url}")
        print("📥 Extracting content...")
        
        title, content = self.extract_article_from_url(url)
        
        if not title and not content:
            print("❌ Could not extract content from the URL. Please try with a different URL or provide text manually.")
            return
        
        if title:
            print(f"📰 Title: {title[:100]}...")
        if content:
            print(f"📄 Content extracted ({len(content)} characters)")
        
        print("\n🤖 Analyzing...")
        try:
            result = self.analyzer.analyze_article(url=url, title=title, content=content)
            print(self.format_analysis_result(result))
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
    
    def analyze_text(self, title: str, content: str = None) -> None:
        """Analyze news text directly"""
        print(f"\n🔍 Analyzing text: {title[:100]}...")
        print("🤖 Analyzing...")
        
        try:
            result = self.analyzer.analyze_article(title=title, content=content)
            print(self.format_analysis_result(result))
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
    
    def interactive_mode(self) -> None:
        """Run interactive mode"""
        print("\n🚀 Welcome to Fake News Detector - Interactive Mode")
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("fake-news-detector> ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() in ['help', 'h']:
                    self.show_help()
                elif user_input.startswith('url '):
                    url = user_input[4:].strip()
                    if self.is_valid_url(url):
                        self.analyze_url(url)
                    else:
                        print("❌ Invalid URL format")
                elif user_input.startswith('text '):
                    text = user_input[5:].strip()
                    if text:
                        self.analyze_text(text)
                    else:
                        print("❌ Please provide text to analyze")
                else:
                    # Assume it's a URL or text
                    if self.is_valid_url(user_input):
                        self.analyze_url(user_input)
                    elif user_input:
                        self.analyze_text(user_input)
                    else:
                        print("❌ Please provide a URL or text to analyze. Type 'help' for instructions.")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def show_help(self) -> None:
        """Show help information"""
        print("""
📋 FAKE NEWS DETECTOR - HELP
        
🔗 Analyze URL:
   url <URL>        - Analyze news article from URL
   <URL>           - Direct URL input
   
📝 Analyze Text:
   text <TEXT>     - Analyze news headline or content
   <TEXT>          - Direct text input
   
🔧 Commands:
   help, h         - Show this help
   exit, quit, q   - Exit the program
   
📖 Examples:
   url https://example.com/news/article
   text Breaking: Major event happens in city
   """)
    
    def is_valid_url(self, url: str) -> bool:
        """Check if string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Professional Fake News Detector - Analyze news articles for credibility",
        epilog="Example: python cli.py --url https://example.com/news/article"
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--url', '-u', help='URL of the news article to analyze')
    group.add_argument('--text', '-t', help='Text content to analyze')
    group.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    parser.add_argument('--title', help='Article title (use with --text)')
    parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    cli = NewsDetectorCLI()
    
    # Check if no arguments provided
    if len(sys.argv) == 1 or args.interactive:
        cli.interactive_mode()
        return
    
    # URL analysis
    if args.url:
        if not cli.is_valid_url(args.url):
            print("❌ Invalid URL format")
            sys.exit(1)
        cli.analyze_url(args.url)
    
    # Text analysis
    elif args.text:
        cli.analyze_text(args.text, args.title)
    
    else:
        print("❌ Please provide either --url, --text, or use --interactive mode")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
