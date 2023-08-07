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

if __name__ == "__main__":
    bootstrap_servers = "localhost:9092"  
    topic_name = "RoomStatus"          
    partitions = 3                        
    replication_factor = 1 

    create_topic(bootstrap_servers, topic_name, partitions, replication_factor)
