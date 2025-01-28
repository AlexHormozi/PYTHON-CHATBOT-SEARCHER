from flask import Flask, request, jsonify
import os
from groq import Groq
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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

urls = [
    "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiqt7zXvpiLAxX1UkEAHbmbO6QQFnoECDUQAQ&url=https%3A%2F%2Fwww.sciencedirect.com%2Ftopics%2Fmedicine-and-dentistry%2Fcraniectomy&usg=AOvVaw13-keP-_5lnHfjDle4puzC&opi=89978449",
    # Add more URLs as needed
]

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('message')
    url_index = request.json.get('url_index')  
    theme = request.json.get('theme', 'default')  # Capture theme from user input
    
    # Select the URL based on the index
    url = urls[url_index] if url_index is not None and url_index < len(urls) else urls[0]
    
    # Fetch and parse HTML data
    soup = fetch_and_parse_html(url)
    data = "Failed to fetch data."
    if soup:
        paragraphs = soup.find_all('p')
        data = " ".join([p.text.strip() for p in paragraphs[:5]])
    
    # Generate response using Groq API
    response = generate_response(user_query, data)
    
    # Generate Embed Code with the provided theme
    embed_code = generate_embed_code(theme)
    
    return jsonify({"response": response, "embed_code": embed_code})

def generate_response(user_query, data):
    system_prompt = f"""
    You are a sales assistant. Use this external information to answer questions and lead the customer towards a sale:
    {data}
    """
    
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
    # Customize the embed code based on the theme
    base_embed = f'<div id="chatbot" style="position: fixed; bottom: 10px; right: 10px; width: 300px; height: 400px;">'
    if theme == 'dark':
        base_embed += '<iframe src="https://yourchatbotlink.com/dark-theme" width="100%" height="100%" style="border: none;"></iframe>'
    else:
        base_embed += '<iframe src="https://yourchatbotlink.com/light-theme" width="100%" height="100%" style="border: none;"></iframe>'
    base_embed += '</div>'
    return base_embed

if __name__ == '__main__':
    app.run(debug=True)
