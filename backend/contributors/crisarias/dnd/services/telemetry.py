def setupLogger():
    logger = logging.getLogger("dnd_telemetry")
    logger.setLevel(logging.INFO)  # Or DEBUG for more verbosity

    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
