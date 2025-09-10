import logging
import sys

def setup_logging(level=logging.INFO):

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    logging.getLogger('app.functions.shipment_list.src.app').setLevel(level)
    logging.getLogger('app.functions.create_shipment.src.app').setLevel(level)
    
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    
    return root_logger

if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration test")
    logger.debug("Debug message test")
    logger.warning("Warning message test")
    logger.error("Error message test")
