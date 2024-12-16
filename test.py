import openai
from openai import OpenAI

client = OpenAI(api_key="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")


try:
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello, GPT-4!"}
    ])
    print("GPT-4 is accessible!")
except openai.InvalidRequestError as e:
    print(f"Error: {e}")
    print("Trying gpt-3.5-turbo instead...")
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello, GPT-3.5!"}
    ])
    print("GPT-3.5-turbo is accessible!")