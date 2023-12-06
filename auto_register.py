import argparse
import os
import subprocess
import time
import json
import bittensor as bt

##### Bittensor Code #####

def get_wallet_config(wallet_name, wallet_hotkey, subnet_id):
    parser = argparse.ArgumentParser()
    bt.subtensor.add_args(parser)
    bt.logging.add_args(parser)
    bt.wallet.add_args(parser)
    config = bt.config(parser)
    config.wallet.name = wallet_name
    config.wallet.hotkey = wallet_hotkey
    wallet = bt.wallet(config=config)
    subtensor = bt.subtensor(config=config)
    metagraph = subtensor.metagraph(subnet_id)
    wallet_config ={
        'wallet': wallet,
        'subnet_id': subnet_id,
        'subtensor': subtensor,
        'metagraph': metagraph
    }

    return wallet_config


def check_wallet_registration_status(wallet_config):
    axons = wallet_config['metagraph'].axons

    registered_hotkeys = []
    for axon in axons:
        registered_hotkeys.append(axon.hotkey)

    if wallet_config['wallet'].get_hotkey().ss58_address not in registered_hotkeys:
        return False
    else:
        return True


def register_wallet(wallet_config):
    subtensor = wallet_config['subtensor']
    # Check register cost
    register_cost = subtensor.burn(wallet_config['subnet_id'])
    if(register_cost < 3.0):
        # Registration cost is okay, attempt to register.
        registration_attempt = subtensor.burned_register(wallet=wallet_config['wallet'], netuid=wallet_config['subnet_id'], wait_for_finalization=True)

        if(registration_attempt):
            # Registration succeeded
            return True
        else:
            # Registration failed
            return False


##### Miner Code #####

def get_miner_status(miner_name):
    # Get the list of all pm2 processes in JSON format
    result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to get the list of processes from pm2")
        return None

    # Parse the JSON output
    try:
        processes = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse JSON output from pm2")
        return None

    # Check if the miner process is in the list
    for proc in processes:
        if proc['name'] == miner_name:
            return True
    return False


def start_miner(wallet):
    # Check if miner already running
    status = get_miner_status("miner-" + wallet['id'])
    if(status):
        print("Miner is already running.")
        return
    
    elif(status is None):
        print("Error getting pm2 info.")
        return
    
    # Start Miner
    env = os.environ.copy()
    start_command = f"pm2 start ~/bittensor/sn18/miner/miner.py --name miner-{wallet['id']} --interpreter python3 -- --netuid 18 --subtensor.network local --subtensor.chain_endpoint localhost:9944 --wallet.name {wallet['wallet_name']} --wallet.hotkey {wallet['wallet_hotkey']} --axon.port {wallet['port']} --logging.debug"
    start_miner_attempt = subprocess.call(start_command, shell=True, env=env)
    if start_miner_attempt == 0:
        print("Miner started successfully.")



##### Main Function #####

if __name__ == "__main__":
    # Wallet structure: {wallet_name: "cold", wallet_hotkey: "hot", id: "1", port: "8091"}
    wallets = [
        {'wallet_name': 'sn18cold', 'wallet_hotkey': 'sn18hot', 'id': "1", 'port': '8098'},
        {'wallet_name': 'sn18cold', 'wallet_hotkey': 'sn18hot2', 'id': "2", 'port': '8099'}
    ]

    # For each wallet check if registered
    while True:
        for wallet in wallets:
            wallet_config = get_wallet_config(wallet['wallet_name'], wallet['wallet_hotkey'], 18) # Hard coded subnet 18

            # Check if registered on subnet
            is_registered = check_wallet_registration_status(wallet_config) 

            # If wallet not registered, try register
            if (not is_registered):
                print(f"Wallet: {wallet['id']} is not registered.")
                print(f"Attempting register Wallet {wallet['id']}... ")
                # Try register
                register_result = register_wallet(wallet_config)

                # Registration succeeded, start a miner
                if (register_result == True):
                    print(f"Wallet: {wallet['id']} has been registered. Starting miner...")
                    start_miner(wallet)
                else:
                    print("Registration Failed.")
            else:
                print(f"Wallet {wallet['id']} already registered. Checking miner....")
                start_miner(wallet)

        # Wait 20s before retrying
        time.sleep(20)


