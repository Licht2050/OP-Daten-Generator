from kafka.admin import KafkaAdminClient, NewTopic

def delete_topic(bootstrap_servers, topic_name):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        
        # Check if the topic exists
        topic_list = admin_client.list_topics()
        if topic_name not in topic_list:
            print(f"Topic '{topic_name}' does not exist.")
            return

        # Delete the topic
        admin_client.delete_topics(topics=[topic_name])

        print(f"Topic '{topic_name}' deleted successfully.")
    except Exception as e:
        print(f"Error occurred while deleting the topic: {e}")

if __name__ == "__main__":
    bootstrap_servers = "localhost:9092"
    topic_name = "Patientenakte"
    delete_topic(bootstrap_servers, topic_name)
