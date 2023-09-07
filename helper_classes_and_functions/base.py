import json
import logging
from typing import Dict, Any


class Base:
    def _setup_logging(self):
        """Initialize logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _decode_message(self, message)-> Dict[str, Any]:
        """Decode a JSON message."""
        return json.loads(message.value().decode('utf-8'))

    def _handle_exception(self, e):
        """Handle exceptions and log them."""
        self.logger.error(f"{type(e).__name__} occurred: {e}")