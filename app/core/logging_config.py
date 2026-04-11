import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Reducing log noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
