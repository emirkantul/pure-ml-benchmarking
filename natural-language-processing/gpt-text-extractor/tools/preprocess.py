import os
import re
import json
import multiprocessing


def replace_non_latin_characters(file_path):
    # Load the JSON file
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    # Replace non-Latin character groups with a single whitespace character
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = re.sub(r"[^\x00-\x7F]+", " ", value)

    # Save the modified data back to the JSON file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def process_json_files(directory, num_processes=4):
    # Get the list of JSON files in the directory
    json_files = [
        filename
        for filename in os.listdir(directory)
        if filename.endswith(".json")
    ]

    # Determine the number of processes to use
    num_processes = min(num_processes, len(json_files))

    # Create and start the process pool
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(
            replace_non_latin_characters,
            [os.path.join(directory, filename) for filename in json_files],
        )


if __name__ == "__main__":
    # Usage
    process_json_files("./json/extracted-papers/", num_processes=8)
