import os
import re
import json
import pdfplumber
import multiprocessing

output_directory = "./json/extracted-papers/"
directory = "../../paper-dataset/"


# Function to process a single PDF file
def process_pdf_file(filename):
    if filename.endswith(".pdf"):
        file_path = os.path.join(directory, filename)
        output_filename = (
            re.sub(r"_", " ", os.path.splitext(filename)[0]) + ".json"
        )
        output_path = os.path.join(output_directory, output_filename)

        # Skip if file already exists
        if os.path.exists(output_path):
            print(f"Skipped {filename} as {output_filename} already exists.")
            return

        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0]
            content = first_page.extract_text()

            # Create the JSON data
            data = {
                "title": os.path.splitext(filename)[0].replace("_", " "),
                "content": content.replace("\n", " "),
            }

            # Save the JSON data to file
            with open(output_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

        print(
            f"Extracted content from {filename} and saved as {output_filename}"
        )


def read_pdf_files_and_save_as_json(num_processes=4):
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Get the list of PDF files in the directory
    pdf_files = [
        filename
        for filename in os.listdir(directory)
        if filename.endswith(".pdf")
    ]

    # Determine the number of processes to use
    num_processes = min(num_processes, len(pdf_files))

    # Create and start the process pool
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(process_pdf_file, pdf_files)


if __name__ == "__main__":
    # Usage
    read_pdf_files_and_save_as_json(num_processes=16)
