import re
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import math

from api_clients import (
    NewsAPIClient, GoogleFactCheckClient, FreeTextAnalysisClient,
    MediaBiasFactCheckClient, CrossReferenceClient
)
from gemini_client import GeminiAIClient
from config import Config

@dataclass
class NewsAnalysisResult:
    """Data class to store news analysis results"""
    overall_credibility_score: float
    credibility_level: str
    sentiment_analysis: Dict[str, Any]
    source_credibility: Dict[str, Any]
    content_analysis: Dict[str, Any]
    cross_reference_results: Dict[str, Any]
    fact_check_results: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    bias_indicators: List[str]
    warning_flags: List[str]
    recommendations: List[str]
    confidence_score: float
    analysis_timestamp: str

class NewsAnalyzer:
    """Main class for analyzing news articles for credibility and bias"""
    
    def __init__(self):
        self.news_api = NewsAPIClient()
        self.fact_check_api = GoogleFactCheckClient()
        self.text_analyzer = FreeTextAnalysisClient()
        self.bias_checker = MediaBiasFactCheckClient()
        self.cross_reference = CrossReferenceClient()
        self.gemini_ai = GeminiAIClient()
    
    def analyze_article(self, url: str = None, title: str = None, content: str = None) -> NewsAnalysisResult:
        """
        Main method to analyze a news article
        
        Args:
            url: URL of the article (optional)
            title: Title/headline of the article
            content: Full text content of the article
        
        Returns:
            NewsAnalysisResult object with comprehensive analysis
        """
        if not title and not content:
            raise ValueError("Either title or content must be provided")
        
        # Initialize analysis components
        sentiment_analysis = {}
        source_credibility = {}
        content_analysis = {}
        cross_reference_results = {}
        fact_check_results = {}
        bias_indicators = []
        warning_flags = []
        recommendations = []
        
        # Analyze sentiment and content
        if content:
            sentiment_analysis = self.text_analyzer.analyze_sentiment_textblob(content)
            content_analysis = self._analyze_content(content, title or "")
        
        # Analyze source credibility
        if url:
            source_credibility = self._analyze_source(url)
        
        # Cross-reference the story
        if title:
            cross_reference_results = self.cross_reference.cross_reference_story(
                title, content or ""
            )
        
        # Search for fact checks
        if title:
            fact_check_results = self.fact_check_api.search_fact_checks(title)
        
        # AI-powered analysis using Gemini (optional enhancement)
        ai_analysis = {}
        if title or content:
            try:
                ai_analysis = self.gemini_ai.analyze_news_credibility(title or "", content or "")
                
                # If AI analysis successful, also get bias analysis
                if ai_analysis.get('status') == 'success':
                    text_for_bias = f"{title or ''} {content or ''}"[:2000]
                    bias_analysis = self.gemini_ai.detect_bias_and_manipulation(text_for_bias)
                    if bias_analysis.get('status') == 'success':
                        ai_analysis['bias_analysis'] = bias_analysis
                else:
                    # AI analysis failed, continue without it
                    ai_analysis = {'status': 'unavailable', 'message': 'AI analysis not available'}
                        
            except Exception as e:
                ai_analysis = {'status': 'error', 'message': f'AI analysis failed: {str(e)}'}
        
        # Identify bias indicators
        text_to_analyze = f"{title or ''} {content or ''}".strip()
        bias_indicators = self._identify_bias_indicators(text_to_analyze)
        
        # Generate warning flags
        warning_flags = self._generate_warning_flags(
            sentiment_analysis, source_credibility, content_analysis,
            bias_indicators, cross_reference_results
        )
        
        # Calculate overall credibility score (now includes AI analysis)
        credibility_score, confidence = self._calculate_credibility_score(
            sentiment_analysis, source_credibility, content_analysis,
            cross_reference_results, bias_indicators, fact_check_results, ai_analysis
        )
        
        # Determine credibility level
        credibility_level = self._determine_credibility_level(credibility_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            credibility_score, warning_flags, source_credibility
        )
        
        return NewsAnalysisResult(
            overall_credibility_score=credibility_score,
            credibility_level=credibility_level,
            sentiment_analysis=sentiment_analysis,
            source_credibility=source_credibility,
            content_analysis=content_analysis,
            cross_reference_results=cross_reference_results,
            fact_check_results=fact_check_results,
            ai_analysis=ai_analysis,
            bias_indicators=bias_indicators,
            warning_flags=warning_flags,
            recommendations=recommendations,
            confidence_score=confidence,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _analyze_source(self, url: str) -> Dict[str, Any]:
        """Analyze the credibility of the news source"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check against known reliable/unreliable sources
            bias_check = self.bias_checker.check_source_bias(domain)
            
            # Additional analysis
            source_analysis = {
                'domain': domain,
                'is_https': parsed_url.scheme == 'https',
                'bias_check': bias_check,
                'domain_age_indicator': self._estimate_domain_credibility(domain)
            }
            
            # Calculate source credibility score
            credibility_score = 0.5  # Default neutral
            
            if bias_check.get('credibility') == 'high':
                credibility_score = 0.9
            elif bias_check.get('credibility') == 'low':
                credibility_score = 0.1
            
            # Adjust for HTTPS (small bonus)
            if source_analysis['is_https']:
                credibility_score += 0.05
            
            source_analysis['credibility_score'] = min(credibility_score, 1.0)
            
            return source_analysis
        
        except Exception as e:
            return {'error': f'Source analysis failed: {str(e)}', 'credibility_score': 0.3}
    
    def _analyze_content(self, content: str, title: str) -> Dict[str, Any]:
        """Analyze the content of the article for credibility indicators"""
        analysis = {
            'length': len(content),
            'word_count': len(content.split()),
            'sentence_count': len(re.findall(r'[.!?]+', content)),
            'keywords': self.text_analyzer.extract_keywords(content),
            'readability_indicators': {},
            'suspicious_patterns': []
        }
        
        # Check for suspicious patterns
        full_text = f"{title} {content}".lower()
        
        # Check for clickbait indicators
        clickbait_patterns = [
            r'you won\'t believe',
            r'shocking',
            r'this will blow your mind',
            r'doctors hate this',
            r'number \d+ will shock you'
        ]
        
        for pattern in clickbait_patterns:
            if re.search(pattern, full_text):
                analysis['suspicious_patterns'].append(f'Clickbait pattern: {pattern}')
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.1:  # More than 10% caps
            analysis['suspicious_patterns'].append('Excessive capitalization')
        
        # Check for excessive punctuation
        punct_ratio = sum(1 for c in content if c in '!?') / max(len(content), 1)
        if punct_ratio > 0.02:  # More than 2% exclamation/question marks
            analysis['suspicious_patterns'].append('Excessive punctuation')
        
        # Basic readability assessment
        if analysis['word_count'] > 0:
            avg_sentence_length = analysis['word_count'] / max(analysis['sentence_count'], 1)
            analysis['readability_indicators']['avg_sentence_length'] = avg_sentence_length
            
            # Flag very short articles (might be incomplete or low-quality)
            if analysis['word_count'] < 100:
                analysis['suspicious_patterns'].append('Very short article')
        
        return analysis
    
    def _identify_bias_indicators(self, text: str) -> List[str]:
        """Identify potential bias indicators in the text"""
        indicators = []
        text_lower = text.lower()
        
        # Check for bias indicator phrases from config
        for indicator in Config.BIAS_INDICATORS:
            if indicator.lower() in text_lower:
                indicators.append(indicator)
        
        # Check for emotional language
        emotional_words = [
            'outrageous', 'disgraceful', 'shocking', 'unbelievable',
            'devastating', 'alarming', 'terrifying', 'incredible'
        ]
        
        for word in emotional_words:
            if word in text_lower:
                indicators.append(f'Emotional language: {word}')
        
        # Check for absolute statements
        absolute_patterns = [
            r'always', r'never', r'all .* are', r'every .* is',
            r'completely', r'totally', r'absolutely'
        ]
        
        for pattern in absolute_patterns:
            if re.search(pattern, text_lower):
                indicators.append(f'Absolute statement: {pattern}')
        
        return list(set(indicators))  # Remove duplicates
    
    def _calculate_credibility_score(self, sentiment_analysis: Dict, source_credibility: Dict,
                                   content_analysis: Dict, cross_reference_results: Dict,
                                   bias_indicators: List, fact_check_results: Dict, ai_analysis: Dict) -> Tuple[float, float]:
        """Calculate overall credibility score and confidence level"""
        
        scores = []
        weights = []
        
        # Source credibility (25% weight)
        if source_credibility.get('credibility_score') is not None:
            scores.append(source_credibility['credibility_score'])
            weights.append(0.25)
        
        # Content quality (20% weight)
        content_score = 0.5  # Default neutral
        if content_analysis:
            # Penalize suspicious patterns
            pattern_penalty = len(content_analysis.get('suspicious_patterns', [])) * 0.1
            content_score = max(0.7 - pattern_penalty, 0.1)
            
            # Bonus for reasonable article length
            word_count = content_analysis.get('word_count', 0)
            if 200 <= word_count <= 2000:
                content_score += 0.1
        
        scores.append(content_score)
        weights.append(0.2)
        
        # Cross-reference consensus (15% weight)
        if cross_reference_results.get('consensus_score') is not None:
            consensus_score = cross_reference_results['consensus_score']
            # Higher consensus = higher credibility
            scores.append(min(0.5 + consensus_score * 0.5, 1.0))
            weights.append(0.15)
        
        # Bias indicators (10% weight)
        bias_score = max(0.8 - len(bias_indicators) * 0.1, 0.2)
        scores.append(bias_score)
        weights.append(0.1)
        
        # AI Analysis (20% weight) - highest priority for advanced reasoning
        if ai_analysis.get('status') == 'success' and ai_analysis.get('credibility_score') is not None:
            ai_score = ai_analysis['credibility_score']
            # AI provides sophisticated analysis, so give it significant weight
            scores.append(ai_score)
            weights.append(0.2)
        
        # Sentiment objectivity (10% weight)
        if sentiment_analysis.get('subjectivity') is not None:
            objectivity = 1 - sentiment_analysis['subjectivity']
            # More objective = higher credibility
            subjectivity_score = 0.3 + (objectivity * 0.7)
            scores.append(subjectivity_score)
            weights.append(0.1)
        
        # Calculate weighted average
        if scores and weights:
            total_weight = sum(weights)
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            final_score = weighted_sum / total_weight
            
            # Calculate confidence based on number of factors analyzed
            confidence = len(scores) / 5.0  # Max 5 factors
        else:
            final_score = 0.3  # Low default if no analysis possible
            confidence = 0.2
        
        return min(max(final_score, 0.0), 1.0), min(confidence, 1.0)
    
    def _determine_credibility_level(self, score: float) -> str:
        """Determine credibility level based on score"""
        if score >= Config.HIGH_CREDIBILITY_THRESHOLD:
            return "High"
        elif score >= Config.MEDIUM_CREDIBILITY_THRESHOLD:
            return "Medium"
        elif score >= Config.LOW_CREDIBILITY_THRESHOLD:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_warning_flags(self, sentiment_analysis: Dict, source_credibility: Dict,
                              content_analysis: Dict, bias_indicators: List,
                              cross_reference_results: Dict) -> List[str]:
        """Generate warning flags based on analysis"""
        warnings = []
        
        # Source warnings
        if source_credibility.get('bias_check', {}).get('credibility') == 'low':
            warnings.append("Source has low credibility rating")
        
        if not source_credibility.get('is_https', True):
            warnings.append("Source does not use HTTPS")
        
        # Content warnings
        suspicious_patterns = content_analysis.get('suspicious_patterns', [])
        if suspicious_patterns:
            warnings.extend([f"Content issue: {pattern}" for pattern in suspicious_patterns])
        
        # Bias warnings
        if len(bias_indicators) > 3:
            warnings.append("High number of bias indicators detected")
        
        # Cross-reference warnings
        consensus_score = cross_reference_results.get('consensus_score', 0.5)
        if consensus_score < 0.3:
            warnings.append("Low consensus with other sources")
        
        source_diversity = cross_reference_results.get('source_diversity', 0)
        if source_diversity < 2:
            warnings.append("Limited source diversity for verification")
        
        # Sentiment warnings
        subjectivity = sentiment_analysis.get('subjectivity', 0.5)
        if subjectivity > 0.8:
            warnings.append("Highly subjective content")
        
        return warnings
    
    def _generate_recommendations(self, credibility_score: float, warning_flags: List[str],
                                source_credibility: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if credibility_score < Config.MEDIUM_CREDIBILITY_THRESHOLD:
            recommendations.append("Verify this information with additional reliable sources")
        
        if credibility_score < Config.LOW_CREDIBILITY_THRESHOLD:
            recommendations.append("Exercise extreme caution - this content may be unreliable")
        
        if len(warning_flags) > 2:
            recommendations.append("Multiple warning indicators detected - fact-check before sharing")
        
        if source_credibility.get('bias_check', {}).get('credibility') == 'unknown':
            recommendations.append("Unknown source - research the publisher's background and reputation")
        
        recommendations.append("Always cross-reference important news with multiple reliable sources")
        
        return recommendations
    
    def _estimate_domain_credibility(self, domain: str) -> Dict[str, Any]:
        """Estimate domain credibility based on simple heuristics"""
        # This is a simplified implementation
        # In a production system, you might use domain age APIs or other indicators
        
        indicators = {
            'has_common_tld': domain.endswith(('.com', '.org', '.gov', '.edu', '.net')),
            'length': len(domain),
            'suspicious_keywords': []
        }
        
        # Check for suspicious keywords in domain
        suspicious = ['fake', 'real', 'truth', 'insider', 'leaked', 'exposed']
        for keyword in suspicious:
            if keyword in domain.lower():
                indicators['suspicious_keywords'].append(keyword)
        
        return indicators
