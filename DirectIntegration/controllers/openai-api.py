import sys
import os
import subprocess
from openai import OpenAI

def main():
    if len(sys.argv) != 3:
        print("Usage: python openai-api.py <systemcontentpath> <usercontentpath>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as file:
        systemcontent = file.read()

    with open(sys.argv[2], 'r') as file:
        usercontent = file.read()

    # Initialize Together client
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.55,
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
