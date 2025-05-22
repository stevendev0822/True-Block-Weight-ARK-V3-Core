import logging
from utility.delegate_manager import DelegateManager

class DelegateConfig:
    def __init__(self, delegate_name):
        # Set up logging
        self.logger = logging.getLogger(f'delegate_config_{delegate_name}')
        self.logger.info(f"Initializing configuration for delegate: {delegate_name}")
        
        # Initialize the delegate manager
        self.delegate_manager = DelegateManager(None)
        
        # Get the specific delegate configuration
        self.logger.debug(f"Retrieving configuration for delegate: {delegate_name}")
        delegate_config = self.delegate_manager.get_delegate_config(delegate_name)
        
        if not delegate_config:
            error_msg = f"Delegate '{delegate_name}' not found in configuration"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Load static settings
        self.logger.debug("Loading static settings")
        atomic_settings = delegate_config.get('static', {})
        self.atomic = atomic_settings.get('atomic', 0)
        self.network = atomic_settings.get('network', 'mainnet')
        self.username = delegate_name
        self.start_block = atomic_settings.get('start_block', 0)
        self.logger.debug(f"Static settings: atomic={self.atomic}, network={self.network}, start_block={self.start_block}")
        
        # Load delegate settings
        self.logger.debug("Loading delegate settings")
        delegate_settings = delegate_config.get('delegate', {})
        self.delegate = delegate_name
        self.message = delegate_settings.get('message', '')
        self.voter_share = delegate_settings.get('voter_share', 0)
        self.voter_cap = delegate_settings.get('voter_cap', 0)
        self.voter_min = delegate_settings.get('voter_min', 0)
        self.whitelist = delegate_settings.get('whitelist', False)
        self.whitelist_address = delegate_settings.get('whitelist_address', [])
        self.blacklist = delegate_settings.get('blacklist', False)
        self.blacklist_address = delegate_settings.get('blacklist_address', [])
        self.logger.debug(f"Delegate settings: voter_share={self.voter_share}, voter_cap={self.voter_cap}, voter_min={self.voter_min}")
        
        # Load payment settings
        self.logger.debug("Loading payment settings")
        payment_settings = delegate_config.get('payment', {})
        self.interval = payment_settings.get('interval', 0)
        self.multi = payment_settings.get('multi', False)
        self.passphrase = payment_settings.get('passphrase', '')
        self.secondphrase = payment_settings.get('secondphrase', None)
        self.delegate_fee = payment_settings.get('delegate_fee', [])
        self.delegate_fee_address = payment_settings.get('delegate_fee_address', [])
        self.logger.debug(f"Payment settings: interval={self.interval}, multi={self.multi}")
        
        # Load exchange settings
        self.logger.debug("Loading exchange settings")
        exchange_settings = delegate_config.get('exchange', {})
        self.exchange = exchange_settings.get('exchange', False)
        self.convert_from = exchange_settings.get('convert_from', [])
        self.convert_address = exchange_settings.get('convert_address', [])
        self.convert_to = exchange_settings.get('convert_to', [])
        self.address_to = exchange_settings.get('address_to', [])
        self.network_to = exchange_settings.get('network_to', [])
        self.provider = exchange_settings.get('provider', [])
        self.logger.debug(f"Exchange settings: exchange={self.exchange}")
        
        # Load donation settings
        self.logger.debug("Loading donation settings")
        donate_settings = delegate_config.get('donate', {})
        self.donate = "Y" if donate_settings.get('donate', False) else "N"
        self.donate_address = donate_settings.get('donate_address', '')
        self.donate_percent = donate_settings.get('donate_percent', 0)
        self.logger.debug(f"Donation settings: donate={self.donate}, donate_percent={self.donate_percent}")
        
        # Load other settings
        self.logger.debug("Loading other settings")
        other_settings = delegate_config.get('other', {})
        self.custom = "Y" if other_settings.get('custom', False) else "N"
        self.manual_pay = "Y" if other_settings.get('manual_pay', False) else "N"
        self.update_share = "Y" if other_settings.get('update_share', False) else "N"
        self.logger.debug(f"Other settings: custom={self.custom}, manual_pay={self.manual_pay}, update_share={self.update_share}")
        
        self.logger.info(f"Successfully initialized configuration for delegate: {delegate_name}")
