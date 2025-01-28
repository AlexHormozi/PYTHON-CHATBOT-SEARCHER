from flask import Flask, request, jsonify
import os
from groq import Groq
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('message')
    url = request.json.get('url')  # Assuming you pass the URL in the request
    
    # Fetch and parse HTML data
    soup = fetch_and_parse_html(url)
    if soup:
        paragraphs = soup.find_all('p')
        data = " ".join([p.text.strip() for p in paragraphs[:5]])  # Extract first few paragraphs
    else:
        data = "Failed to fetch data."
    
    # Generate response using Groq API
    response = generate_response(user_query, data)
    return jsonify({"response": response})

def generate_response(user_query, data):
    system_prompt = f"""
    You are a helpful assistant. Use this external information to answer questions:
    {data}
    """
    
    response = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        model="llama3-70b-8192"
    )
    
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True)
