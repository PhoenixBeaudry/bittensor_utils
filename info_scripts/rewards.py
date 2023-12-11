import bittensor as bt
import argparse
import json

parser = argparse.ArgumentParser()
bt.subtensor.add_args(parser)
config = bt.config(parser)
subtensor = bt.subtensor(config=config)

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

# Returns the current percent emissions of the given subnet.
def get_subnet_weight(subnet_id):
    return float(subtensor.get_emission_value_by_subnet(netuid=subnet_id))

# Returns the wallet's uid if it is registered on subnet, None if it isn't
def get_wallet_uid(hotkey, subnet_id):
    metagraph = subtensor.metagraph(subnet_id)
    axons = metagraph.axons
    uid = 0
    for axon in axons:
        if axon.hotkey == hotkey:
            return uid
        uid += 1
    print("Wallet is not registered on this subnet.")

    return None

# Returns the amount of TAO a hotkey is making per day
def get_rewards_per_day(hotkey, subnet_id):
    metagraph = subtensor.metagraph(subnet_id)
    subnet_tao_per_day = get_subnet_weight(subnet_id)*7200
    incentives = metagraph.incentive.tolist()
    wallet_uid = get_wallet_uid(hotkey, subnet_id)
    wallet_incentive = incentives[wallet_uid]
    return wallet_incentive*subnet_tao_per_day*0.41 # 41% goes to miners


if __name__ == "__main__":
    # Open the JSON file and load its content into a Python object
    # Define the path to your JSON file, expanding the tilde to the home directory
    json_file_path = os.path.expanduser('~/bittensor_utils/wallets.json')
    with open(json_file_path, 'r') as file:
        wallets = json.load(file)

    subnet_id = 18

    total_tao = 0

    for wallet in wallets:
        wallet_config = get_wallet_config(wallet['wallet_name'], wallet['wallet_hotkey'], subnet_id)
        # Wallet Hot Key
        wallet_hotkey = wallet_config['wallet'].get_hotkey().ss58_address
        wallet_reward = get_rewards_per_day(wallet_hotkey, subnet_id)
        print(f"Rewards for wallet {wallet['id']}: {wallet_reward}")
        total_tao += wallet_reward

    print(f"Total Daily Rewards: {total_tao}")