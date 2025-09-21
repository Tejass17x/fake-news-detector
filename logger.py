import logging
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os

from news_analyzer import NewsAnalysisResult

class FakeNewsDetectorLogger:
    """Comprehensive logging and reporting system for the fake news detector"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup main logger
        self.logger = logging.getLogger('fake_news_detector')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler for general logs
        log_file = self.log_dir / f"fake_news_detector_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Analysis results log file
        self.analysis_log_file = self.log_dir / f"analysis_results_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # CSV report file
        self.csv_report_file = self.log_dir / f"analysis_summary_{datetime.now().strftime('%Y%m%d')}.csv"
        self._init_csv_file()
    
    def _init_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not self.csv_report_file.exists():
            headers = [
                'timestamp', 'analysis_type', 'url', 'title', 'credibility_score',
                'credibility_level', 'confidence_score', 'source_domain',
                'source_credibility', 'warning_count', 'bias_indicator_count',
                'sentiment', 'word_count', 'consensus_score', 'source_diversity'
            ]
            
            with open(self.csv_report_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def log_analysis_start(self, analysis_type: str, target: str):
        """Log the start of an analysis"""
        self.logger.info(f"Starting {analysis_type} analysis for: {target[:100]}")
    
    def log_analysis_complete(self, result: NewsAnalysisResult, analysis_type: str, 
                            url: str = None, title: str = None, content_length: int = 0):
        """Log completed analysis with full results"""
        
        # Log to main logger
        self.logger.info(
            f"Analysis completed - Credibility: {result.credibility_level} "
            f"({result.overall_credibility_score:.2f}) - Confidence: {result.confidence_score:.2f}"
        )
        
        # Log detailed results to JSONL file
        self._log_detailed_analysis(result, analysis_type, url, title, content_length)
        
        # Log summary to CSV
        self._log_csv_summary(result, analysis_type, url, title)
        
        # Log warnings if any
        if result.warning_flags:
            self.logger.warning(f"Analysis produced {len(result.warning_flags)} warning flags")
            for flag in result.warning_flags[:3]:  # Log first 3 warnings
                self.logger.warning(f"  - {flag}")
    
    def _log_detailed_analysis(self, result: NewsAnalysisResult, analysis_type: str,
                             url: str, title: str, content_length: int):
        """Log detailed analysis results to JSONL file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'url': url,
            'title': title[:200] if title else None,  # Truncate long titles
            'content_length': content_length,
            'results': {
                'overall_credibility_score': result.overall_credibility_score,
                'credibility_level': result.credibility_level,
                'confidence_score': result.confidence_score,
                'sentiment_analysis': result.sentiment_analysis,
                'source_credibility': result.source_credibility,
                'content_analysis': {
                    'word_count': result.content_analysis.get('word_count') if result.content_analysis else None,
                    'sentence_count': result.content_analysis.get('sentence_count') if result.content_analysis else None,
                    'suspicious_patterns_count': len(result.content_analysis.get('suspicious_patterns', [])) if result.content_analysis else 0,
                    'keywords_count': len(result.content_analysis.get('keywords', [])) if result.content_analysis else 0
                },
                'cross_reference_results': {
                    'consensus_score': result.cross_reference_results.get('consensus_score') if result.cross_reference_results else None,
                    'source_diversity': result.cross_reference_results.get('source_diversity') if result.cross_reference_results else None,
                    'similar_articles_count': len(result.cross_reference_results.get('similar_articles', [])) if result.cross_reference_results else 0
                },
                'bias_indicators_count': len(result.bias_indicators),
                'warning_flags_count': len(result.warning_flags),
                'warning_flags': result.warning_flags,
                'bias_indicators': result.bias_indicators,
                'recommendations': result.recommendations,
                'analysis_timestamp': result.analysis_timestamp
            }
        }
        
        with open(self.analysis_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _log_csv_summary(self, result: NewsAnalysisResult, analysis_type: str,
                        url: str, title: str):
        """Log summary to CSV file"""
        row = [
            datetime.now().isoformat(),
            analysis_type,
            url or '',
            (title[:100] + '...') if title and len(title) > 100 else (title or ''),
            result.overall_credibility_score,
            result.credibility_level,
            result.confidence_score,
            result.source_credibility.get('domain', '') if result.source_credibility else '',
            result.source_credibility.get('bias_check', {}).get('credibility', '') if result.source_credibility else '',
            len(result.warning_flags),
            len(result.bias_indicators),
            result.sentiment_analysis.get('sentiment', '') if result.sentiment_analysis else '',
            result.content_analysis.get('word_count', '') if result.content_analysis else '',
            result.cross_reference_results.get('consensus_score', '') if result.cross_reference_results else '',
            result.cross_reference_results.get('source_diversity', '') if result.cross_reference_results else ''
        ]
        
        with open(self.csv_report_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context"""
        self.logger.error(f"Error in {context}: {str(error)}")
    
    def log_warning(self, message: str):
        """Log warning messages"""
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log info messages"""
        self.logger.info(message)
    
    def generate_daily_report(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive daily analysis report"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        analysis_file = self.log_dir / f"analysis_results_{date}.jsonl"
        
        if not analysis_file.exists():
            return {"error": f"No analysis data found for {date}"}
        
        analyses = []
        with open(analysis_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    analyses.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        if not analyses:
            return {"error": f"No valid analysis data found for {date}"}
        
        # Generate statistics
        report = {
            "date": date,
            "total_analyses": len(analyses),
            "analysis_types": {},
            "credibility_distribution": {},
            "warning_statistics": {},
            "performance_metrics": {},
            "top_domains": {},
            "common_bias_indicators": {}
        }
        
        # Count analysis types
        for analysis in analyses:
            analysis_type = analysis.get('analysis_type', 'unknown')
            report["analysis_types"][analysis_type] = report["analysis_types"].get(analysis_type, 0) + 1
        
        # Credibility distribution
        for analysis in analyses:
            level = analysis.get('results', {}).get('credibility_level', 'unknown')
            report["credibility_distribution"][level] = report["credibility_distribution"].get(level, 0) + 1
        
        # Warning statistics
        warning_counts = [len(analysis.get('results', {}).get('warning_flags', [])) for analysis in analyses]
        report["warning_statistics"] = {
            "total_warnings": sum(warning_counts),
            "avg_warnings_per_analysis": sum(warning_counts) / len(warning_counts) if warning_counts else 0,
            "analyses_with_warnings": sum(1 for count in warning_counts if count > 0)
        }
        
        # Performance metrics
        credibility_scores = [
            analysis.get('results', {}).get('overall_credibility_score', 0)
            for analysis in analyses
        ]
        confidence_scores = [
            analysis.get('results', {}).get('confidence_score', 0)
            for analysis in analyses
        ]
        
        report["performance_metrics"] = {
            "avg_credibility_score": sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0,
            "avg_confidence_score": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "high_credibility_count": sum(1 for score in credibility_scores if score >= 0.8),
            "low_credibility_count": sum(1 for score in credibility_scores if score <= 0.3)
        }
        
        # Top domains analyzed
        domains = []
        for analysis in analyses:
            source_cred = analysis.get('results', {}).get('source_credibility')
            if source_cred and source_cred.get('domain'):
                domains.append(source_cred['domain'])
        
        domain_counts = {}
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        report["top_domains"] = dict(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Common bias indicators
        all_indicators = []
        for analysis in analyses:
            indicators = analysis.get('results', {}).get('bias_indicators', [])
            all_indicators.extend(indicators)
        
        indicator_counts = {}
        for indicator in all_indicators:
            indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
        
        report["common_bias_indicators"] = dict(sorted(indicator_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Save report
        report_file = self.log_dir / f"daily_report_{date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Daily report generated for {date}: {report_file}")
        
        return report
    
    def export_analysis_data(self, format: str = "json", date_range: Optional[tuple] = None) -> str:
        """Export analysis data in specified format"""
        # Implementation for exporting data in various formats
        # This is a simplified version - you could extend it for more formats
        
        if format.lower() == "json":
            return self._export_json(date_range)
        elif format.lower() == "csv":
            return str(self.csv_report_file)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, date_range: Optional[tuple] = None) -> str:
        """Export JSON data for specified date range"""
        export_file = self.log_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # For simplicity, export today's data
        # You could extend this to handle date ranges
        today = datetime.now().strftime('%Y%m%d')
        analysis_file = self.log_dir / f"analysis_results_{today}.jsonl"
        
        if analysis_file.exists():
            analyses = []
            with open(analysis_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        analyses.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(analyses, f, indent=2, ensure_ascii=False)
        
        return str(export_file)
