import bittensor as bt
import argparse

parser = argparse.ArgumentParser()
bt.subtensor.add_args(parser)
config = bt.config(parser)
subtensor = bt.subtensor(config=config)

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
    # Wallet Hot Key
    wallet_hotkey = "ss58 address"
    subnet_id = 1
    print(get_rewards_per_day(wallet_hotkey, subnet_id))