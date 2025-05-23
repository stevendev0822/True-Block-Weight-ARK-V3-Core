#!/usr/bin/env python
import argparse
import logging
import time
from pathlib import Path

from config.delegate_config import DelegateConfig
from utility.delegate_manager import DelegateManager
from network.network import Network
from modules.allocate import Allocate
from modules.blocks import Blocks
from modules.initialize import Initialize
from modules.stage import Stage
from modules.voters import Voters
from utility.database import Database
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility


def setup_logging(delegate_name):
    """Set up logging for the delegate"""
    log_dir = Path.home() / "True-Block-Weight-ARK-V3-Core" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"tbw_{delegate_name}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(f'tbw_{delegate_name}')
    return logger



def update_voter_share(sql, config):
    """Update voter share rate for all voters"""
    logger = logging.getLogger(f'tbw_{config.username}')
    logger.info("Updating voter share rates")
    
    old_rate = float(input("Enter old share rate in the following format (80): "))
    sql.open_connection()
    voters = sql.all_voters().fetchall()
    
    updated_count = 0
    for i in voters:
        if i[4] == old_rate:
            sql.update_voter_share(i[0], config.voter_share)
            updated_count += 1

    sql.close_connection()
    logger.info(f"Share rate updated for {updated_count} voters from {old_rate}% to {config.voter_share}%")
    print("Share rate updated")
    quit()


def update_custom_share(sql, config):
    """Update custom share rate for a specific voter"""
    logger = logging.getLogger(f'tbw_{config.username}')
    
    address = input("Enter address to update with custom rate: ")
    new_rate = float(input("Enter custom share rate in the following format (80): "))
    
    logger.info(f"Updating custom share rate for address {address} to {new_rate}%")
    
    sql.open_connection()
    sql.update_voter_share(address, new_rate)
    sql.close_connection()
    
    logger.info(f"Custom share rate updated successfully")
    print("Address {} updated with custom rate of: {}".format(address, new_rate))
    quit()


def force_manual_pay(config, dynamic, sql):
    """Force a manual payment run"""
    logger = logging.getLogger(f'tbw_{config.username}')
    logger.info("Forcing manual payment run")
    
    # set fake block_count
    block_count = 1
    stage, unpaid_voters, unpaid_delegate = interval_check(block_count, config.interval, config.manual_pay, logger)
        
    # check if true to stage payments
    if stage == True and sum(unpaid_voters.values()) > 0:
        logger.info(f"Staging payments for {len(unpaid_voters)} voters")
        print("Staging payments")
        s = Stage(config, dynamic, sql, unpaid_voters, unpaid_delegate)
    else:
        logger.info("No payments to stage")
    
    quit()


def interval_check(block_count, interval, sql, manual="N", logger=None):
    """Check if payment interval has been reached"""
    if logger:
        logger.debug(f"Checking payment interval: block_count={block_count}, interval={interval}, manual={manual}")
    
    if block_count % interval == 0 or manual == "Y":
        if logger:
            logger.info("Payout interval reached")
        print("Payout interval reached")
        
        sql.open_connection()
        voter_balances = sql.voters().fetchall()
        delegate_balances = sql.rewards().fetchall()
        sql.close_connection()
        
        voter_unpaid = {i[0]:i[2] for i in voter_balances}
        delegate_unpaid = {i[0]:i[1] for i in delegate_balances}
        
        if logger:
            logger.debug(f"Found {len(voter_unpaid)} voters with unpaid balances")
            logger.debug(f"Found {len(delegate_unpaid)} delegate accounts with unpaid balances")
        
        # check if there is a positive unpaid balance
        if sum(voter_unpaid.values()) > 0:
            stage = True
            if logger:
                logger.info(f"Positive unpaid balance found: {sum(voter_unpaid.values())}")
        else:
            stage = False
            if logger:
                logger.info("No positive unpaid balance found")
    else:
        if logger:
            logger.debug("Payout interval not reached")
        stage = False
        voter_unpaid = {}
        delegate_unpaid = {}
    
    return stage, voter_unpaid, delegate_unpaid


