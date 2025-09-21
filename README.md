# 🛡️ Professional Fake News Detector

A comprehensive, professional-grade fake news detection system that analyzes news articles for credibility and bias using advanced AI techniques and free APIs.

## 🚀 Features

### Core Analysis Capabilities
- **Source Credibility Assessment** - Evaluates news source reliability and bias ratings
- **Content Analysis** - Detects suspicious patterns, clickbait indicators, and content quality
- **Sentiment Analysis** - Analyzes emotional tone and objectivity using TextBlob
- **Cross-Reference Verification** - Compares articles across multiple sources
- **Bias Detection** - Identifies potential bias indicators and emotional language
- **Real-time Fact-Checking** - Integration with Google Fact Check Tools API

### User Interfaces
- **Command Line Interface (CLI)** - Interactive terminal-based analysis
- **Web Interface** - Modern, responsive web application using Flask
- **REST API** - Programmatic access for developers

### Professional Features
- **Comprehensive Logging** - Detailed analysis logs and reporting
- **CSV/JSON Export** - Export analysis results in multiple formats
- **Daily Reports** - Automated statistical reports and insights
- **Confidence Scoring** - Reliability metrics for each analysis
- **Professional UI** - Clean, intuitive interface with visual indicators

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for API calls
- Free API keys (optional but recommended):
  - [NewsAPI.org](https://newsapi.org/) - For news article searches
  - [Google Custom Search API](https://developers.google.com/custom-search/v1/introduction) - For cross-referencing

## 🔧 Installation

1. **Clone or Download the Project**
   ```bash
   # Navigate to your desired directory
   cd /path/to/your/projects
   
   # If you have the files, navigate to the fake_news_detector directory
   cd fake_news_detector
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK Data** (First run only)
   ```python
   python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords')\"
   ```

4. **Configure API Keys** (Optional but recommended)
   ```bash
   # Copy the example environment file
   copy .env.example .env
   
   # Edit .env and add your API keys
   # NEWS_API_KEY=your_newsapi_key_here
   # GOOGLE_CUSTOM_SEARCH_API_KEY=your_google_cse_key_here
   # GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_cse_id_here
   ```

## 🏃‍♂️ Quick Start

### Command Line Interface

1. **Interactive Mode**
   ```bash
   python cli.py
   ```

2. **Analyze a URL**
   ```bash
   python cli.py --url \"https://example.com/news/article\"
   ```

3. **Analyze Text**
   ```bash
   python cli.py --text \"Breaking: Major event happens in city\"
   ```

### Web Interface

1. **Start the Web Server**
   ```bash
   python app.py
   ```

2. **Open in Browser**
   - Navigate to `http://localhost:5000`
   - Enter a URL or paste text to analyze
   - View comprehensive analysis results

## 📊 Analysis Components

### Credibility Scoring
The system provides an overall credibility score (0.0 to 1.0) based on:
- **Source Credibility (30%)** - Domain reputation and reliability
- **Content Quality (25%)** - Writing quality and suspicious patterns
- **Cross-Reference Consensus (20%)** - Agreement with other sources
- **Bias Indicators (15%)** - Presence of biased or emotional language
- **Sentiment Objectivity (10%)** - Emotional neutrality of content

### Credibility Levels
- **High (0.8+)** - ✅ Highly credible, minimal concerns
- **Medium (0.5-0.8)** - ⚠️ Moderately credible, some caution advised
- **Low (0.3-0.5)** - ⚠️ Low credibility, verification recommended
- **Very Low (<0.3)** - ❌ Very low credibility, high skepticism advised

## 🔍 Usage Examples

### CLI Examples

```bash
# Interactive mode with help
python cli.py -i

# Analyze a news URL
python cli.py -u \"https://www.bbc.com/news/world-12345678\"

# Analyze text with custom title
python cli.py -t \"Scientists discover new treatment\" --title \"Medical Breakthrough\"

# Verbose output
python cli.py -u \"https://example.com/news\" -v
```

### Web API Examples

```python
import requests

# Analyze URL
response = requests.post('http://localhost:5000/analyze', json={
    'type': 'url',
    'url': 'https://example.com/news/article'
})

# Analyze text
response = requests.post('http://localhost:5000/analyze', json={
    'type': 'text',
    'title': 'Breaking News Headline',
    'content': 'Full article content here...'
})

result = response.json()
print(f\"Credibility: {result['result']['credibility_level']}\")
```

### Python Module Usage

```python
from news_analyzer import NewsAnalyzer

# Initialize analyzer
analyzer = NewsAnalyzer()

# Analyze URL
result = analyzer.analyze_article(
    url=\"https://example.com/news\",
    title=\"Article Title\",
    content=\"Article content...\"
)

print(f\"Credibility Score: {result.overall_credibility_score:.2f}\")
print(f\"Credibility Level: {result.credibility_level}\")
print(f\"Warning Flags: {result.warning_flags}\")
```

## 📈 API Integration Guide

### Free APIs Used

1. **NewsAPI.org**
   - **Purpose**: Cross-reference news articles
   - **Limit**: 1,000 requests/month (free tier)
   - **Signup**: https://newsapi.org/register

2. **Google Custom Search API**
   - **Purpose**: Broader web search for fact-checking
   - **Limit**: 100 queries/day (free tier)
   - **Setup**: https://developers.google.com/custom-search/v1/introduction

3. **Google Fact Check Tools API**
   - **Purpose**: Find existing fact-checks
   - **Limit**: Generous free tier
   - **Setup**: https://developers.google.com/fact-check/tools/api/

### API Configuration

```python
# config.py
NEWS_API_KEY = \"your_newsapi_key\"
GOOGLE_CSE_API_KEY = \"your_google_api_key\"
GOOGLE_CSE_ID = \"your_custom_search_engine_id\"
```

## 📝 Logging and Reports

### Log Files
- `logs/fake_news_detector_YYYYMMDD.log` - General application logs
- `logs/analysis_results_YYYYMMDD.jsonl` - Detailed analysis results
- `logs/analysis_summary_YYYYMMDD.csv` - Summary data for analysis

### Generate Reports

```python
from logger import FakeNewsDetectorLogger

logger = FakeNewsDetectorLogger()

# Generate daily report
report = logger.generate_daily_report()
print(f\"Analyzed {report['total_analyses']} articles today\")

# Export data
csv_file = logger.export_analysis_data('csv')
json_file = logger.export_analysis_data('json')
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
NEWS_API_KEY=your_newsapi_key_here
GOOGLE_CUSTOM_SEARCH_API_KEY=your_google_key_here
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_cse_id_here

# Application Settings
DEBUG=True
PORT=5000
```

### Customizing Thresholds
```python
# config.py
HIGH_CREDIBILITY_THRESHOLD = 0.8  # Adjust as needed
MEDIUM_CREDIBILITY_THRESHOLD = 0.5
LOW_CREDIBILITY_THRESHOLD = 0.3
```

### Adding Reliable Sources
```python
# config.py
RELIABLE_SOURCES = [
    'reuters.com', 'ap.org', 'bbc.com', 'npr.org',
    # Add your trusted sources here
]
```

## 🚨 Limitations and Disclaimers

### Important Notes
- **Not 100% Accurate**: This tool provides analysis based on available data and algorithms
- **Human Judgment Required**: Always apply critical thinking and verify important information
- **API Dependencies**: Some features require active internet connection and API keys
- **Language Support**: Primarily designed for English-language content
- **Bias in Training Data**: The tool's judgments may reflect biases in its training sources

### Best Practices
1. **Use Multiple Sources**: Always cross-reference important news with multiple reliable sources
2. **Consider Context**: Analyze the full context, not just headlines
3. **Check Publication Date**: Verify the timeliness and relevance of information
4. **Verify Claims**: Independently verify specific claims and statistics
5. **Understand Limitations**: This tool is an aid, not a replacement for critical thinking

## 🤝 Contributing

### How to Contribute
1. **Report Issues**: Use GitHub issues for bugs and feature requests
2. **Improve Algorithms**: Enhance credibility scoring and bias detection
3. **Add API Integrations**: Integrate additional free APIs for better analysis
4. **Improve Documentation**: Help improve this README and code documentation
5. **Language Support**: Add support for additional languages

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when available)
python -m pytest tests/

# Code formatting
python -m black .
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Getting Help
1. **Check Documentation**: Review this README thoroughly
2. **Common Issues**: Check the troubleshooting section below
3. **GitHub Issues**: Report bugs and request features
4. **Community**: Join discussions and share experiences

### Troubleshooting

**Issue: \"No module named 'textblob'\"**
```bash
Solution: pip install textblob
```

**Issue: \"NLTK data not found\"**
```bash
Solution: python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords')\"
```

**Issue: \"API key not configured\"**
```bash
Solution: Copy .env.example to .env and add your API keys
```

**Issue: \"Could not extract content from URL\"**
```bash
Solution: Try a different URL or manually paste the text content
```

## 🏆 Acknowledgments

- **TextBlob**: For sentiment analysis capabilities
- **BeautifulSoup**: For web scraping and content extraction  
- **Flask**: For the web interface framework
- **NLTK**: For natural language processing features
- **Bootstrap**: For responsive web design
- **Free API Providers**: NewsAPI, Google APIs, and others

---

**⚠️ Disclaimer**: This tool is designed to assist in evaluating news credibility but should not be the sole basis for determining the truthfulness of information. Always apply critical thinking and consult multiple reliable sources when evaluating news content.

**🔐 Privacy**: This tool processes content locally and through third-party APIs. Be mindful of privacy when analyzing sensitive content.

Made with ❤️ for promoting media literacy and critical thinking.
#   f a k e - n e w s - d e t e c t o r  
 