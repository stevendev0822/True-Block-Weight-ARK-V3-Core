#!/usr/bin/env python
import argparse
import logging
import time
from pathlib import Path

from config.delegate_config import DelegateConfig
from utility.delegate_manager import DelegateManager
from network.network import Network
from modules.exchange import Exchange
from modules.payments import Payments
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility


def setup_logging(delegate_name):
    """Set up logging for the delegate"""
    log_dir = Path.home() / "True-Block-Weight-ARK-V3-Core" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"pay_{delegate_name}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(f'pay_{delegate_name}')
    return logger

def chunks(l, n):
    """Split a list into chunks of size n"""
    # For item i in a range that is a length of l
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def process_multi_payments(payment, unprocessed, dynamic, config, exchange, sql, logger):
    """Process payments using multi-payment transactions"""
    logger.info(f"Processing multi-payment for {len(unprocessed)} transactions")
    print("Multi Payment")

    signed_tx = []
    check = {} 
    request_limit = dynamic.get_tx_request_limit()
    multi_limit = dynamic.get_multipay_limit()

    logger.debug(f"Transaction request limit: {request_limit}, multi-payment limit: {multi_limit}")
   
    if len(unprocessed) == 1:
        logger.info("Only one payment, using standard payment method")
        process_standard_payments(payment, unprocessed, dynamic, config, exchange, sql)
    else:
        temp_multi_chunk = list(chunks(unprocessed, multi_limit))
        # remove any items over request_tx_limit
        multi_chunk = temp_multi_chunk[:request_limit]
        logger.debug(f"Created {len(multi_chunk)} multi-payment chunks (max {request_limit} of {len(temp_multi_chunk)})")
        nonce = payment.get_nonce() + 1
        logger.debug(f"Starting nonce: {nonce}")
        
        for i in multi_chunk:
            if len(i) > 1:
                unique_rowid = [y[0] for y in i]
                logger.debug(f"Building multi-payment transaction for {len(i)} payments with nonce {nonce}")
                tx = payment.build_multi_transaction(i, str(nonce))
                check[tx['id']] = unique_rowid
                signed_tx.append(tx)
                nonce += 1
                logger.debug(f"Transaction {tx['id']} created with {len(i)} payments")
        
        if signed_tx:
            logger.info(f"Broadcasting {len(signed_tx)} multi-payment transactions")
            accepted = payment.broadcast_multi(signed_tx)
            logger.debug(f"Accepted transaction IDs: {accepted}")
            
            #check for accepted and non-accepted transactions
            for k, v in check.items():
                if k in accepted:
                    # mark all accepted records complete
                    logger.info(f"Transaction {k} accepted, marking {len(v)} payments as processed")
                    sql.open_connection()
                    sql.process_staged_payment(v)
                    sql.close_connection()
                else:
                    # delete all transaction records with relevant multipay txid
                    logger.warning(f"Transaction {k} not accepted, deleting transaction record")
                    print("Transaction ID Not Accepted")
                    sql.open_connection()
                    sql.delete_transaction_record(k)
                    sql.close_connection()

            # payment run complete
            logger.info('Payment run completed!')
            print('Payment Run Completed!')
        else:
            logger.warning("No transactions to broadcast")


