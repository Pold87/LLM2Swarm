import sys
import os
import subprocess
from openai import OpenAI

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py '<usercontent>'")
        sys.exit(1)

    robotID = sys.argv[1]

    with open('controllers/human_concrete_instruct.txt', 'r') as file:
        usercontent = file.read()

    with open('controllers/system_human_instruct.txt', 'r') as file:
        systemcontent = file.read()

        
    # Initialize Together client
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.35,
        messages=[
            {"role": "system", "content": systemcontent},
            {"role": "user", "content": usercontent}
        ]
    )
    
    # Get the response content
    response_content = response.choices[0].message.content

    print(response_content)

if __name__ == "__main__":
    main()
