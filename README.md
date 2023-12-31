# THIS GUIDE IS NOW OUT OF DATE | DO NOT USE

# Useful scripts for setting up a new server for mining on Bittensor Subnet 18.

## Testing
These scripts have been tested on fresh AWS EC2 Ubuntu 22.04 t2.xlarge Instances with 500GB of storage.

### Prerequisites
- A fresh Ubuntu 22.04 install. Local or Cloud.
- An OpenAI API Key that can handle $160 dollars of running cost a day.
- A WandB API Key (Get one here: https://wandb.ai/)
- Ports 8098, 9933 and 30333 portforwarded.

### How to use

1. Clone this repo in a fresh Ubuntu 22.04 instance. `git clone https://github.com/PhoenixBeaudry/bittensor_utils`
2. Change deploy script permissions to executable. `chmod u+x bittensor_utils/deploy.sh`
3. Run the deploy script. `./bittensor_utils/deploy.sh`
4. Log out of your instance and back in.
5. Create a new Bittensor cold wallet. `btcli wallet new_coldkey --wallet.name coldwallet`
6. Create a new Bittensor hot wallet. `btcli wallet new_hotkey --wallet.name coldwallet --wallet.hotkey hotwallet`
7. Ensure you have saved the mnemonics for both wallets and the password for the cold wallet.
8. Rename your example wallets.json. `mv bittensor_utils/example.wallets.json bittensor_utils/wallets.json`
9. Rename your example .env. `mv bittensor_utils/example.env bittensor_utils/.env`
10. Add your OpenAI API key and Bittensor cold wallet password to .env `nano bittensor_utils/.env`
11. Fund your Bittensor cold wallet with ~2 TAO. (View wallet address with `btcli wallet list`)
12. Check your funds have arrived. `btcli wallet balance`
13. Login to WandB. `wandb login` And then paste in your API key. 
14. Run the auto_register script to register to Subnet 18 and automatically start a miner. `python3 bittensor_utils/auto_register.py`
15. ?????
16. Profit.

### Monitoring your miner
Once your miner has been started by running auto_register.py. You can stop the script with CTRL-C.

Then to ensure your miner is working correctly you can view it's logs with `pm2 logs miner-1`.

Watch the logs and ensure that your miner is receiving IsAlive requests: `|      DEBUG       | accepting IsAlive request from 5F4...Ac3`.

You will start receiving rewards once your miner receives Stream or Image requests: `|      DEBUG       | axon     | <-- | 984 B | StreamPrompting |`.

This can take a varying amount of time up to hours.

Finally to ensure you are receiving rewards use the command: `btcli wallet overview --wallet.name coldwallet`.

If your miner is receiving rewards on the network it will have a non-zero number in 'incentive' and 'emission'.

To check your estimated daily rewards enter your hotkey found with `btcli wallet list` in to `https://taostats.io`.


### Useful Commands

- Check whether your miner is running: `pm2 status`
- Check the logs of your miner: `pm2 logs miner-1`
- Start your miner `pm2 start miner-1`
- Stop your miner: `pm2 stop miner-1`


Happy mining :)
