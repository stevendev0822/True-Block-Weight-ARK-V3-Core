# True-Block-Weight-ARK-V3-Core

A robust and configurable True Block Weight (TBW) calculation and payment distribution system for ARK Core v3 and compatible blockchains.

## Overview

This tool allows delegates to automatically calculate and distribute rewards to voters based on their voting weight, with extensive configuration options for customization. **A key feature is support for multiple delegates within a single LXC server**, making it ideal for delegate teams or individuals managing multiple delegates.

## Key Features

- **Multi-delegate support**: Run and manage multiple delegates from a single installation
- Customizable voter reward sharing
- Flexible payment schedules
- Blacklist/whitelist functionality
- Optional cryptocurrency exchange integration
- Detailed logging for each delegate

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- pm2 (Process manager for Node.js)

### Installing pm2

```bash
npm install pm2@latest -g
```

Or if you use Yarn:

```bash
yarn global add pm2
```

## Installation

Follow these steps to set up the True-Block-Weight system:

```bash
# Clone the repository
git clone https://github.com/stevendev0822/True-Block-Weight-ARK-V3-Core.git

# Navigate to the project directory
cd True-Block-Weight-ARK-V3-Core

# Create and activate a virtual environment
python -m venv .venv
.venv/scripts/activate  # On Windows
# source .venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Edit delegates.json with your configuration
```

## Multi-Delegate Setup

One of the most powerful features of this tool is the ability to manage multiple delegates from a single installation. This is especially useful for:

- Delegate teams sharing infrastructure
- Individual delegates running multiple delegates across different networks
- Backup delegates management

To configure multiple delegates:
1. Edit the `delegates.json` file to include configurations for each delegate
2. Each delegate can have its own unique sharing settings, payment schedules, and voter rules
3. Run commands with the `--all` flag to process all delegates, or specify individual delegates with `--delegate <name>`

## Usage

### Running Manually

Navigate to the core directory and run the scripts:

```bash
cd core
```

For TBW calculations:
```bash
# Calculate rewards for all delegates
python tbw.py --all

# Calculate rewards for a specific delegate
python tbw.py --delegate <delegate_name>
```

For payments:
```bash
# Process payments for all delegates
python pay.py --all

# Process payments for a specific delegate
python pay.py --delegate <delegate_name>
```

### Running with PM2

For continuous operation, use pm2:

```bash
pm2 start apps.json
```

## Configuration

After cloning the repository, create and modify the configuration file at `core/config/delegates.json`. The file uses a JSON structure with an array of delegate configurations.

### Configuration Structure

The `delegates.json` file contains an array of delegate objects, each with the following structure:

```json
{
    "delegates": [
        {
            "name": "delegate1",
            "static": {
                "atomic": 100000000,
                "network": "ark_devnet",
                "start_block": 0
            },
            "delegate": {
                "message": "Thank you for voting delegate1",
                "voter_share": 90,
                "voter_cap": 0,
                "voter_min": 0,
                "whitelist": false,
                "whitelist_address": [],
                "blacklist": false,
                "blacklist_address": []
            },
            "payment": {
                "interval": 211,
                "multi": true,
                "passphrase": "passphrase1",
                "secondphrase": null,
                "delegate_fee": [10],
                "delegate_fee_address": ["addr1"]
            },
            "exchange": {
                "exchange": false,
                "convert_from": ["ark", "ark"],
                "convert_address": ["addr1", "addr2"],
                "convert_to": ["usdc", "xrp"],
                "address_to": ["usdc_addr1", "xrp_addr2"],
                "network_to": ["eth", "xrp"],
                "provider": ["provider", "provider"]
            },
            "other": {
                "custom": false,
                "manual_pay": false,
                "update_share": false
            },
            "donate": {
                "donate": false,
                "donate_address": "addr1",
                "donate_percent": 0
            }
        },
        // Additional delegate configurations follow the same structure
    ]
}
```

### Configuration Sections

Each delegate configuration contains the following sections:

#### Static
Network and blockchain settings:
- `atomic`: The atomic unit value (default: 100000000)
- `network`: Network identifier (e.g., "ark_devnet", "ark_mainnet")
- `start_block`: Block height to start calculations from

#### Delegate
Delegate information and voter sharing rules:
- `message`: Message to include in vendor field for payments
- `voter_share`: Percentage to share with voters
- `voter_cap`: Maximum voting weight to consider for rewards (0 = no cap)
- `voter_min`: Minimum wallet balance required for reward eligibility
- `whitelist`: Enable/disable whitelist mode (boolean)
- `whitelist_address`: Array of whitelisted addresses
- `blacklist`: Enable/disable blacklist mode (boolean)
- `blacklist_address`: Array of blacklisted addresses

#### Payment
Payment intervals and distribution details:
- `interval`: Payment interval in blocks
- `multi`: Use multipayments (boolean)
- `passphrase`: Delegate passphrase
- `secondphrase`: Second passphrase (if enabled)
- `delegate_fee`: Array of percentages for delegate to keep
- `delegate_fee_address`: Array of addresses for delegate fee distribution

#### Exchange (Experimental - ARK network only)
Cryptocurrency exchange settings:
- `exchange`: Enable/disable exchange functionality (boolean)
- `convert_from`: Array of source networks for swap
- `convert_address`: Array of source addresses for swap
- `convert_to`: Array of target cryptocurrencies
- `address_to`: Array of target addresses
- `network_to`: Array of target networks
- `provider`: Array of swap providers ("SimpleSwap" or "ChangeNow")

**Notes:**
- Exchange functionality does not work with fixed amount/address processing
- Swaps are processed through affiliate accounts at SimpleSwap/ChangeNow
- Use `test_exchange.py` to test your exchange configuration

#### Other
Custom settings and manual operations:
- `custom`: Enable/disable custom share rates for individual voters (boolean)
- `manual_pay`: Enable/disable manual payment runs outside normal intervals (boolean)
- `update_share`: Enable/disable updating voter share rates in database (boolean)

**Note:** Reset these options to `false` after using them

#### Donate
Optional donation settings:
- `donate`: Enable/disable donations (boolean)
- `donate_address`: Donation address
- `donate_percent`: Donation percentage (from reserve account)

## Logging

Logs are stored in the `logs` directory with filenames based on delegate names. Each delegate has its own log file for easy tracking and troubleshooting.

## LXC Server Optimization

When running multiple delegates on a single LXC server, consider:

- Allocating sufficient resources to the LXC container
- Monitoring database performance
- Setting appropriate payment intervals to distribute server load
- Using pm2 for process management and automatic restarts

## Changelog

### 1.0.1
- Added devfund implementation
- Implemented v3 (bip340) transaction signing as default
- Enhanced multi-delegate support

### 0.1
- Initial release

## Future Development

- Additional features and improvements planned
- Enhanced multi-delegate management tools

## Security

If you discover a security vulnerability, please open an issue. All security vulnerabilities will be promptly addressed.

## License

[MIT](LICENSE) © [stevendev0822](https://github.com/stevendev0822)
