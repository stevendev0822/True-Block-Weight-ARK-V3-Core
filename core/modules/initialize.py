import os
from pathlib import Path
import logging

class Initialize:
    def __init__(self, config, database, sql):
        """
        Initialize the database for a delegate
        
        Args:
            config: DelegateConfig instance for the specific delegate
            database: Database connection for blockchain data
            sql: SQL connection for TBW data
        """
        self.home = str(Path.home())
        self.database = database
        self.sql = sql
        self.config = config
        
        # Set up logging
        self.logger = logging.getLogger(f'initialize_{config.username}')
        self.logger.info(f"Initializing database for delegate: {config.username}")
        
        # Create delegate-specific data directory if it doesn't exist
        delegate_data_dir = f"{self.home}/core3-tbw/core/data/{config.username}"
        os.makedirs(delegate_data_dir, exist_ok=True)
        
        data_path = f"{delegate_data_dir}/tbw.db"
        
        if os.path.exists(data_path) == False:
            self.logger.info(f"Database not found at {data_path}, initializing new database")
            self.initialize()
            self.logger.info("Database initialization complete")
            quit()
        else:
            self.logger.info(f"Database detected at {data_path} - no initialization needed")
            print("Database detected - no initialization needed")

        self.update_delegate_records()
    
    def initialize(self):
        """Initialize the database with blocks and mark them as processed"""
        self.logger.info("Setting up database")
        self.sql.open_connection()
        
        print("Setting up database")
        self.sql.setup()
        
        print("Importing forged blocks")
        self.logger.info("Importing forged blocks from blockchain database")
        self.database.open_connection()
        total_blocks = self.database.get_all_blocks()
        self.database.close_connection()
            
        print("Storing forged blocks in database")
        self.logger.info(f"Storing {len(total_blocks)} forged blocks in database")
        self.sql.store_blocks(total_blocks)
            
        print("Marking blocks processed up to starting block {}".format(self.config.start_block))
        self.logger.info(f"Marking blocks processed up to starting block {self.config.start_block}")
        self.sql.mark_processed(self.config.start_block, initial = "Y")
        processed_blocks = self.sql.processed_blocks().fetchall()
        self.sql.close_connection()
            
        print("Total blocks imported - {}".format(len(total_blocks)))
        print("Total blocks marked as processed - {}".format(len(processed_blocks)))
        print("Finished setting up database")
        
        self.logger.info(f"Total blocks imported: {len(total_blocks)}")
        self.logger.info(f"Total blocks marked as processed: {len(processed_blocks)}")
        self.logger.info("Finished setting up database")

    
    def update_delegate_records(self):
        """Update delegate reward records in the database"""
        self.logger.info("Updating delegate reward records")
        self.sql.open_connection()
        accounts = [i for i in self.config.delegate_fee_address]
        self.logger.debug(f"Storing delegate rewards for accounts: {accounts}")
        self.sql.store_delegate_rewards(accounts)
        self.sql.close_connection()
        self.logger.info("Delegate reward records updated")
