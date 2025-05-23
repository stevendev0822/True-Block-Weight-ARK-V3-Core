from crypto.transactions.builder.transfer import Transfer
from crypto.transactions.builder.multi_payment import MultiPayment
import time
import logging

class Payments:
    def __init__(self, config, sql, dynamic, utility, exchange):
        """
        Initialize the Payments module
        
        Args:
            config: DelegateConfig instance for the specific delegate
            sql: SQL connection for TBW data
            dynamic: Dynamic fee calculator
            utility: Utility instance for network operations
            exchange: Exchange processor for currency conversions
        """
        self.config = config
        self.sql = sql
        self.dynamic = dynamic
        self.utility = utility
        self.exchange = exchange
        self.client = self.utility.get_client()
        
        # Set up logging
        self.logger = logging.getLogger(f'payments_{config.username}')
        self.logger.info(f"Initializing Payments module for delegate: {config.username}")

    
    def non_accept_check(self, c, a):
        """
        Check for transactions that were not accepted by the network
        
        Args:
            c: Dictionary of transaction IDs and values
            a: List of accepted transaction IDs
            
        Returns:
            List of transactions that were not accepted
        """
        self.logger.debug(f"Checking {len(c)} transactions for acceptance")
        removal_check = []
        for k, v in c.items():
            if k not in a:
                self.logger.warning(f"Transaction ID {k} not accepted by network")
                print("Transaction ID Not Accepted")
                removal_check.append(v)
                self.sql.open_connection()
                self.sql.delete_transaction_record(k)
                self.sql.close_connection()
                
        self.logger.info(f"Found {len(removal_check)} transactions not accepted")
        return removal_check
    
    
    def get_nonce(self):
        """Get the current nonce for the delegate wallet"""
        self.logger.debug(f"Getting nonce for delegate: {self.config.delegate}")
        n = self.client.wallets.get(self.config.delegate)
        nonce = int(n['data']['nonce'])
        self.logger.debug(f"Current nonce: {nonce}")
        return nonce

    
    def build_transfer_transaction(self, address, amount, vendor, fee, nonce):
        """
        Build a transfer transaction
        
        Args:
            address: Recipient address
            amount: Amount to send
            vendor: Vendor field message
            fee: Transaction fee
            nonce: Current nonce value
            
        Returns:
            Transaction dictionary
        """
        self.logger.debug(f"Building transfer transaction to {address} for {amount} with nonce {nonce}")
        # python3 crypto version    
        transaction = Transfer(recipientId=address, amount=amount, vendorField=vendor, fee=fee)
        transaction.set_nonce(int(nonce))
        transaction.schnorr_sign(self.config.passphrase)

        sp = self.config.secondphrase
        if sp == 'None':
            sp = None
        if sp is not None:
            self.logger.debug("Applying second signature")
            transaction.second_sign(sp)

        transaction_dict = transaction.to_dict()
        self.logger.debug(f"Transaction built with ID: {transaction_dict['id']}")
        return transaction_dict


    def build_multi_transaction(self, payments, nonce):
        """
        Build a multi-payment transaction
        
        Args:
            payments: List of payment details
            nonce: Current nonce value
            
        Returns:
            Transaction dictionary
        """
        self.logger.debug(f"Building multi-payment transaction with {len(payments)} payments and nonce {nonce}")
        # f = int(self.config.multi_fee * self.config.atomic)
        f = self.dynamic.get_dynamic_fee_multi(len(payments))
        transaction = MultiPayment(vendorField=self.config.message, fee=f)
        transaction.set_nonce(int(nonce))

        for i in payments:
            # exchange processing
            if i[1] in self.config.convert_address and self.config.exchange == "Y":
                index = self.config.convert_address.index(i[1])
                self.logger.debug(f"Processing exchange for payment to {i[1]}")
                pay_in = self.exchange.exchange_select(index, i[1], i[2], self.config.provider[index])
                transaction.add_payment(i[2], pay_in)
                self.logger.debug(f"Added payment of {i[2]} to exchange address {pay_in}")
            else:
                transaction.add_payment(i[2], i[1])
                self.logger.debug(f"Added direct payment of {i[2]} to {i[1]}")

        transaction.schnorr_sign(self.config.passphrase)
        sp = self.config.secondphrase
        if sp == 'None':
            sp = None
        if sp is not None:
            self.logger.debug("Applying second signature")
            transaction.second_sign(sp)
        transaction_dict = transaction.to_dict()
        self.logger.debug(f"Multi-payment transaction built with ID: {transaction_dict['id']}")
        return transaction_dict
    
    
    def broadcast_standard(self, tx):
        """
        Broadcast standard transfer transactions to the network
        
        Args:
            tx: List of transaction dictionaries
            
        Returns:
            List of accepted transaction IDs
        """
        self.logger.info(f"Broadcasting {len(tx)} standard transactions")
        # broadcast to relay
        try:
            transaction = self.client.transactions.create(tx)
            self.logger.debug(f"Broadcast response: {transaction}")
            print(transaction)
            records = [[j['recipientId'], j['amount'], j['id']] for j in tx]
            self.logger.info(f"Transactions created: {len(records)} records")
            time.sleep(1)
        except Exception as e:
            # error
            self.logger.error(f"Error broadcasting transactions: {str(e)}")
            print("Something went wrong", e)
            quit()

        self.sql.open_connection()
        self.sql.store_transactions(records)
        self.sql.close_connection()
        
        self.logger.info(f"Stored {len(records)} transaction records")
        return transaction['data']['accept']
    
    
    def broadcast_multi(self, tx):    
        """
        Broadcast multi-payment transactions to the network
        
        Args:
            tx: List of multi-payment transaction dictionaries
            
        Returns:
            List of accepted transaction IDs
        """
        self.logger.info(f"Broadcasting {len(tx)} multi-payment transactions")
        # broadcast to relay
        try:
            transaction = self.client.transactions.create(tx)
            self.logger.debug(f"Broadcast response: {transaction}")
            print(transaction)
            
            records = []
            for i in tx:
                id = i['id']
                self.logger.debug(f"Processing multi-payment transaction {id} with {len(i['asset']['payments'])} payments")
                tx_records = [[j['recipientId'], j['amount'], id] for j in i['asset']['payments']]
                records.extend(tx_records)
                
            self.logger.info(f"Multi-payment transactions created: {len(records)} total payment records")
            time.sleep(1)
        except Exception as e:
            # error
            self.logger.error(f"Error broadcasting multi-payment transactions: {str(e)}")
            print("Something went wrong", e)
            quit()
    
        self.sql.open_connection()
        self.sql.store_transactions(records)
        self.sql.close_connection()
        
        self.logger.info(f"Stored {len(records)} transaction records")
        return transaction['data']['accept']
