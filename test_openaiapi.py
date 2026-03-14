from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Say hello"
)

print(response.output[0].content[0].text)