from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the Groq API
groq_api_key = "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"
groq = Groq(api_key=groq_api_key)

# List of URLs
urls = [
    "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiqt7zXvpiLAxX1UkEAHbmbO6QQFnoECDUQAQ&url=https%3A%2F%2Fwww.sciencedirect.com%2Ftopics%2Fmedicine-and-dentistry%2Fcraniectomy&usg=AOvVaw13-keP-_5lnHfjDle4puzC&opi=89978449",
    # Add more URLs as needed
]

# Function to fetch and parse HTML from a URL
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
    # Extract JSON data from the request
    user_query = request.json.get('message')
    url_index = request.json.get('url_index')
    theme = request.json.get('theme', 'default')  # Default to 'default' if no theme is provided

    # Select the URL based on the index, fallback to the first URL if out of range
    url = urls[url_index] if url_index is not None and 0 <= url_index < len(urls) else urls[0]

    # Fetch and parse the HTML data from the selected URL
    soup = fetch_and_parse_html(url)
    data = "Failed to fetch data."
    if soup:
        paragraphs = soup.find_all('p')
        data = " ".join([p.text.strip() for p in paragraphs[:5]])  # Extract the first 5 paragraphs

    # Generate a response using the Groq API
    response = generate_response(user_query, data)

    # Generate the embed code based on the theme
    embed_code = generate_embed_code(theme)

    return jsonify({"response": response, "embed_code": embed_code})

def generate_response(user_query, data):
    # Create the system prompt for the assistant
    system_prompt = f"""
    You are a sales assistant. Use this external information to answer questions and lead the customer towards a sale:
    {data}
    """
    
    # Generate the chat response using the Groq API
    response = groq.chat.completions.create(
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
        model="llama3-70b-8192",
        max_tokens=100
    )
    
    content = response.choices[0].message.content
    if "buy" in user_query.lower() or "purchase" in user_query.lower():
        content += " Would you like to proceed with the purchase? Please let me know how I can assist you further."
    
    return content

def generate_embed_code(theme):
    # Generate the embed code dynamically based on the theme
    base_embed = f'<div id="chatbot" style="position: fixed; bottom: 10px; right: 10px; width: 300px; height: 400px;">'
    if theme == 'dark':
        base_embed += '<iframe src="/chatbot/dark" width="100%" height="100%" style="border: none; background-color: #121212; color: #FFFFFF;"></iframe>'
    else:
        base_embed += '<iframe src="/chatbot/light" width="100%" height="100%" style="border: none; background-color: #FFFFFF; color: #000000;"></iframe>'
    base_embed += '</div>'
    return base_embed

# New route to serve embed code dynamically
@app.route('/chatbot/<theme>', methods=['GET'])
def chatbot(theme):
    # Return an HTML page with the chatbot iframe embedded
    theme = theme.lower()
    if theme not in ['dark', 'light']:
        theme = 'light'  # Default to light theme if invalid
    
    return f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: {'#121212' if theme == 'dark' else '#FFFFFF'};
                color: {'#FFFFFF' if theme == 'dark' else '#000000'};
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
        </style>
    </head>
    <body>
        <iframe src="/chat" width="100%" height="100%"></iframe>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
