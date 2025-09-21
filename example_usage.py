#!/usr/bin/env python3
"""
Example Usage Script for Fake News Detector
Demonstrates various ways to use the fake news detection system
"""

from news_analyzer import NewsAnalyzer
from logger import FakeNewsDetectorLogger
import json

def example_url_analysis():
    """Example: Analyze a news article from URL"""
    print("🔍 Example 1: URL Analysis")
    print("-" * 50)
    
    analyzer = NewsAnalyzer()
    logger = FakeNewsDetectorLogger()
    
    # Example URLs (replace with actual news URLs)
    test_urls = [
        "https://www.bbc.com/news",  # Reliable source
        "https://www.reuters.com/world",  # Reliable source
        # Add more URLs as needed
    ]
    
    for url in test_urls:
        try:
            print(f"\\nAnalyzing: {url}")
            logger.log_analysis_start("url", url)
            
            # Note: This will try to extract content from the URL
            # You might need to provide actual article URLs
            result = analyzer.analyze_article(url=url)
            
            logger.log_analysis_complete(result, "url", url=url)
            
            print(f"  Credibility Level: {result.credibility_level}")
            print(f"  Credibility Score: {result.overall_credibility_score:.2f}")
            print(f"  Confidence: {result.confidence_score:.2f}")
            print(f"  Warning Flags: {len(result.warning_flags)}")
            
        except Exception as e:
            print(f"  Error analyzing {url}: {str(e)}")

