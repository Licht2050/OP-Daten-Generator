from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import logging

logging.basicConfig(level=logging.INFO)

def create_topic(bootstrap_servers, topic_name, partitions=1, replication_factor=1):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        topic = NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication_factor)
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        logging.info(f"Topic '{topic_name}' created successfully.")
    except TopicAlreadyExistsError:
        logging.info(f"Topic '{topic_name}' already exists.")
    except Exception as e:
        logging.error(f"Error occurred while creating the topic: {e}")

def create_topics(bootstrap_servers, topic_configs):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        new_topics = [NewTopic(name=config['topic_name'], num_partitions=config['partitions'], replication_factor=config['replication_factor']) for config in topic_configs]
        admin_client.create_topics(new_topics=new_topics, validate_only=False)
        for config in topic_configs:
            logging.info(f"Topic '{config['topic_name']}' created successfully.")
    except TopicAlreadyExistsError as e:
        logging.info(f"Topic '{e.args[0]}' already exists.")
    except Exception as e:
        logging.error(f"Error occurred while creating topics: {e}")

if __name__ == "__main__":
    bootstrap_servers = "localhost:9092"  
    topic_name = "vital_parameters"          
    partitions = 5                        
    replication_factor = 2 

    # create_topic(bootstrap_servers, topic_name, partitions, replication_factor)

    topic_configs = [
        {"topic_name": "environmental_data", "partitions": 3, "replication_factor": 2},
        {"topic_name": "vital_parameters", "partitions": 5, "replication_factor": 2},
        {"topic_name": "patient_data", "partitions": 3, "replication_factor": 2},
        {"topic_name": "operation_room_status", "partitions": 1, "replication_factor": 1},
        {"topic_name": "staff_communication", "partitions": 5, "replication_factor": 2},
        {"topic_name": "operation_team", "partitions": 3, "replication_factor": 2},
        {"topic_name": "entry_exit_events", "partitions": 3, "replication_factor": 2}
    ]
    create_topics(bootstrap_servers, topic_configs)
    # create_topic(bootstrap_servers, topic_name, partitions, replication_factor)