import sys
import os
import subprocess
from together import Together

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py '<customcontent>'")
        sys.exit(1)

    robotID = sys.argv[1]

    with open('controllers/'+ str(robotID) + '_prompt.txt', 'r') as file:
        customcontent = file.read()

    # Initialize Together client
    client = Together(api_key="7777f6e34f04364aa9a5db2e82c57064f262d6416523d029b725ee16cfd11030")

    # Create a chat completion
    response = client.chat.completions.create(
        model="mistralai/Mixtral-8x22B-Instruct-v0.1", #### Very very good - best results so far
        #model="mistralai/Mistral-7B-Instruct-v0.1",
        messages=[{"role": "user", "content": customcontent}],
    )

    # Get the response content
    response_content = response.choices[0].message.content

    print(response_content)

if __name__ == "__main__":
    main()