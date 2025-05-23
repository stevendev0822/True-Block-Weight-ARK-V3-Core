from configparser import ConfigParser
from pathlib import Path
import os


class Network:
    def __init__(self, network):
        self.home = str(Path.home())
        self.network = network
        
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))  # network directory
        
        # Construct the path to the network file
        env_path = os.path.join(current_dir, self.network)
        
        # Print debug information
        print(f"Loading network configuration from: {env_path}")
        
        # Check if the file exists
        if not os.path.exists(env_path):
            raise FileNotFoundError(f"Network configuration file not found: {env_path}")
        
        config = ConfigParser()
        config.read(env_path)
        
        # Print sections for debugging
        print(f"Available sections in config: {config.sections()}")
        
        self.load_network(config)

    def load_network(self, c):
        self.epoch = c.get("network", "epoch").split(",")
        self.version = int(c.get("network", "version"))
        self.wif = int(c.get("network", "wif"))
        self.api = int(c.get("network", "api"))
        self.database = c.get("network", "database")
        self.database_host = c.get("network", "database_host", fallback="127.0.0.1")
        self.user = c.get("network", "user")
        self.password = c.get("network", "password")
