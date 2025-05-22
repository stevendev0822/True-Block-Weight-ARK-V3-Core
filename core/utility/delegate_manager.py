import json
import os
import logging
from pathlib import Path

class DelegateManager:
    def __init__(self, config):
        self.logger = logging.getLogger('delegate_manager')
        self.logger.info("Initializing DelegateManager")
        
        self.home = str(Path.home()) 
        self.config = config
        self.delegates = {}
        self.load_delegates()     
        
    def load_delegates(self):
        delegates_file = f"{self.home}/True-Block-Weight-ARK-V3-Core/core/config/delegates.json"
        self.logger.info(f"Loading delegates from {delegates_file}")
        
        if os.path.exists(delegates_file):
            try:
                with open(delegates_file, 'r') as f:
                    data = json.load(f)
                    
                    for delegate_config in data.get('delegates', []):
                        delegate_name = delegate_config.get('name')
                        if delegate_name:
                            self.delegates[delegate_name] = delegate_config
                            self.logger.info(f"Loaded configuration for delegate: {delegate_name}")
                
                self.logger.info(f"Successfully loaded {len(self.delegates)} delegates")
            except Exception as e:
                self.logger.error(f"Error loading delegates file: {str(e)}")
                print(f"Error loading delegates file: {str(e)}")
        else:
            self.logger.warning(f"Warning: Delegates configuration file not found at {delegates_file}")
            print(f"Warning: Delegates configuration file not found at {delegates_file}")
    
    def get_delegate_config(self, delegate_name):
        self.logger.debug(f"Retrieving configuration for delegate: {delegate_name}")
        config = self.delegates.get(delegate_name)
        if config:
            self.logger.debug(f"Found configuration for delegate: {delegate_name}")
        else:
            self.logger.warning(f"Configuration not found for delegate: {delegate_name}")
        return config
    
    def get_all_delegates(self):
        self.logger.debug(f"Retrieving all delegate configurations, count: {len(self.delegates)}")
        return self.delegates.values()
    
    def get_delegate_names(self):
        self.logger.debug(f"Retrieving all delegate names, count: {len(self.delegates)}")
        return self.delegates.keys()
