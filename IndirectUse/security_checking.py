from openai import OpenAI

import os
from os.path import expanduser

client = OpenAI()

home = expanduser("~")
ARGOSPATH=os.path.join(home, "software/LLM2Swarm/DirectUse/")
default_filepath = os.path.join(ARGOSPATH, "controllers/movement_generated.py")


# Function to interact with the OpenAI model for security checking
def check_security(controller_code):
    prompt = f"""
    The following is a synthesized controller code. Your task is to check the code for potential security issues or malicious parts.
    - Specifically, identify any vulnerabilities based on the Common Weakness Enumeration (CWE).
    - If possible, indicate if there are risks such as sabotaging other logic.
    - Provide remediation steps for the identified issues.

    Controller Code:
    {controller_code}

    Now, check the code and list any issues you can find.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a security expert with deep knowledge of software vulnerabilities."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']



if __name__ == "__main__":

    with open(default_filepath, 'r') as file:
        
        controller_code = file.read()
        # Perform security checking
        security_report = check_security(controller_code)
        
        print("Security Analysis Report:")
        print(security_report)
