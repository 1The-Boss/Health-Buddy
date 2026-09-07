from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("API"))

def bot(query, prompt):
    response = client.chat.completions.create(
        model="groq/compound-mini",
        max_tokens=500,
        temperature=0.7,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content