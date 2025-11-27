import logging
import sys

from config.settings import get_settings

logging.basicConfig()

logger = logging.getLogger()

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(get_settings().log_level)

logger.addHandler(stream_handler)
