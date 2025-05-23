from utility.utility import Utility
import logging

class Voters():
    def __init__(self, config, sql):
        """
        Initialize the Voters module
        
        Args:
            config: DelegateConfig instance for the specific delegate
            sql: SQL connection for TBW data
        """
        self.config = config
        self.sql = sql
        
        # Set up logging
        self.logger = logging.getLogger(f'voters_{config.username}')
        self.logger.info(f"Initializing Voters module for delegate: {config.username}")

    def process_whitelist(self, voter_balances):
        """
        Process whitelist - only include voters in the whitelist
        
        Args:
            voter_balances: Dictionary of voter addresses and their balances
            
        Returns:
            Dictionary of whitelisted voter addresses and their balances
        """
        self.logger.debug(f"Processing whitelist with {len(voter_balances)} voters")
        adjusted_voters = {}
        
        if not self.config.whitelist:
            self.logger.debug("Whitelist not enabled, returning original balances")
            return voter_balances
            
        for k, v in voter_balances.items():
            if k in self.config.whitelist_address:
                adjusted_voters[k] = v
                self.logger.debug(f"Voter {k} is in whitelist, keeping balance {v}")
            else:
                self.logger.debug(f"Voter {k} is not in whitelist, removing")
        
        self.logger.info(f"Whitelist processing complete: {len(adjusted_voters)} voters remain")
        return adjusted_voters

    
    def process_blacklist(self, voter_balances):
        """
        Process blacklist - exclude voters in the blacklist
        
        Args:
            voter_balances: Dictionary of voter addresses and their balances
            
        Returns:
            Dictionary of non-blacklisted voter addresses and their balances
        """
        self.logger.debug(f"Processing blacklist with {len(voter_balances)} voters")
        adjusted_voters = {}
        
        if not self.config.blacklist:
            self.logger.debug("Blacklist not enabled, returning original balances")
            return voter_balances
            
        for k, v in voter_balances.items():
            if k not in self.config.blacklist_address:
                adjusted_voters[k] = v
                self.logger.debug(f"Voter {k} is not in blacklist, keeping balance {v}")
            else:
                self.logger.debug(f"Voter {k} is in blacklist, removing")
        
        self.logger.info(f"Blacklist processing complete: {len(adjusted_voters)} voters remain")
        return adjusted_voters
    
    
    def process_voter_cap(self, voter_balances):
        """
        Apply voter cap - limit maximum vote weight
        
        Args:
            voter_balances: Dictionary of voter addresses and their balances
            
        Returns:
            Dictionary of voter addresses with capped balances
        """
        self.logger.debug(f"Processing voter cap with {len(voter_balances)} voters")
        adjusted_voters = {}
        
        # no voter cap
        if self.config.voter_cap == 0:
            self.logger.debug("No voter cap set, returning original balances")
            adjusted_voters = voter_balances
        else:
            # get max cap
            max_votes = int(self.config.voter_cap * self.config.atomic)
            self.logger.debug(f"Applying voter cap of {self.config.voter_cap} tokens ({max_votes} atomic units)")
            
            for k, v in voter_balances.items():
                if v > max_votes:
                    adjusted_voters[k] = max_votes
                    self.logger.debug(f"Voter {k} balance {v} exceeds cap, capping at {max_votes}")
                else:
                    adjusted_voters[k] = v
                    self.logger.debug(f"Voter {k} balance {v} is under cap, keeping as is")
        
        self.logger.info(f"Voter cap processing complete for {len(adjusted_voters)} voters")
        return adjusted_voters
    
    
    def process_voter_min(self, voter_balances):
        """
        Apply voter minimum - exclude votes below minimum threshold
        
        Args:
            voter_balances: Dictionary of voter addresses and their balances
            
        Returns:
            Dictionary of voter addresses with balances above minimum
        """
        self.logger.debug(f"Processing voter minimum with {len(voter_balances)} voters")
        adjusted_voters = {}
        
        # no minimum
        if self.config.voter_min == 0:
            self.logger.debug("No voter minimum set, returning original balances")
            adjusted_voters = voter_balances
        else:
            # get min threshold
            min_votes = int(self.config.voter_min * self.config.atomic)
            self.logger.debug(f"Applying voter minimum of {self.config.voter_min} tokens ({min_votes} atomic units)")
            
            for k, v in voter_balances.items():
                if v > min_votes:
                    adjusted_voters[k] = v
                    self.logger.debug(f"Voter {k} balance {v} exceeds minimum, keeping as is")
                else:
                    adjusted_voters[k] = 0
                    self.logger.debug(f"Voter {k} balance {v} is below minimum, setting to 0")
        
        self.logger.info(f"Voter minimum processing complete for {len(adjusted_voters)} voters")
        return adjusted_voters
    
    
    def process_anti_dilution(self, voter_balances):
        """
        Apply anti-dilution - include unpaid balances in vote weight
        
        Args:
            voter_balances: Dictionary of voter addresses and their balances
            
        Returns:
            Dictionary of voter addresses with anti-dilution applied
        """
        self.logger.debug(f"Processing anti-dilution with {len(voter_balances)} voters")
        adjusted_voters = {}
        
        self.sql.open_connection()
        dilute = self.sql.all_voters().fetchall()
        self.sql.close_connection()
        
        unpaid = {i[0]:i[2] for i in dilute}
        self.logger.debug(f"Retrieved unpaid balances for {len(unpaid)} voters")
        
        for k, v in voter_balances.items():
            adjusted_voters[k] = (v + unpaid[k])
            self.logger.debug(f"Voter {k}: original balance {v}, unpaid {unpaid[k]}, adjusted {adjusted_voters[k]}")
        
        self.logger.info(f"Anti-dilution processing complete for {len(adjusted_voters)} voters")
        return adjusted_voters
