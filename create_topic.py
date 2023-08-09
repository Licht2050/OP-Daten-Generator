from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def create_topic(bootstrap_servers, topic_name, partitions=1, replication_factor=1):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        topic = NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication_factor)
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        print(f"Topic '{topic_name}' created successfully.")
    except TopicAlreadyExistsError:
        print(f"Topic '{topic_name}' already exists.")
    except Exception as e:
        print(f"Error occurred while creating the topic: {e}")

def create_topics(bootstrap_servers, topic_configs):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        new_topics = [NewTopic(name=config['topic_name'], num_partitions=config['partitions'], replication_factor=config['replication_factor']) for config in topic_configs]
        admin_client.create_topics(new_topics=new_topics, validate_only=False)
        for config in topic_configs:
            print(f"Topic '{config['topic_name']}' created successfully.")
    except TopicAlreadyExistsError as e:
        print(f"Topic '{e.args[0]}' already exists.")
    except Exception as e:
        print(f"Error occurred while creating topics: {e}")

if __name__ == "__main__":
    bootstrap_servers = "localhost:9092"  
    topic_name = "OP_Entry_Exit_Events"          
    partitions = 3                        
    replication_factor = 1 

    create_topic(bootstrap_servers, topic_name, partitions, replication_factor)

    # topic_configs = [
    #     {"topic_name": "RoomStatus", "partitions": 3, "replication_factor": 2},
    #     {"topic_name": "SensorData", "partitions": 5, "replication_factor": 2},
    #     {"topic_name": "PatientenRecords", "partitions": 3, "replication_factor": 2},
    #     {"topic_name": "EmergencyAlerts", "partitions": 1, "replication_factor": 1},
    #     {"topic_name": "StaffCommunication", "partitions": 5, "replication_factor": 2},
    #     {"topic_name": "InventoryManagement", "partitions": 3, "replication_factor": 2}
        
    # ]

    # create_topics(bootstrap_servers, topic_configs)