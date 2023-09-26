import logging
import socket
import json
import time
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from config import CONFIG_FILE_PATH
from config_loader import ConfigLoader


class UDPToUDP:
    def __init__(self, config):
        self.config = config.load_config('udp_server')
        self._setup_services()
        self._setup_logging()
    
    def _setup_services(self):
        """Initialize all services"""
        self.udp_server = self._init_udp_server()
    
    def _setup_logging(self):
        """Initialize logging configuration."""
        self.logger = logging.getLogger(__name__)
    
    def _init_udp_server(self):
        """Initialize UDP server."""
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind((self.config['host'], self.config['port']))
        return udp_server
    
    def send_to(self, message, address):
        """Send message to address."""
        message_to_send = json.dumps(message).encode('utf-8')
        self.udp_server.sendto(message, address)
    
    def recieved_from(self, buffer_size):
        """Receive message from address."""
        message, address = self.udp_server.recvfrom(buffer_size)
        return message, address
    
    def close(self):
        """Close all services."""
        self.udp_server.close()

def get_config(config_file_path):
    """Return configuration settings."""
    config_loader = ConfigLoader(config_file_path)
    return config_loader.get_all_configs()




if __name__ == "__main__":

    average_latency = 0
    average_drift = 0
    latency_samples = []
    drift_samples = []

    config = get_config(CONFIG_FILE_PATH)
    client_config = config['udp_client']
    client_address = (client_config['host'], client_config['port'])
    udp_server = UDPToUDP(config)
    
    


    while True:
        server_send_time = time.time()
        message_to_send = {'server_send_time': server_send_time}
        # Send time to client
        udp_server.send_to(message_to_send, client_address)
        
        # Wait for a packet from the client
        message, address = udp_server.recieved_from(1024)
        message = json.loads(message.decode('utf-8'))

        server_received_time = time.time()
        
        client_send_time = message['client_send_time']
        client_received_time = message['client_received_time']

        latency = (server_received_time - server_send_time) - (client_send_time - client_received_time)
        message_transfer_duration = abs(latency / 2)
        clock_drift = ((client_received_time - server_send_time) - (server_received_time - client_send_time)) / 2

        latency_samples.append(message_transfer_duration)
        drift_samples.append(clock_drift)
        
        if len(latency_samples) > 100:
            latency_samples.pop(0)
        if len(drift_samples) > 100:
            drift_samples.pop(0)

        average_latency = sum(latency_samples) / len(latency_samples)
        average_drift = sum(drift_samples) / len(drift_samples)
        
        print(f"Average Latency: {average_latency}, Average Clock Drift: {average_drift}")
