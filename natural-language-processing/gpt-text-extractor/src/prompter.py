import openai
import os
from dotenv import load_dotenv
import time


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


@handle_rate_limit
def get_performance_issues(code):
    prompt = (
        "Given performance issues:\n\nComputational Expensive"
        " Operation\nInefficient Data Structures\nNot Using Function"
        " Inlining\nInefficient Concurrency Control\nMissing SIMD"
        " Parallelism\nMissing GPU Parallelism\nMissing Task"
        " Parallelism\n\nDetect and classify performance-related bugs in"
        " given C++ code - which can be sequential, OpenMP-based (CPU"
        " parallel) or CUDA-based (GPU Parallel).Only use the classes that"
        " are given and ONLY USE THE FORMAT BELOW\nComputational Expensive"
        f" Operation: {{ YOUR ANSWER }}\n...\n\ngiven code:\n{code}"
    )
    print(f"PROMPT: {prompt}")

    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        temperature=0.1,
        n=1,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a HPC expert who can analyze parallel and"
                    " sequential code and classify performance bugs."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    result = response["choices"][0]["message"]["content"]
    print(f"RESPONSE: {result}")

    # Split the response into separate parts for each issue
    issues = result.split("\n")
    issues_dict = {}
    for issue in issues:
        if ": " in issue:
            key, val = issue.split(": ", 1)
            issues_dict[key] = val
    return issues_dict

    return result
