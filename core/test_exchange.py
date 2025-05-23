#!/usr/bin/env python
import argparse
import logging
from pathlib import Path

from config.delegate_config import DelegateConfig
from utility.delegate_manager import DelegateManager
from network.network import Network
from modules.exchange import Exchange
from utility.sql import Sql
from utility.utility import Utility


def setup_logging(delegate_name):
    """Set up logging for the delegate"""
    log_dir = Path.home() / "core3-tbw" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"exchange_test_{delegate_name}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(f'exchange_test_{delegate_name}')
    return logger


def test_delegate_exchange(delegate_name):
    """Test exchange functionality for a single delegate"""
    logger = setup_logging(delegate_name)
    logger.info(f"Starting exchange test for delegate: {delegate_name}")
    
    try:
        # get configuration for this delegate
        config = DelegateConfig(delegate_name)
        logger.info(f"Loaded configuration for delegate: {delegate_name}")
        
        # load network
        network = Network(config.network)
        logger.info(f"Loaded network configuration: {config.network}")
        
        # load utility
        utility = Utility(network)
        logger.info("Initialized utility module")
       
        # connect to tbw script database and exchange module
        sql = Sql(delegate_name)
        exchange = Exchange(sql, config)
        logger.info("Connected to database and initialized exchange module")
        
        addresses = [i for i in config.convert_address]
        logger.info(f"Found {len(addresses)} exchange addresses to test")
        
        if not addresses:
            logger.warning("No exchange addresses configured for this delegate")
            print("No exchange addresses configured for this delegate")
            return
            
        for i in addresses:
            amount = 50000000000  # Test amount
            logger.info(f"Testing exchange for address {i} with amount {amount}")
            
            if i in config.convert_address:
                index = config.convert_address.index(i)
                logger.debug(f"Found exchange configuration at index {index}")
                
                provider = config.provider[index]
                logger.info(f"Using exchange provider: {provider}")
                
                pay_in = exchange.exchange_select(index, i, amount, provider)
                logger.info(f"Exchange test result - pay in address: {pay_in}")
                
                # delete exchange record
                new_amount = exchange.truncate(amount/config.atomic, 4)
                logger.debug(f"Deleting test exchange record: {i} -> {pay_in}, amount: {new_amount}")
                
                sql.open_connection()
                sql.delete_test_exchange(i, pay_in, new_amount)
                sql.close_connection()
                logger.info("Test exchange record deleted")
            else:
                logger.warning(f"Address {i} not found in convert_address list")
                
        logger.info("Exchange test completed successfully")
        
    except Exception as e:
        logger.error(f"Error in exchange test: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    print("Start Script")
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Test Exchange Functionality')
    parser.add_argument('--delegate', '-d', help='Delegate name to test exchange for', default=None)
    parser.add_argument('--all', '-a', action='store_true', help='Test exchange for all delegates')
    args = parser.parse_args()
    
    # Initialize delegate manager
    delegate_manager = DelegateManager(None)
    
    if args.all:
        # Test all delegates
        delegate_names = list(delegate_manager.get_delegate_names())
        print(f"Testing exchange for all {len(delegate_names)} delegates")
        
        for delegate_name in delegate_names:
            print(f"\nTesting exchange for delegate: {delegate_name}")
            test_delegate_exchange(delegate_name)
            
    elif args.delegate:
        # Test a single delegate
         (args.delegate)
    else:
        # No arguments provided, show help
        parser.print_help()
