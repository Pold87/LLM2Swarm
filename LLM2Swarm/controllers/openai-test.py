from openai import OpenAI
import sys

with open('input.txt', 'r') as file:
  customcontent = file.read()

  client = OpenAI()

  completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "user", "content": customcontent}
    ]
  )

  print(completion.choices[0].message.content)
