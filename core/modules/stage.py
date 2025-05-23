import logging

class Stage:
    def __init__(self, config, dynamic, sql, voters, delegate):
        """
        Initialize the Stage module and process payments
        
        Args:
            config: DelegateConfig instance for the specific delegate
            dynamic: Dynamic fee calculator
            sql: SQL connection for TBW data
            voters: Dictionary of voter addresses and payment amounts
            delegate: Dictionary of delegate addresses and payment amounts
        """
        self.config = config
        self.dynamic = dynamic
        self.sql = sql
        self.voters = voters
        self.delegate = delegate
        
        # Set up logging
        self.logger = logging.getLogger(f'stage_{config.username}')
        self.logger.info(f"Initializing Stage module for delegate: {config.username}")
        
        # get transactions
        fees = self.get_transaction_fees()
        
        # stage delegate payments
        self.stage_delegate_payments(fees)
        
        # stage voter payments
        self.stage_voter_payments()
        
        
    def get_transaction_fees(self):
        """
        Calculate transaction fees for all payments
        
        Returns:
            Total transaction fees
        """
        delegate_tx = len([v for v in self.delegate.values() if v >= 0])
        voter_tx = len([v for v in self.voters.values() if v > 0])
        total_tx = voter_tx + delegate_tx
        
        self.logger.info(f"Calculating fees for {total_tx} total transactions ({delegate_tx} delegate, {voter_tx} voter)")
        print("Total Transactions: ", total_tx)
        
        # check if multipayments
        if self.config.multi == "Y":
            multi_limit = self.dynamic.get_multipay_limit()
            self.logger.debug(f"Using multi-payment with limit of {multi_limit} payments per transaction")

            if total_tx % multi_limit == 0:
                numtx = round(total_tx / multi_limit)
            else:
                numtx = round(total_tx // multi_limit) + 1

            full_payments = total_tx // multi_limit
            full = int(full_payments * self.dynamic.get_dynamic_fee_multi(multi_limit))
            partial_payments = total_tx % multi_limit
            partial = self.dynamic.get_dynamic_fee_multi(partial_payments)
            transaction_fees = full + partial
            
            self.logger.debug(f"Multi-payment fees: {full} for {full_payments} full transactions, {partial} for partial transaction with {partial_payments} payments")
            
        else:
            self.logger.debug("Using standard payments")
            transaction_fees = int(total_tx * self.dynamic.get_dynamic_fee())
            
        self.logger.info(f"Total transaction fees: {transaction_fees}")
        return transaction_fees
        
    
    def stage_delegate_payments(self, f):
        """
        Stage delegate payments
        
        Args:
            f: Transaction fees to deduct from reserve
        """
        self.logger.info("Staging delegate payments")
        paid_delegate = {}
        count = 1
        
        for k, v in self.delegate.items():
            # this is the reserve account
            if count == 1:
                # reserve account insuffient to pay fees
                if (v - f) <= 0:
                    error_msg = "Not enough to cover transaction fees in reserve"
                    self.logger.error(f"{error_msg} - needed {f}, have {v}")
                    print(error_msg)
                    print("Update interval and restart")
                    quit()
                # process donation
                elif self.config.donate == "Y":
                    paid_donation = {}
                    donate_amt = int((self.config.donate_percent / 100) * v)
                    reserve_amt = v - donate_amt
                    paid_donation[self.config.donate_address] = donate_amt
                    
                    self.logger.info(f"Processing donation: {donate_amt} to {self.config.donate_address} ({self.config.donate_percent}% of {v})")
                    
                    # update staging table with donation line
                    self.sql.open_connection()
                    self.sql.stage_payment(paid_donation, msg = "Donation")
                    self.sql.close_connection()
                    
                    # subtract out single tx fee because of extra donation tx
                    pay_amount = reserve_amt - self.dynamic.get_dynamic_fee()
                    self.logger.debug(f"Reserve amount after donation and fee: {pay_amount}")
                else:
                    pay_amount = v - f
                    self.logger.debug(f"Reserve amount after fees: {pay_amount}")
            else:
                pay_amount = v
                self.logger.debug(f"Delegate payment to {k}: {pay_amount}")
                
            count += 1
            paid_delegate[k] = pay_amount
            
        self.logger.info(f"Delegate payments prepared: {len(paid_delegate)} payments")
        print("Delegate Payments\n", paid_delegate)
        
        self.sql.open_connection()
        self.sql.update_delegate_paid_balance(paid_delegate)
        self.sql.stage_payment(paid_delegate, msg = "Reward")
        self.sql.close_connection()
        
        self.logger.info("Delegate payments staged successfully")
    
    
    def stage_voter_payments(self):
        """Stage voter payments"""
        self.logger.info(f"Staging voter payments for {len(self.voters)} voters")
        print("Voter Payments\n", self.voters)
        
        # Filter out zero payments
        non_zero_voters = {k: v for k, v in self.voters.items() if v > 0}
        self.logger.debug(f"Staging {len(non_zero_voters)} non-zero voter payments")
        
        self.sql.open_connection()
        self.sql.update_voter_paid_balance(self.voters)
        self.sql.stage_payment(non_zero_voters, msg = self.config.message)
        self.sql.close_connection()
        
        self.logger.info("Voter payments staged successfully")
