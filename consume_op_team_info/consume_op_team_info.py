
import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from general_kafka_consumer import GeneralKafkaConsumer
from json_writer import JSONWriter
from config_loader import ConfigLoader

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    source_name = 'op_team'
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config = ConfigLoader(config_file_path)
    op_team_info_config = config.load_config(source_name)
    topic_name = op_team_info_config['topic']
    bootstrap_servers = op_team_info_config['bootstrap_servers']
    op_team_info_path = os.path.join(os.path.dirname(__file__), 'op_team_info.json')

    consumer = GeneralKafkaConsumer(topic_name, bootstrap_servers)
    writer = JSONWriter(op_team_info_path)

    try:
        for message in consumer.consume_messages():
            message_value = message.value
            if message_value.get('source') == 'op_team':
                op_team_info = {"op_team_info": message_value['value']}
                writer.write_data(op_team_info)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Closing Kafka consumer.")
    except Exception as e:
        logging.error(f"Error while consuming message: {e}")
    finally:
        consumer.close()