def process_delegate(delegate_name):
    """Process a single delegate's true block weight calculations"""
    logger = setup_logging(delegate_name)
    logger.info(f"Starting TBW process for delegate: {delegate_name}")
    
    # get configuration for this delegate
    config = DelegateConfig(delegate_name)
    logger.info(f"Loaded configuration for delegate: {delegate_name}")
    
    # load network
    network = Network(config.network)
    logger.info(f"Loaded network configuration: {config.network}")
    
    # load utility and dynamic
    utility = Utility(network)
    dynamic = Dynamic(utility, config)
    logger.info("Initialized utility and dynamic modules")
    
    # connect to core and tbw script database
    database = Database(config, network)
    sql = Sql(delegate_name)
    logger.info("Connected to databases")
    
    # check if initialized
    Initialize(config, database, sql)
    
    # update all voter share
    if config.update_share == "Y":
        logger.info("Update share flag is set, updating voter shares")
        update_voter_share(sql, config)
    
    # check if manual pay flag is set
    if config.manual_pay == "Y":
        logger.info("Manual pay flag is set, forcing payment")
        force_manual_pay(config, dynamic, sql)

    # check if custom share flag is set
    if config.custom == "Y":
        logger.info("Custom share flag is set, updating custom share")
        update_custom_share(sql, config)
    
    # MAIN FUNCTION LOOP SHOULD START HERE
    logger.info("Starting main processing loop")
    while True:
        try:
            # get blocks
            block = Blocks(config, database, sql)
        
            # get last block to start
            last_block = block.get_last_block()
            if last_block:
                logger.info(f"Last Block Height Retrieved: {last_block[0][1]}")
                print("Last Block Height Retrieved: ", last_block[0][1])
            else:
                logger.warning("No last block found, waiting for next cycle")
                time.sleep(1200)
                continue
        
            # use last block timestamp to get all new blocks
            new_blocks = block.get_new_blocks(last_block)
        
            # store all new blocks
            block.store_new_blocks(new_blocks)
        
            # get unprocessed blocks
            unprocessed_blocks = block.return_unprocessed_blocks()
        
            # allocate block rewards
            allocate = Allocate(database, config, sql)
            voter_options = Voters(config, sql)
        
            for unprocessed in unprocessed_blocks:
                tic_a = time.perf_counter()
                logger.info(f"Processing unprocessed block at height {unprocessed[4]}")
                print("\nUnprocessed Block Information\n", unprocessed)
                
                block_timestamp = unprocessed[1]
                # get vote and unvote transactions
                vote, unvote = allocate.get_vote_transactions(block_timestamp)
                tic_b = time.perf_counter()
                print(f"Get all Vote and Unvote transactions in {tic_b - tic_a:0.4f} seconds")
                
                # create voter_roll
                voter_roll = allocate.create_voter_roll(vote, unvote)
                tic_c = time.perf_counter()
                print(f"Create voter rolls in {tic_c - tic_b:0.4f} seconds")
                
                # get voter_balances
                voter_balances = allocate.get_voter_balance(unprocessed, voter_roll)
                tic_d = time.perf_counter()
                print(f"Get all voter balances in {tic_d - tic_c:0.4f} seconds")
                
                print("\noriginal voter_balances")
                for k, v in voter_balances.items():
                    print(k, v / config.atomic)
                
                # run voters through various vote_options
                if config.whitelist == 'Y':
                    voter_balances = voter_options.process_whitelist(voter_balances)
                if config.whitelist == 'N' and config.blacklist =='Y':
                    voter_balances = voter_options.process_blacklist(voter_balances)
                    
                voter_balances = voter_options.process_voter_cap(voter_balances)
                voter_balances = voter_options.process_voter_min(voter_balances)
                voter_balances = voter_options.process_anti_dilution(voter_balances)
                tic_e = time.perf_counter()
                print(f"Process all voter options in {tic_e - tic_d:0.4f} seconds")
                
                # allocate block rewards
                allocate.block_allocations(unprocessed, voter_balances)
                tic_f = time.perf_counter()
                print(f"Allocate block rewards in {tic_f - tic_e:0.4f} seconds")
                
                # get block count
                block_count = block.block_counter()
                print(f"\nCurrent block count : {block_count}")
                
                tic_g = time.perf_counter()
                print(f"Processed block in {tic_g - tic_a:0.4f} seconds")
                logger.info(f"Block {unprocessed[4]} processed in {tic_g - tic_a:0.4f} seconds")
            
                # check interval for payout
                stage, unpaid_voters, unpaid_delegate = interval_check(block_count, config.interval, logger=logger)
            
                # check if true to stage payments
                if stage == True and sum(unpaid_voters.values()) > 0:
                    logger.info("Staging payments")
                    print("Staging payments")
                    s = Stage(config, dynamic, sql, unpaid_voters, unpaid_delegate)
            
            logger.info("Completed processing cycle, sleeping before next check")
            print("End Script - Looping")
            time.sleep(1200)
            
        except Exception as e:
            logger.error(f"Error in main processing loop: {str(e)}", exc_info=True)
            print(f"Error: {str(e)}")
            time.sleep(300)  # Sleep for 5 minutes on error


if __name__ == '__main__':
    print("Start Script")
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='True Block Weight Calculator')
    parser.add_argument('--delegate', '-d', help='Delegate name to process', default=None)
    parser.add_argument('--all', '-a', action='store_true', help='Process all delegates')
    args = parser.parse_args()
    
    # Initialize delegate manager
    delegate_manager = DelegateManager(None)
    
    if args.all:
        # Process all delegates
        delegate_names = list(delegate_manager.get_delegate_names())
        print(f"Processing all {len(delegate_names)} delegates")
        
        # Import multiprocessing here to avoid issues with Windows
        import multiprocessing
        
        # Create a process for each delegate
        processes = []
        for delegate_name in delegate_names:
            p = multiprocessing.Process(target=process_delegate, args=(delegate_name,))
            processes.append(p)
            p.start()
            
        # Wait for all processes to complete
        for p in processes:
            p.join()
            
    elif args.delegate:
        # Process a single delegate
        process_delegate(args.delegate)
    else:
        # No arguments provided, show help
        parser.print_help()