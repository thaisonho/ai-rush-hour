import json
import glob
import os

def aggregate_results():
    """Aggregate all experiment JSON files into a single final_result.json"""
    # Get all experiment result files in the current directory
    files = glob.glob('experiment_results_*.json')
    
    # Combine all data from the files
    combined_data = []
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            combined_data.extend(data)
    
    # Write the combined data to final_result.json
    with open('final_result.json', 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)
    
    print(f"Successfully aggregated {len(files)} files into final_result.json")
    print(f"Total records: {len(combined_data)}")

if __name__ == '__main__':
    aggregate_results()
