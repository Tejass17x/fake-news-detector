#!/usr/bin/env python3
"""
Main Entry Point for Fake News Detector
Provides a unified interface to access all functionality
"""

import argparse
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

def run_cli():
    """Run the command line interface"""
    from cli import main as cli_main
    cli_main()

def run_web_app():
    """Run the web application"""
    from app import app
    from config import Config
    
    print("🚀 Starting Fake News Detector Web Server...")
    print(f"📡 Server will be available at: http://localhost:{Config.PORT}")
    print("🛑 Press Ctrl+C to stop the server")
    
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )

def run_examples():
    """Run usage examples"""
    from example_usage import main as examples_main
    examples_main()

def show_info():
    """Show system information and setup status"""
    print("🛡️  Fake News Detector - System Information")
    print("=" * 60)
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # Check dependencies
    print("\\nDependency Check:")
    dependencies = [
        'requests', 'beautifulsoup4', 'nltk', 'textblob', 
        'newspaper3k', 'python-dotenv', 'flask', 'pandas', 'numpy'
    ]
    
    for dep in dependencies:
        try:
            # Special cases for imports
            if dep == 'beautifulsoup4':
                import_name = 'bs4'
            elif dep == 'python-dotenv':
                import_name = 'dotenv'
            elif dep == 'newspaper3k':
                import_name = 'newspaper'
            else:
                import_name = dep.replace('-', '_')
            __import__(import_name)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - Run: pip install {dep}")
    
    # Check NLTK data
    print("\\nNLTK Data Check:")
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
            print("  ✅ punkt tokenizer")
        except LookupError:
            print("  ❌ punkt tokenizer - Run: python -c \\\"import nltk; nltk.download('punkt')\\\"")
        
        try:
            nltk.data.find('corpora/stopwords')
            print("  ✅ stopwords corpus")
        except LookupError:
            print("  ❌ stopwords corpus - Run: python -c \\\"import nltk; nltk.download('stopwords')\\\"")
    except ImportError:
        print("  ❌ NLTK not installed")
    
    # Check configuration
    print("\\nConfiguration Check:")
    try:
        from config import Config
        print(f"  Debug Mode: {Config.DEBUG}")
        print(f"  Port: {Config.PORT}")
        
        if Config.NEWS_API_KEY:
            print("  ✅ NewsAPI key configured")
        else:
            print("  ⚠️  NewsAPI key not configured (optional)")
        
        if Config.GOOGLE_CSE_API_KEY:
            print("  ✅ Google CSE API key configured")
        else:
            print("  ⚠️  Google CSE API key not configured (optional)")
        
        if Config.GEMINI_API_KEY:
            print("  ✅ Gemini AI API key configured")
        else:
            print("  ⚠️  Gemini AI API key not configured (optional)")
            
    except Exception as e:
        print(f"  ❌ Configuration error: {str(e)}")
    
    # Check directories
    print("\\nDirectory Structure:")
    directories = ['logs', 'templates']
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"  ✅ {directory}/")
        else:
            print(f"  ⚠️  {directory}/ - Will be created when needed")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Professional Fake News Detector - Main Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --cli              # Run command line interface
  python main.py --web              # Run web server
  python main.py --examples         # Run usage examples
  python main.py --info             # Show system information
  
For more specific options, use individual commands:
  python cli.py --help              # CLI-specific options
  python app.py                     # Direct web server start
        '''
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--cli', '-c', action='store_true', 
                      help='Run command line interface')
    group.add_argument('--web', '-w', action='store_true',
                      help='Run web server')
    group.add_argument('--examples', '-e', action='store_true',
                      help='Run usage examples')
    group.add_argument('--info', '-i', action='store_true',
                      help='Show system information')
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    try:
        if args.cli:
            run_cli()
        elif args.web:
            run_web_app()
        elif args.examples:
            run_examples()
        elif args.info:
            show_info()
    
    except KeyboardInterrupt:
        print("\\n\\n👋 Goodbye!")
    except Exception as e:
        print(f"\\n❌ Error: {str(e)}")
        print("\\nFor help, run: python main.py --info")
        sys.exit(1)

if __name__ == "__main__":
    main()
