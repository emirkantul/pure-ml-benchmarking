import openai
import os
from dotenv import load_dotenv
import time
import json


# Load environment variables from .env file
load_dotenv()

# Set the API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not set")

openai.api_key = openai_api_key


MODEL_NAME = "gpt-3.5-turbo"


def handle_rate_limit(func):
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < 3:
            try:
                return func(*args, **kwargs)
            except openai.error.RateLimitError:
                wait_time = (attempts + 1) * 5
                print(f"RateLimit error. Waiting for {wait_time} seconds.")
                time.sleep(wait_time)
                attempts += 1
        print("Exceeded rate limit retry attempts. Exiting.")
        return None

    return wrapper


def make_prompt(title, content):
    return "".join(
        (
            (
                f"Given Title: {title}\nGiven Abstract and Introduction:"
                f" {content}\nFill the information for PA device and given"
                " paper. If not found write None. NO OTHER ANSWER ONLY"
                " FILL:\n\n"
            ),
            "Publication:\n",
            "Year:\n",
            "Month:\n",
            "Last Name (1st Author):\n",
            "Paper Title:\n",
            "Process (CMOS_Bulk, CMOS_SOI, SiGe):\n",
            "CW Performance:\n",
            "Frequency (GHz):\n",
            "Psat (dBm):\n",
            "PAEmax (%):\n",
            "P1dB (dBm):\n",
            "PAE_1dB (%):\n",
            "Gain (dB):\n",
            "RF PA Modulations:\n",
            "EVM (dB):\n",
            "Modulation Speed (Msym/s):\n",
            "Average Pout (dBm):\n",
            "Average PAE (%):\n",
            "RF PA Note (Modulation Type):\n",
            "RF PA Note (Analog PA or Digital PA):\n",
            "Process node:\n",
            "PCB:\n",
            "Sub2G-Psar:\n",
            "Sub2G-PAE:\n",
            "2-6GHz-Psat:\n",
            "2-6GHz-PAE:\n",
            "6-20GHz-Psat:\n",
            "6-20GHz-PAE:\n",
            "20-50GHz-Psat:\n",
            "20-50GHz-PAE:\n",
            ">50GHz-Psat:\n",
            ">50GHz-PAE:\n",
            "PAE (%):\n",
            "<10%:\n",
            "10-20%:\n",
            "20-30%:\n",
            ">30%:\n",
            "CMOS from 2018:\n",
            "64QAM Power:\n",
            "6QAM Efficiency:\n",
            "64QAM Power 20-50:\n",
            "64QAM Efficiency 20-50:\n",
            "64QAM Efficiency >50:\n",
            "Since 2018 64QAM Power 20-50:\n",
            "Since 2018 64QAM Efficiency 20-50:\n",
            "Chip_area:\n",
            "Core_area:\n",
            "Gain/core_area:\n",
            "Psat/core_area:\n",
            "Gain/chip_area:\n",
            "Psat/chip_area:\n",
            "Psat_W:\n",
        )
    )


@handle_rate_limit
def get_results_from_chat_gpt(title, content):
    prompt = "".join(make_prompt(title, content))

    print(f"PROMPT: {prompt}\n")

    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        temperature=0.1,
        n=1,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Power Amplifier expert who is trying to fill"
                    " the needed information for a given paper."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    result = response["choices"][0]["message"]["content"]
    print(f"RESPONSE: {result}\n")

    # Split the response into separate parts for each attribute
    attributes = result.split("\n")
    attributes_dict = {}
    for attribute in attributes:
        if ": " in attribute:
            key, val = attribute.split(":", 1)
            attributes_dict[key.strip()] = val.strip()
    return attributes_dict

    return result


def write_results_to_json(directory, output_file):
    # Initialize the dictionary to store the results
    all_results = {}

    # Get the existing results, if any
    if os.path.exists(output_file):
        with open(output_file, "r") as json_existing:
            all_results = json.load(json_existing)

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)

            # Check if the results for this file already exist
            file_name = os.path.splitext(filename)[0]
            if file_name in all_results:
                continue

            # Read the contents of the file
            with open(file_path, "r") as json_file:
                data = json.load(json_file)

            # Apply the get_results_from_chat_gpt function
            results = get_results_from_chat_gpt(data["title"], data["content"])

            # Add the results to the dictionary
            all_results[file_name] = results

    # Save all the results to the output file
    with open(output_file, "w") as json_output:
        json.dump(all_results, json_output, indent=4)

    print(f"All extracted papers' results saved to {output_file}")


# Usage
directory = "./json/extracted-papers/"
output_file = "./json/all_extracted_papers.json"
write_results_to_json(directory, output_file)
