import logging
class Blocks:
    def __init__(self, config, database, sql):
        """
        Initialize the Blocks module
        
        Args:
            config: DelegateConfig instance for the specific delegate
            database: Database connection for blockchain data
            sql: SQL connection for TBW data
        """
        self.database = database
        self.sql = sql
        self.config = config
        self.logger = logging.getLogger(f'blocks_{config.username}')
        self.logger.info(f"Initializing Blocks module for delegate: {config.username}")
        
    
    def get_last_block(self):
        """Get the last processed block from the database"""
        self.logger.debug("Getting last processed block")
        self.sql.open_connection()
        last_block = self.sql.last_block().fetchall()
        self.sql.close_connection()

        if last_block:
            self.logger.debug(f"Last block timestamp: {last_block[0][0]}, height: {last_block[0][1]}")
        else:
            self.logger.debug("No last block found")
        return last_block
        
        
    def get_new_blocks(self, last_block):
        """Get new blocks since the last processed block"""
        self.logger.debug(f"Getting new blocks since timestamp: {last_block[0][0]}")
        self.database.open_connection()
        new_blocks = self.database.get_limit_blocks(last_block[0][0])
        self.database.close_connection()
        
        if new_blocks:
            self.logger.info(f"Found {len(new_blocks)} new blocks to process")
        else:
            self.logger.debug("No new blocks found")
            
        return new_blocks
        
        
    def store_new_blocks(self, new_blocks):
        """Store new blocks in the database"""
        if not new_blocks:
            self.logger.debug("No new blocks to store")
            return
            
        self.logger.debug(f"Storing {len(new_blocks)} new blocks")
        self.sql.open_connection()
        self.sql.store_blocks(new_blocks)
        self.sql.close_connection()
        self.logger.info(f"Stored {len(new_blocks)} new blocks")
        
        
    def return_unprocessed_blocks(self):
        """Get blocks that haven't been processed yet"""
        self.logger.debug("Getting unprocessed blocks")
        self.sql.open_connection()
        unprocessed_blocks = self.sql.unprocessed_blocks().fetchall()
        self.sql.close_connection()
        
        if unprocessed_blocks:
            self.logger.info(f"Found {len(unprocessed_blocks)} unprocessed blocks")
        else:
            self.logger.debug("No unprocessed blocks found")
            
        return unprocessed_blocks
    
    
    def block_counter(self):
        """Count the number of processed blocks"""
        self.logger.debug("Counting processed blocks")
        self.sql.open_connection()
        processed_blocks = self.sql.processed_blocks().fetchall()
        self.sql.close_connection()
        
        count = len(processed_blocks)
        self.logger.debug(f"Found {count} processed blocks")
        return count
       
