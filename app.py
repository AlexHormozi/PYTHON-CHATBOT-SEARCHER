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

# Store multiple URLs in a list
urls = [
    "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiqt7zXvpiLAxX1UkEAHbmbO6QQFnoECDUQAQ&url=https%3A%2F%2Fwww.sciencedirect.com%2Ftopics%2Fmedicine-and-dentistry%2Fcraniectomy&usg=AOvVaw13-keP-_5lnHfjDle4puzC&opi=89978449",
    "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiqt7zXvpiLAxX1UkEAHbmbO6QQFnoECDcQAQ&url=https%3A%2F%2Fwww.mdanderson.org%2Fcancerwise%2Fcraniotomy-vs--craniectomy--what-is-the-difference.h00-159702279.html&usg=AOvVaw2EjtHz4jQKjsRy2kdsvTcN&opi=89978449",
    "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiqt7zXvpiLAxX1UkEAHbmbO6QQFnoECDkQAQ&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FDecompressive_craniectomy&usg=AOvVaw0fQzyYtQi5AyMW5WFZrQO0&opi=89978449"
]

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('message')
    url_index = request.json.get('url_index')  # Index of the URL to use
    
    # Select the URL based on the index
    if url_index is not None and url_index < len(urls):
        url = urls[url_index]
    else:
        url = urls[0]  # Default to the first URL if no index is provided
    
    # Fetch and parse HTML data
    soup = fetch_and_parse_html(url)
    if soup:
        paragraphs = soup.find_all('p')
        data = " ".join([p.text.strip() for p in paragraphs[:5]])  # Extract first few paragraphs
    else:
        data = "Failed to fetch data."
    
    # Generate response using Groq API with a sales-oriented approach
    response = generate_response(user_query, data)
    return jsonify({"response": response})

def generate_response(user_query, data):
    system_prompt = f"""
    You are a sales assistant. Use this external information to answer questions and lead the customer towards a sale:
    {data}
    """
    
    # Generate response
    response = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        model="llama3-70b-8192",
        max_tokens=100  # Adjust this based on your desired response length
    )
    
    # Extract response content
    content = response.choices[0].message.content
    
    # Trim response if it's too long
    words = content.split()
    if len(words) > 50:
        content = ' '.join(words[:50]) + '...'
    
    # Add a call-to-action if the user is interested in purchasing
    if "buy" in user_query.lower() or "purchase" in user_query.lower():
        content += " Would you like to proceed with the purchase? Please let me know how I can assist you further."
    
    return content

if __name__ == '__main__':
    app.run(debug=True)


