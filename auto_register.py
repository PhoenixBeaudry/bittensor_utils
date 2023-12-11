import argparse
import os
import subprocess
import time
import json
import bittensor as bt
from dotenv import load_dotenv
load_dotenv()

##### Bittensor Code #####

# Gets all the relevant Bittensor information on a specific wallet and subnet
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


# Checks the registration status of a wallet on the subnet in its config.
def check_wallet_registration_status(wallet_config):
    axons = wallet_config['metagraph'].axons
    for axon in axons:
        if axon.hotkey == wallet_config['wallet'].get_hotkey().ss58_address:
            return True

    return False


# Gets the UID of the wallet on it's subnet
def get_wallet_uid(wallet_config):
    metagraph = wallet_config['metagraph']
    axons = metagraph.axons
    uid = 0
    for axon in axons:
        if axon.hotkey == wallet_config['wallet'].get_hotkey().ss58_address:
            return uid
        uid += 1
    return None


# Returns a list of UIDs about to be deregistered on a subnet
def get_endangered_uids(subnet_id):
    parser = argparse.ArgumentParser()
    bt.subtensor.add_args(parser)
    config = bt.config(parser)
    subtensor = bt.subtensor(config=config)
    subnet_immunity_period = subtensor.immunity_period(subnet_id)
    current_block = subtensor.get_current_block()
    
    # Go through UIDs in subnet
    subnet_neurons = subtensor.neurons(subnet_id)
    pruning_scores = []
    id = 0
    for neuron in subnet_neurons:
        print(f"Checking UID {id}/255")
        id += 1
        # Get registration block of neuron
        uid_registration_block = subtensor.query_subtensor("BlockAtRegistration", params=[subnet_id, neuron.uid]).value
        # Check if in immunity
        if(current_block-uid_registration_block > subnet_immunity_period):
            pruning_scores.append((neuron.uid, neuron.pruning_score))
    return sorted(pruning_scores, key=lambda x: x[1])


# Returns the amount of TAO a miner is making per block
def get_rewards_per_block(wallet_config):
    metagraph = wallet_config['metagraph']
    subnet_tao_per_day = get_subnet_weight(wallet_config['subnet_id'])*7200
    incentives = metagraph.incentive.tolist()
    wallet_uid = get_wallet_uid(wallet_config)
    wallet_incentive = incentives[wallet_uid]
    return wallet_incentive*subnet_tao_per_day*0.41 # 41% goes to miners


# Returns the current percent emissions of the given subnet.
def get_subnet_weight(subnet_id):
    parser = argparse.ArgumentParser()
    bt.subtensor.add_args(parser)
    config = bt.config(parser)
    subtensor = bt.subtensor(config=config)
    return float(subtensor.get_emission_value_by_subnet(netuid=subnet_id))


# Attempts to register a given wallet on the subnet in its config.
def register_wallet(wallet_config):
    subtensor = wallet_config['subtensor']
    # Check register cost
    register_cost = subtensor.burn(wallet_config['subnet_id']).tao
    if(register_cost < 2.0):
        # Registration cost is okay, attempt to register.
        registration_attempt = subtensor.burned_register(wallet=wallet_config['wallet'], netuid=wallet_config['subnet_id'], wait_for_finalization=True)
        if(registration_attempt):
            # Registration succeeded
            return True
        else:
            # Registration failed
            print("Too Busy.")
            return False
    else:
        print(f"Too expensive: {register_cost}")
        return False


##### Miner Code #####

# Gets a miners running status. Returns True is a miner is running, False if it isnt, or None if there is an error.
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


# Checks if a miner is running and if it isn't starts one.
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
    start_command = f"pm2 start {sn18_repo_path}/miner/miner.py --name miner-{wallet['id']} --interpreter python3 -- --netuid {subnet_id} --subtensor.network local --wallet.name {wallet['wallet_name']} --wallet.hotkey {wallet['wallet_hotkey']} --axon.port {wallet['port']} --logging.debug"
    start_miner_attempt = subprocess.call(start_command, shell=True, env=env)
    if start_miner_attempt == 0:
        print("Miner started successfully.")


##### Main Function #####

###### Important Input ######
# Open the JSON file and load its content into a Python object
with open('wallets.json', 'r') as file:
    wallets = json.load(file)

subnet_id = 18 # Hard coded subnet 18
sn18_repo_path = "~/cortex.t"

uid_snipe = True
uid_snipe_threshold = 70
register_tries_before_refresh = 3

# Make sure you have OPENAI_API_KEY and BT_COLD_PW_WALLETNAME in a .env file.
if __name__ == "__main__":
    while True:
        # If trying to get low UIDs, check availability
        low_uid_available = False
        endangered_uids = get_endangered_uids(subnet_id)
        # Wait for low UID probability to be worth it.
        if(endangered_uids[0][0] < uid_snipe_threshold and endangered_uids[1][0] < uid_snipe_threshold):
            low_uid_available = True

        for wallet in wallets:
            wallet_config = get_wallet_config(wallet['wallet_name'], wallet['wallet_hotkey'], subnet_id)

            # Check if registered on subnet
            is_registered = check_wallet_registration_status(wallet_config) 

            # If wallet not registered attempt registration.
            if(not is_registered and low_uid_available):
                print(f"Wallet: {wallet['id']} is not registered and low UID is available.")

                for i in range(register_tries_before_refresh):
                    # Try register
                    print(f"Attempting register Wallet {wallet['id']}... ")
                    register_result = register_wallet(wallet_config)

                    # Registration succeeded, start a miner
                    if (register_result == True):
                        print(f"Wallet: {wallet['id']} has been registered. Starting miner...")
                        time.sleep(1)
                        start_miner(wallet)
                        break
                    else:
                        print("Registration Failed.")

            else:
                print(f"Wallet {wallet['id']} already registered. Checking miner....")
                time.sleep(1)
                start_miner(wallet)

        # Wait 20s before retrying
        time.sleep(1)