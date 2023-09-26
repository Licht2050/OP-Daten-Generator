

import os
import sys
import logging


sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../API/pub_sub')
])

from pub_sub import indoor_environment_data_subject

class GraphQLPublisher():
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def process_data(self, processed_message):
        # Log the received message
        self.logger.info(f"Received message: {processed_message.to_dict()}")
        
        # Publish the processed message to the subject
        indoor_environment_data_subject.on_next(processed_message.to_dict())
        
        # Log a confirmation message
        self.logger.info("Message published to subject")
        
        # Continue the middleware pipeline
        return processed_message