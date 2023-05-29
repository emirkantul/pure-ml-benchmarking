import os
import json
from transformers import GPT2TokenizerFast
from prompter import make_prompt


def calculate_average_token_size(directory):
    # Initialize the tokenizer
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

    total_token_size = 0
    num_files = 0

    # Process each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)

            # Load the extracted paper
            with open(file_path, "r") as json_file:
                paper_data = json.load(json_file)

            title = paper_data["title"]
            content = paper_data["content"]

            # Create the prompt using make_prompt function
            prompt = make_prompt(title, content)

            tokenized_prompt = tokenizer.encode(prompt)
            token_size = len(tokenized_prompt)
            total_token_size += token_size

            num_files += 1

    # Calculate the average token size
    average_token_size = total_token_size / num_files
    gpt35 = total_token_size / 1000 * 0.002
    gpt4 = total_token_size / 1000 * 0.003

    print(f"Average token size: {average_token_size:.3f}")
    print(f"Total token size: {total_token_size:.3f}")
    print(f"Number of files: {num_files}")
    print(f"Total cost with gpt-3.5: ${gpt35*1.2:.3f} - ${gpt35*1.5:.3f}")
    print(
        "Average cost with gpt-3.5:"
        f" ${gpt35 / num_files*1.2:.3f} - ${gpt35 / num_files*1.5:.3f}"
    )
    print(f"Total cost with gpt-4: ${gpt4*1.5:.3f} - ${gpt4*2:.3f}")
    print(
        "Average cost with gpt-4:"
        f" ${gpt4 / num_files*1.5:.3f} - ${gpt4 / num_files*2:.3f}"
    )


# Example usage
calculate_average_token_size("json/extracted-papers/")
