import json
import os
from pathlib import Path

class DelegateManager:
    def __init__(self, config):
        self.home = str(Path.home())
        self.config = config
        self.delegates = {}
        self.load_delegates()
        
    def load_delegates(self):
        delegates_file = f"{self.home}/core3-tbw/core/config/delegates.json"
        
        if os.path.exists(delegates_file):
            with open(delegates_file, 'r') as f:
                data = json.load(f)
                
                for delegate_config in data.get('delegates', []):
                    delegate_name = delegate_config.get('name')
                    if delegate_name:
                        self.delegates[delegate_name] = delegate_config
        else:
            print(f"Warning: Delegates configuration file not found at {delegates_file}")
    
    def get_delegate_config(self, delegate_name):
        return self.delegates.get(delegate_name)
    
    def get_all_delegates(self):
        return self.delegates.keys()
    
    def add_delegate(self, delegate_config):
        """Add a new delegate to the configuration"""
        delegate_name = delegate_config.get('name')
        if not delegate_name:
            raise ValueError("Delegate configuration must include a name")
        
        delegates_file = f"{self.home}/core3-tbw/core/config/delegates.json"
        
        if os.path.exists(delegates_file):
            with open(delegates_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"delegates": []}
        
        # Check if delegate already exists
        for i, existing in enumerate(data.get('delegates', [])):
            if existing.get('name') == delegate_name:
                # Update existing delegate
                data['delegates'][i] = delegate_config
                break
        else:
            # Add new delegate
            data['delegates'].append(delegate_config)
        
        # Save updated configuration
        with open(delegates_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update in-memory configuration
        self.delegates[delegate_name] = delegate_config
        
        return True
    
    def remove_delegate(self, delegate_name):
        """Remove a delegate from the configuration"""
        delegates_file = f"{self.home}/core3-tbw/core/config/delegates.json"
        
        if os.path.exists(delegates_file):
            with open(delegates_file, 'r') as f:
                data = json.load(f)
            
            # Filter out the delegate to remove
            data['delegates'] = [d for d in data.get('delegates', []) if d.get('name') != delegate_name]
            
            # Save updated configuration
            with open(delegates_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Update in-memory configuration
            if delegate_name in self.delegates:
                del self.delegates[delegate_name]
            
            return True
        
        return False
