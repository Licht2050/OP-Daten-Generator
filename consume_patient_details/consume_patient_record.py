import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from general_kafka_consumer import GeneralKafkaConsumer
from json_writer import JSONWriter
from config_loader import ConfigLoader

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    source_name = 'patient_records'
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config = ConfigLoader(config_file_path)
    patient_records_config = config.load_config(source_name)
    topic_name = patient_records_config['topic']
    bootstrap_servers = patient_records_config['bootstrap_servers']
    patient_info_path = os.path.join(os.path.dirname(__file__), 'patient_info.json')

    consumer = GeneralKafkaConsumer(topic_name, bootstrap_servers)
    writer = JSONWriter(patient_info_path)

    try:
        for message in consumer.consume_messages():
            message_value = message.value
            if message_value.get('source') == 'patient_records':
                patient_details = {"patient_details": message_value['value']}
                writer.write_data(patient_details)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Closing Kafka consumer.")
    except Exception as e:
        logging.error(f"Error while consuming message: {e}")
    finally:
        consumer.close()