import argparse
import bittensor as bt

##### Bittensor Code #####
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

def find_lowest_available_uid_below(lst, threshold):
    for i in range(len(lst) - 1):
        if lst[i] < threshold:
            return i
    return -1  # Return -1 if the condition is not met in any adjacent pair

if __name__ == "__main__":
    subnet_to_check = 18
    threshold = 120
    print(f"Checking Pruning Order for Subnet {subnet_to_check}")
    endangered_uids = get_endangered_uids(subnet_to_check)
    pruning_order = [item[0] for item in endangered_uids]
    print(f"The next 20 UIDs to be deregistered are: {endangered_uids[:20]}") 