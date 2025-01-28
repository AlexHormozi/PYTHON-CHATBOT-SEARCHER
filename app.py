pip install transformers streamlit requests

from groq import Groq


import requests
from bs4 import BeautifulSoup
import os
from groq import Groq

# Initialize Groq client with your API key
groq_api_key = "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"
groq = Groq(api_key=groq_api_key)

def fetch_and_parse_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Example usage
url = "https://my.clevelandclinic.org/health/treatments/24902-craniotomy"
soup = fetch_and_parse_html(url)

if soup:
    # Extract relevant sections (e.g., paragraphs)
    paragraphs = soup.find_all('p')
    relevant_data = " ".join([p.text.strip() for p in paragraphs[:5]])  # Extract first few paragraphs

    # Prepare a prompt for Groq API
    system_prompt = f"""
    You are a helpful assistant. Use this external information to answer questions:
    {relevant_data}
    """

    # Generate response using Groq API
    def generate_response(user_query):
        response = groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            model="llama3-70b-8192"
        )
        return response.choices[0].message.content

    # Example usage
    user_query = "What is a craniotomy?"
    response = generate_response(user_query)
    print("Chatbot Response:", response)
else:
    print("Failed to fetch data.")
