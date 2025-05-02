import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s - %(asctime)s] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

appLogging = logging
