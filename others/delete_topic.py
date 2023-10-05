from kafka.admin import KafkaAdminClient
import logging

logging.basicConfig(level=logging.INFO)


def delete_topic(bootstrap_servers, topic_name):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        
        # Check if the topic exists
        topic_list = admin_client.list_topics()
        if topic_name not in topic_list:
            logging.info(f"Topic '{topic_name}' does not exist.")
            return

        # Delete the topic
        admin_client.delete_topics(topics=[topic_name])

        logging.info(f"Topic '{topic_name}' deleted successfully.")
    except Exception as e:
        logging.error(f"Error occurred while deleting the topic: {e}")

if __name__ == "__main__":
    bootstrap_servers = "localhost:9092"
    topic_names = ["patient_data", "staff_communication", "environmental_data", "vital_parameters", "entry_exit_events", "operation_room_status", "operation_team", "patient_entry_exit_events"]
    
    for topic in topic_names:
        delete_topic(bootstrap_servers, topic)

    # delete_topic(bootstrap_servers, "vital_parameters")