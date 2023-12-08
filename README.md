# Useful scripts for setting up a new server for mining on Bittensor Subnet 18.

### How to use

1. Clone this repo in a fresh Ubuntu 22.04 instance. `git clone https://github.com/PhoenixBeaudry/bittensor_utils`
2. Change deploy script permissions to executable. `chmod u+x bittensor_utils/deploy.sh`
3. Run the deploy script. `./bittensor_utils/deploy.sh`
4. Log out of your instance and back in.
5. Create a new Bittensor cold wallet. `btcli wallet new_coldkey --wallet.name coldwallet`
6. Create a new Bittensor hot wallet. `btcli wallet new_hotkey --wallet.name coldwallet --wallet.hotkey hotwallet`
7. Ensure you have saved the mnemonics for both wallets.
8. Rename your example .env. `mv bittensor_utils/example.env bittensor_utils/.env`
9. Add your OpenAI API key and Bittensor cold wallet password to .env `nano bittensor_utils/.env`
10. Fund your Bittensor cold wallet with ~2 TAO.
11. Run the auto_register script to register to Subnet 18 and automatically start a miner. `python3 bittensor_utils/auto_register.py`
