# True-Block-Weight-ARK-V3-Core

A robust and configurable True Block Weight (TBW) calculation and payment distribution system for ARK Core v3 and compatible blockchains.

## Overview

This tool allows delegates to automatically calculate and distribute rewards to voters based on their voting weight, with extensive configuration options for customization. **A key feature is support for multiple delegates within a single LXC server**, making it ideal for project owners managing multiple delegates.

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

# Configure your delegate settings
cp core/config/delegates.example.json core/config/delegates.json
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

After cloning the repository, create and modify the configuration file at `core/config/delegates.json`. The main sections to configure are:

- `[static]` - Network and database settings
- `[delegate]` - Delegate information and voter sharing rules
- `[payment]` - Payment intervals and distribution details
- `[exchange]` - (Optional) Cryptocurrency exchange settings
- `[other]` - Custom settings and manual operations
- `[donate]` - Optional donation settings

### Available Configuration Options

#### [Static]
| Option | Default | Description | 
| :--- | :---: | :--- |
| atomic | 100000000 | Atomic value - do not change |
| network | ark_devnet | Network identifier (ark_mainnet, persona_mainnet, qredit_mainnet, etc.) |
| username | username | PostgreSQL database username (usually your OS username) |
| start_block | 0 | Block height to start calculations from |

#### [Delegate]
| Option | Default | Description | 
| :--- | :---: | :--- |
| delegate | delegate | Your delegate name |
| message | message | Message to include in vendor field for payments (ARK and forks only) |
| voter_share | 90 | Percentage to share with voters |
| vote_cap | 0 | Maximum voting weight to consider for rewards (0 = no cap) |
| vote_min | 0 | Minimum wallet balance required for reward eligibility |
| whitelist | N | Enable whitelist mode (Y/N) |
| whitelist_addr | addr1,addr2,addr3 | Comma-separated list of whitelisted addresses |
| blacklist | N | Enable blacklist mode (Y/N) |
| blacklist_addr | addr1,addr2,addr3 | Comma-separated list of blacklisted addresses |

#### [Payment]
| Option | Default | Description | 
| :--- | :---: | :--- |
| interval | 211 | Payment interval in blocks |
| multi | N | Use multipayments (Y/N) |
| passphrase | passphrase | Delegate passphrase |
| secondphrase | None | Second passphrase (if enabled) |
| delegate_fee | 10 | Percentage for delegate to keep (first entry is reserve account) |
| delegate_fee_address | addr1 | Addresses for delegate fee distribution |

#### [Exchange] (Experimental - ARK network only)
| Option | Default | Description | 
| :--- | :---: | :--- |
| exchange | N | Enable exchange functionality (Y/N) |
| convert_from | ark, ark | Source network for swap |
| convert_address | addr1,addr2 | Source addresses for swap |
| convert_to | usdc,xrp | Target cryptocurrencies |
| address_to | usdc_addr1,xrp_addr2 | Target addresses |
| network_to | eth,xrp | Target networks |
| provider | provider,provider | Swap providers ("SimpleSwap" or "ChangeNow") |

**Notes:**
- Exchange functionality does not work with fixed amount/address processing
- Swaps are processed through affiliate accounts at SimpleSwap/ChangeNow
- Use `test_exchange.py` to test your exchange configuration

#### [Other]
| Option | Default | Description | 
| :--- | :---: | :--- |
| custom | N | Enable custom share rates for individual voters |
| manual_pay | N | Enable manual payment runs outside normal intervals |
| update_share | N | Enable updating voter share rates in database |

**Note:** Reset these options to "N" after using them

#### [Donate]
| Option | Default | Description | 
| :--- | :---: | :--- |
| donate | N | Enable donations (Y/N) |
| donate_address | addr1 | Donation address |
| donate_percent | 0 | Donation percentage (from reserve account) |

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

[MIT](LICENSE) © [stevendev0822](https://github.com/stevendev0822/True-Block-Weight-ARK-V3-Core)