def example_text_analysis():
    """Example: Analyze news text directly"""
    print("\\n\\n🔍 Example 2: Text Analysis")
    print("-" * 50)
    
    analyzer = NewsAnalyzer()
    logger = FakeNewsDetectorLogger()
    
    # Example news texts with varying credibility
    test_cases = [
        {
            "title": "Scientists Discover New Treatment for Common Disease",
            "content": "Researchers at a major university have published a peer-reviewed study showing promising results for a new treatment approach. The study, conducted over 18 months with 500 participants, showed significant improvement in 78% of cases. The research team plans to begin Phase III trials next year pending regulatory approval.",
            "expected": "High credibility - formal, specific, verifiable"
        },
        {
            "title": "SHOCKING: Doctors HATE This One Weird Trick That Will Change Your Life Forever!",
            "content": "You won't believe what happened when Sarah from Ohio tried this amazing secret that the medical industry doesn't want you to know! Click here to discover the incredible truth that has been hidden from you! This will absolutely blow your mind and change everything you thought you knew about health!",
            "expected": "Low credibility - clickbait, emotional language"
        },
        {
            "title": "Local Community Center Hosts Annual Fundraiser",
            "content": "The Springfield Community Center will host its annual fundraising event next Saturday from 2-6 PM. The event will feature local vendors, live music, and activities for children. Proceeds will support the center's after-school programs and summer camps. Admission is $5 for adults and free for children under 12.",
            "expected": "Medium-High credibility - local news, factual"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\\n--- Test Case {i} ---")
        print(f"Title: {case['title']}")
        print(f"Expected: {case['expected']}")
        
        try:
            logger.log_analysis_start("text", case['title'])
            
            result = analyzer.analyze_article(
                title=case['title'],
                content=case['content']
            )
            
            logger.log_analysis_complete(
                result, "text", 
                title=case['title'],
                content_length=len(case['content'])
            )
            
            print(f"\\nResults:")
            print(f"  Credibility Level: {result.credibility_level}")
            print(f"  Credibility Score: {result.overall_credibility_score:.2f}")
            print(f"  Confidence: {result.confidence_score:.2f}")
            
            if result.warning_flags:
                print(f"  Warning Flags ({len(result.warning_flags)}):")
                for flag in result.warning_flags[:3]:  # Show first 3
                    print(f"    - {flag}")
            
            if result.bias_indicators:
                print(f"  Bias Indicators ({len(result.bias_indicators)}):")
                for indicator in result.bias_indicators[:3]:  # Show first 3
                    print(f"    - {indicator}")
            
            print(f"  Recommendations:")
            for rec in result.recommendations[:2]:  # Show first 2
                print(f"    - {rec}")
                
        except Exception as e:
            print(f"  Error analyzing text: {str(e)}")

def example_batch_analysis():
    """Example: Batch analysis of multiple articles"""
    print("\\n\\n🔍 Example 3: Batch Analysis")
    print("-" * 50)
    
    analyzer = NewsAnalyzer()
    logger = FakeNewsDetectorLogger()
    
    # Simulate batch processing of news headlines
    headlines = [
        "Climate Change Report Shows Significant Temperature Increases",
        "BREAKING: SHOCKING Discovery Will Change Everything You Know!",
        "Local School Board Approves New Budget for Next Year",
        "You Won't Believe These Incredible Facts About Your Health",
        "Economic Indicators Show Modest Growth in Manufacturing Sector",
        "URGENT: This Simple Trick Will Make You Rich Overnight!"
    ]
    
    results = []
    
    print(f"Analyzing {len(headlines)} headlines...")
    
    for i, headline in enumerate(headlines, 1):
        try:
            print(f"\\n{i}. {headline}")
            
            result = analyzer.analyze_article(title=headline)
            results.append({
                'headline': headline,
                'credibility_level': result.credibility_level,
                'credibility_score': result.overall_credibility_score,
                'warning_count': len(result.warning_flags)
            })
            
            print(f"   → {result.credibility_level} ({result.overall_credibility_score:.2f})")
            
        except Exception as e:
            print(f"   → Error: {str(e)}")
    
    # Summary statistics
    print(f"\\n--- Batch Analysis Summary ---")
    if results:
        avg_score = sum(r['credibility_score'] for r in results) / len(results)
        high_cred = sum(1 for r in results if r['credibility_level'] == 'High')
        low_cred = sum(1 for r in results if r['credibility_level'] in ['Low', 'Very Low'])
        
        print(f"  Average Credibility Score: {avg_score:.2f}")
        print(f"  High Credibility Articles: {high_cred}/{len(results)}")
        print(f"  Low Credibility Articles: {low_cred}/{len(results)}")

def example_reporting():
    """Example: Generate reports and export data"""
    print("\\n\\n📊 Example 4: Reporting and Data Export")
    print("-" * 50)
    
    logger = FakeNewsDetectorLogger()
    
    try:
        # Generate daily report
        print("Generating daily report...")
        report = logger.generate_daily_report()
        
        if 'error' not in report:
            print(f"  Total analyses today: {report.get('total_analyses', 0)}")
            print(f"  Analysis types: {report.get('analysis_types', {})}")
            print(f"  Credibility distribution: {report.get('credibility_distribution', {})}")
        else:
            print(f"  {report['error']}")
        
        # Export data
        print("\\nExporting analysis data...")
        csv_file = logger.export_analysis_data('csv')
        json_file = logger.export_analysis_data('json')
        
        print(f"  CSV export: {csv_file}")
        print(f"  JSON export: {json_file}")
        
    except Exception as e:
        print(f"  Error in reporting: {str(e)}")

def main():
    """Run all examples"""
    print("🛡️  Fake News Detector - Usage Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_text_analysis()  # Start with text analysis (doesn't require URLs)
        example_batch_analysis()
        example_reporting()
        
        # Uncomment if you have valid news URLs to test
        # example_url_analysis()
        
        print("\\n\\n✅ Examples completed successfully!")
        print("\\nTo run specific examples:")
        print("  - Check the logs/ directory for generated reports")
        print("  - Modify the test cases to analyze your own content")
        print("  - Add your API keys to .env for full functionality")
        
    except Exception as e:
        print(f"\\n❌ Error running examples: {str(e)}")
        print("\\nTroubleshooting:")
        print("  - Ensure all dependencies are installed: pip install -r requirements.txt")
        print("  - Download NLTK data: python -c 'import nltk; nltk.download(\\\"punkt\\\"); nltk.download(\\\"stopwords\\\")'")
        print("  - Check your internet connection for API calls")

if __name__ == "__main__":
    main()
