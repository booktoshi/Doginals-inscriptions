import subprocess
import time
import json
import re
import os

def run_node_commands(start, end, directory, file_prefix, file_extension):
    for i in range(start, end + 1):
        # Construct the file name
        file_number = str(i).zfill(1)
        image_path = os.path.join(directory, f"{file_prefix}{file_number}.{file_extension}")

        # Check if file exists
        if not os.path.isfile(image_path):
            print(f"File not found: {image_path}")
            continue

        # Extract base file name without serial number
        base_file_name = os.path.basename(image_path).split('.')[0][:-5]

        # Construct and run the first command
        mint_command = f"node . mint {doge_address} {image_path}"
        result_mint = subprocess.run(mint_command, shell=True, capture_output=True, text=True)
        print("Output from mint command:")
        print(result_mint.stdout)

        # Check if there is an error in the first command
        if result_mint.stderr:
            print("Error in mint command:")
            print(result_mint.stderr)

        # Check for success message in the first command's output
        txid_search = re.search("inscription txid: (\w+)", result_mint.stdout)
        if txid_search:
            txid = txid_search.group(1)
            print("Successful mint, updating JSON file, continuing in 100 seconds....")
            update_json_file(base_file_name, image_path, txid)
            continue

        # Check for specific error message in the first command's output
        if "'64: too-long-mempool-chain'" in result_mint.stdout:
            print("Detected specific error message, proceeding to wallet sync in 100 seconds...")
            time.sleep(100)

            # Loop for the second command
            while True:
                wallet_sync_command = "node . wallet sync"
                result_sync = subprocess.run(wallet_sync_command, shell=True, capture_output=True, text=True)
                print("Output from wallet sync command:")
                print(result_sync.stdout)

                if result_sync.stderr:
                    print("Error in wallet sync command:")
                    print(result_sync.stderr)

                # Check for success message
                if "inscription txid" in result_sync.stdout:
                    print("Successful inscription, extracting txid and updating JSON file.")
                    txid_search = re.search("inscription txid: (\w+)", result_sync.stdout)
                    if txid_search:  # Ensure txid is found
                        txid = txid_search.group(1)
                        update_json_file(base_file_name, image_path, txid)
                        break
                    else:
                        print("TXID not found in wallet sync output")

                # Check for the specific error and retry
                elif "'64: too-long-mempool-chain'" in result_sync.stdout:
                    print("Detected specific error message, retrying in 100 seconds...")
                    time.sleep(100)
                else:
                    print("Unknown response, stopping the retry loop.")
                    break

def update_json_file(base_file_name, image_path, txid):
    json_file_name = f"{base_file_name}.json"
    data = {}
    if os.path.isfile(json_file_name):
        with open(json_file_name, 'r') as file:
            data = json.load(file)
    
    data[os.path.basename(image_path)] = txid

    with open(json_file_name, 'w') as file:
        json.dump(data, file, indent=4)

# Address to inscribe to.
doge_address = 'DESpUq549VHcZTc27cRfE3DNAMfiwyk4W4'
# Replace with directory to the collection.
directory = './images/' # Or your directory
# Replace with collection name. The file name without the serial number
file_prefix = ''
# Replace with file extension
file_extension = 'webp'
# Enter range of files to inscribe.
start = 2
end = 4

run_node_commands(start, end, directory, file_prefix, file_extension)
