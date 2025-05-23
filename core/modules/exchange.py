import json
import math
import requests
import time
import logging
from lowercase_booleans import false


class Exchange:
    def __init__(self, sql, config):
        """
        Initialize the Exchange module
        
        Args:
            sql: SQL connection for TBW data
            config: DelegateConfig instance for the specific delegate
        """
        self.config = config
        self.sql = sql
        
        # Set up logging
        self.logger = logging.getLogger(f'exchange_{config.username}')
        self.logger.info(f"Initializing Exchange module for delegate: {config.username}")

        
    def truncate(self, f, n):
        """Truncate a float to n decimal places"""
        return math.floor(f * 10 ** n) / 10 ** n
   

    def exchange_select(self, index, address, amount, provider):
        """
        Select and process the appropriate exchange provider
        
        Args:
            index: Index of the exchange configuration to use
            address: Address to exchange from
            amount: Amount to exchange
            provider: Exchange provider to use
            
        Returns:
            The payment address to use
        """
        self.logger.info(f"Processing exchange using provider: {provider}")
        self.logger.debug(f"Exchange details - index: {index}, address: {address}, amount: {amount}")
        
        if provider == "ChangeNow":
            pay = self.process_changenow_exchange(index, address, amount)
        elif provider == "SimpleSwap":
            pay = self.process_simpleswap_exchange(index, address, amount)
        elif provider == "StealthEx":
            pay = self.process_stealth_exchange(index, address, amount)
        else:
            self.logger.warning(f"Unknown exchange provider: {provider}, using original address")
            pay = address
            
        time.sleep(5)
        return pay
    
    def process_simpleswap_exchange(self, index, address, amount):
        """Process an exchange using SimpleSwap"""
        fixed = false
        self.logger.info("Processing SimpleSwap exchange")
        amount = self.truncate((amount / self.config.atomic), 4)
        self.logger.debug(f"Exchange amount: {amount}")
        
        url = 'https://t1mi6dwix2.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {
            "fixed": fixed,
            "currency_from": self.config.convert_from[index],
            "currency_to": self.config.convert_to[index],
            "address_to": self.config.address_to[index],
            "amount": str(amount),
            "user_refund_address": address
        }
        
        res_bytes = {}
        res_bytes['data'] = json.dumps(data_in).encode('utf-8')
        
        try:
            self.logger.debug(f"Sending request to SimpleSwap API: {url}")
            r = requests.get(url, params=res_bytes)
            
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                
                self.logger.info(f"SimpleSwap exchange successful - ID: {exchangeid}")
                self.logger.debug(f"Pay-in address: {payin_address}")
                
                self.sql.open_connection()
                self.sql.store_exchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                self.sql.close_connection()
                print("Exchange Success") 
            else:
                self.logger.warning(f"SimpleSwap exchange failed: {r.json()}")
                payin_address = address
                print("Exchange Fail")
        except Exception as e:
            self.logger.error(f"SimpleSwap exchange error: {str(e)}")
            payin_address = address
            print("Exchange Fail")
    
        print("Pay In Address", payin_address)
        return payin_address
    
    
    def process_changenow_exchange(self, index, address, amount):
        """Process an exchange using ChangeNow"""
        self.logger.info("Processing ChangeNow exchange")
        amount = self.truncate((amount / self.config.atomic), 4)
        self.logger.debug(f"Exchange amount: {amount}")
        
        url = 'https://mkcnus24ib.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {
            "fromCurrency": self.config.convert_from[index],
            "toCurrency": self.config.convert_to[index],
            "toNetwork": self.config.network_to[index],
            "address": self.config.address_to[index],
            "fromAmount": str(amount),
            "refundAddress": address
        }
        
        try:
            self.logger.debug(f"Sending request to ChangeNow API: {url}")
            r = requests.get(url, params=data_in)
            
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                
                self.logger.info(f"ChangeNow exchange successful - ID: {exchangeid}")
                self.logger.debug(f"Pay-in address: {payin_address}")
                
                self.sql.open_connection()
                self.sql.store_exchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                self.sql.close_connection()
                print("Exchange Success") 
            else:
                self.logger.warning(f"ChangeNow exchange failed: {r.json()}")
                payin_address = address
                print("Exchange Fail")
        except Exception as e:
            self.logger.error(f"ChangeNow exchange error: {str(e)}")
            payin_address = address
            print("Exchange Fail")
    
        return payin_address


    def process_stealth_exchange(self, index, address, amount):
        """Process an exchange using StealthEx"""
        self.logger.info("Processing StealthEx exchange")
        amount = self.truncate((amount / self.config.atomic), 4)
        self.logger.debug(f"Exchange amount: {amount}")
        
        url = 'https://4kb3mxdi2b.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {
            "currency_from": self.config.convert_from[index],
            "currency_to": self.config.convert_to[index],
            "address_to": self.config.address_to[index],
            "amount_from": str(amount),
            "refund_address": address
        }
        
        res_bytes = {}
        res_bytes['data'] = json.dumps(data_in).encode('utf-8')

        try:
            self.logger.debug(f"Sending request to StealthEx API: {url}")
            r = requests.get(url, params=res_bytes)
            
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                
                self.logger.info(f"StealthEx exchange successful - ID: {exchangeid}")
                self.logger.debug(f"Pay-in address: {payin_address}")
                
                self.sql.open_connection()
                self.sql.store_exchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                self.sql.close_connection()
                print("Exchange Success") 
            else:
                self.logger.warning(f"StealthEx exchange failed: {r.json()}")
                payin_address = address
                print("Exchange Fail")
        except Exception as e:
            self.logger.error(f"StealthEx exchange error: {str(e)}")
            payin_address = address
            print("Exchange Fail")
    
        print("Pay In Address", payin_address)
        return payin_address
