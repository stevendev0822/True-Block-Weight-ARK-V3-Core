import os
import json
import tempfile
import unittest
import logging
from pathlib import Path
from utility.delegate_manager import DelegateManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_delegate_manager.log"),
        logging.StreamHandler()
    ]
)

class TestDelegateManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment with a temporary delegates.json file"""
        self.logger = logging.getLogger('test_delegate_manager')
        self.logger.info("Setting up test environment")
        
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.logger.debug(f"Created temporary directory: {self.temp_dir.name}")
        
        # Create the directory structure
        os.makedirs(os.path.join(self.temp_dir.name, 'True-Block-Weight-ARK-V3-Core/core/config'), exist_ok=True)
        self.logger.debug("Created directory structure")
        
        # Create a test delegates.json file
        self.test_delegates = {
            "delegates": [
                {
                    "name": "delegate1",
                    "static": {
                        "atomic": 100000000,
                        "network": "ark_devnet",
                        "start_block": 0
                    },
                    "delegate": {
                        "message": "Thank you for voting delegate1",
                        "voter_share": 90,
                        "voter_cap": 0,
                        "voter_min": 0,
                        "whitelist": False,
                        "whitelist_address": [],
                        "blacklist": False,
                        "blacklist_address": []
                    }
                },
                {
                    "name": "delegate2",
                    "static": {
                        "atomic": 100000000,
                        "network": "ark_devnet",
                        "start_block": 0
                    },
                    "delegate": {
                        "message": "Thank you for voting delegate2",
                        "voter_share": 80,
                        "voter_cap": 0,
                        "voter_min": 0,
                        "whitelist": False,
                        "whitelist_address": [],
                        "blacklist": False,
                        "blacklist_address": []
                    }
                }
            ]
        }
        
        self.delegates_file = os.path.join(self.temp_dir.name, 'True-Block-Weight-ARK-V3-Core/core/config/delegates.json')
        with open(self.delegates_file, 'w') as f:
            json.dump(self.test_delegates, f, indent=4)
        self.logger.debug(f"Created test delegates.json at {self.delegates_file}")
        
        # Save original home directory
        self.original_home = str(Path.home())
        self.logger.debug(f"Original home directory: {self.original_home}")
        
        # Patch the home directory for testing
        Path.home = lambda: Path(self.temp_dir.name)
        self.logger.debug(f"Patched home directory to: {self.temp_dir.name}")
    
    def tearDown(self):
        """Clean up after tests"""
        self.logger.info("Tearing down test environment")
        
        # Restore original home directory
        Path.home = lambda: Path(self.original_home)
        self.logger.debug("Restored original home directory")
        
        # Clean up temporary directory
        self.temp_dir.cleanup()
        self.logger.debug("Cleaned up temporary directory")
    
    def test_init_and_load_delegates(self):
        """Test initialization and loading of delegates"""
        self.logger.info("Testing initialization and loading of delegates")
        
        manager = DelegateManager(None)
        
        # Check if delegates were loaded
        self.assertEqual(len(manager.delegates), 2)
        self.assertIn('delegate1', manager.delegates)
        self.assertIn('delegate2', manager.delegates)
        
        self.logger.info("Initialization and loading test passed")
    
    def test_get_delegate_config(self):
        """Test retrieving a specific delegate configuration"""
        self.logger.info("Testing get_delegate_config method")
        
        manager = DelegateManager(None)
        
        # Get delegate1 config
        self.logger.debug("Retrieving delegate1 config")
        delegate1_config = manager.get_delegate_config('delegate1')
        self.assertIsNotNone(delegate1_config)
        self.assertEqual(delegate1_config['name'], 'delegate1')
        self.assertEqual(delegate1_config['delegate']['voter_share'], 90)
        
        # Get delegate2 config
        self.logger.debug("Retrieving delegate2 config")
        delegate2_config = manager.get_delegate_config('delegate2')
        self.assertIsNotNone(delegate2_config)
        self.assertEqual(delegate2_config['name'], 'delegate2')
        self.assertEqual(delegate2_config['delegate']['voter_share'], 80)
        
        # Try to get non-existent delegate
        self.logger.debug("Retrieving non-existent delegate config")
        nonexistent_config = manager.get_delegate_config('nonexistent')
        self.assertIsNone(nonexistent_config)
        
        self.logger.info("get_delegate_config test passed")
    
    def test_get_all_delegates(self):
        """Test retrieving all delegate configurations"""
        self.logger.info("Testing get_all_delegates method")
        
        manager = DelegateManager(None)
        
        # Get all delegates
        self.logger.debug("Retrieving all delegates")
        all_delegates = list(manager.get_all_delegates())
        
        # Check if we got the right number of delegates
        self.assertEqual(len(all_delegates), 2)
        
        # Check if the delegate configurations are complete
        delegate_names = [delegate['name'] for delegate in all_delegates]
        self.assertIn('delegate1', delegate_names)
        self.assertIn('delegate2', delegate_names)
        
        # Find delegate1 and check its configuration
        for delegate in all_delegates:
            if delegate['name'] == 'delegate1':
                self.assertEqual(delegate['delegate']['voter_share'], 90)
                self.logger.debug("Verified delegate1 configuration")
            elif delegate['name'] == 'delegate2':
                self.assertEqual(delegate['delegate']['voter_share'], 80)
                self.logger.debug("Verified delegate2 configuration")
        
        self.logger.info("get_all_delegates test passed")
    
    def test_get_delegate_names(self):
        """Test retrieving all delegate names"""
        self.logger.info("Testing get_delegate_names method")
        
        manager = DelegateManager(None)
        
        # Get all delegate names
        self.logger.debug("Retrieving all delegate names")
        delegate_names = list(manager.get_delegate_names())
        
        # Check if we got the right delegate names
        self.assertEqual(len(delegate_names), 2)
        self.assertIn('delegate1', delegate_names)
        self.assertIn('delegate2', delegate_names)
        
        self.logger.info("get_delegate_names test passed")
    
    def test_file_not_found(self):
        """Test behavior when delegates.json is not found"""
        self.logger.info("Testing behavior when delegates.json is not found")
        
        # Remove the delegates file
        os.remove(self.delegates_file)
        self.logger.debug(f"Removed delegates file: {self.delegates_file}")
        
        # Capture stdout to check for warning message
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Initialize manager, which should print a warning
        self.logger.debug("Initializing DelegateManager with missing file")
        manager = DelegateManager(None)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Check if warning was printed
        output = captured_output.getvalue()
        self.assertIn("Warning: Delegates configuration file not found", output)
        self.logger.debug(f"Captured output: {output}")
        
        # Check if delegates is empty
        self.assertEqual(len(manager.delegates), 0)
        
        self.logger.info("File not found test passed")

if __name__ == '__main__':
    unittest.main()
