#!/usr/bin/env python3
"""
Forward Proxy Caching Service - Main Application Entry Point.
"""
import os
import sys
import logging
from src.services import create_app

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main application entry point."""
    try:
        # Configure logging using centralized setup
        from src.helpers import setup_logging
        setup_logging(level="INFO", log_file="service.log")
        
        logger = logging.getLogger(__name__)
        logger.info("Starting Forward Proxy Caching Service...")
        
        # Create Flask application
        app = create_app()
        
        # Get configuration from environment variables
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 4000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Service configuration: host={host}, port={port}, debug={debug}")
        
        # Start the service
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # Disable reloader for production
        )
        
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Failed to start service: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 