def process_standard_payments(payment, unprocessed, dynamic, config, exchange, sql, logger):
    """Process payments using standard transfer transactions"""
    logger.info(f"Processing standard payments for {len(unprocessed)} transactions")
    print("Standard Payment")
    
    signed_tx = []
    check = {}

    # process unpaid transactions
    unique_rowid = [y[0] for y in unprocessed]
    logger.debug(f"Processing {len(unique_rowid)} unique row IDs")

    temp_nonce = payment.get_nonce() + 1
    transaction_fee = dynamic.get_dynamic_fee()
    logger.debug(f"Starting nonce: {temp_nonce}, transaction fee: {transaction_fee}")
        
    for i in unprocessed:
        # exchange processing
        if i[1] in config.convert_address and config.exchange == "Y":
            index = config.convert_address.index(i[1])
            logger.debug(f"Processing exchange for payment to {i[1]}")
            pay_in = exchange.exchange_select(index, i[1], i[2], config.provider[index])
            logger.debug(f"Exchange address: {pay_in}")
            tx = payment.build_transfer_transaction(pay_in, (i[2]), i[3], transaction_fee, str(temp_nonce))
        # standard tx processing
        else:           
            logger.debug(f"Processing standard payment to {i[1]} for {i[2]}")
            tx = payment.build_transfer_transaction(i[1], (i[2]), i[3], transaction_fee, str(temp_nonce))
            
        check[tx['id']] = i[0]
        signed_tx.append(tx)
        logger.debug(f"Transaction {tx['id']} created with nonce {temp_nonce}")
        temp_nonce += 1
    
    if signed_tx:
        logger.info(f"Broadcasting {len(signed_tx)} standard transactions")
        accepted = payment.broadcast_standard(signed_tx)
        logger.debug(f"Accepted transaction IDs: {accepted}")
        
        for_removal = payment.non_accept_check(check, accepted)
                
        # remove non-accepted transactions from being marked as completed
        if len(for_removal) > 0:
            logger.warning(f"{len(for_removal)} transactions were not accepted")
            for i in for_removal:
                logger.debug(f"Removing RowId: {i}")
                print("Removing RowId: ", i)
                unique_rowid.remove(i)
                    
        sql.open_connection()
        sql.process_staged_payment(unique_rowid)
        sql.close_connection()
        logger.info(f"Marked {len(unique_rowid)} payments as processed")

        # payment run complete
        logger.info('Payment run completed!')
        print('Payment Run Completed!')
    else:
        logger.warning("No transactions to broadcast")


def process_delegate_payments(delegate_name):
    """Process payments for a single delegate"""
    logger = setup_logging(delegate_name)
    logger.info(f"Starting payment process for delegate: {delegate_name}")
    
    try:
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
          
        # connect to tbw script database and exchange module
        sql = Sql(delegate_name)
        exchange = Exchange(sql, config)
        logger.info("Connected to database and initialized exchange module")
        
        # MAIN FUNCTION LOOP SHOULD START HERE
        while True:
            sql.open_connection()
            check = sql.unprocessed_staged_payments()
            sql.close_connection()
            logger.debug(f"Found {check} unprocessed staged payments")
        
            if check > 0:
                # staged payments detected
                logger.info(f"Staged payments detected: {check} payments")
                print("Staged Payments Detected.......Begin Payment Processing")
                payments = Payments(config, sql, dynamic, utility, exchange)
            
                sql.open_connection()
                if config.multi == "Y":
                    logger.info("Using multi-payment transactions")
                    unprocessed = sql.get_staged_payment(multi=config.multi).fetchall()
                    sql.close_connection()
                    process_multi_payments(payments, unprocessed, dynamic, config, exchange, sql, logger)
                else:
                    logger.info("Using standard payment transactions")
                    unprocessed = sql.get_staged_payment(dynamic.get_tx_request_limit()).fetchall()
                    sql.close_connection()
                    process_standard_payments(payments, unprocessed, dynamic, config, exchange, sql, logger)
     
            logger.info("Completed payment cycle, sleeping before next check")
            print("End Script - Looping")
            time.sleep(1200)
            
    except Exception as e:
        logger.error(f"Error in payment process: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")


if __name__ == '__main__':    
    print("Start Script")
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='True Block Weight Payment Processor')
    parser.add_argument('--delegate', '-d', help='Delegate name to process payments for', default=None)
    parser.add_argument('--all', '-a', action='store_true', help='Process payments for all delegates')
    args = parser.parse_args()
    
    # Initialize delegate manager
    delegate_manager = DelegateManager(None)
    
    if args.all:
        # Process all delegates
        delegate_names = list(delegate_manager.get_delegate_names())
        print(f"Processing payments for all {len(delegate_names)} delegates")
        
        # Import multiprocessing here to avoid issues with Windows
        import multiprocessing
        
        # Create a process for each delegate
        processes = []
        for delegate_name in delegate_names:
            p = multiprocessing.Process(target=process_delegate_payments, args=(delegate_name,))
            processes.append(p)
            p.start()
            
        # Wait for all processes to complete
        for p in processes:
            p.join()
            
    elif args.delegate:
        # Process a single delegate
        process_delegate_payments(args.delegate)
    else:
        # No arguments provided, show help
        parser.print_help()