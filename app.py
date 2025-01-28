from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import string

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the Groq API
groq_api_key = "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"
# groq = Groq(api_key=groq_api_key)  # Commented out for simplicity

# Dictionary to store user IDs and their respective URLs
user_ids = {}

# Function to generate a random user ID
def generate_user_id():
    return ''.join(random.choices(string.digits, k=15))

# Function to fetch and parse HTML from a URL
def fetch_and_parse_html(url):
    try:
        # Simulating requests.get for demonstration
        # response = requests.get(url)
        # response.raise_for_status()
        # soup = BeautifulSoup(response.text, 'html.parser')
        # return soup
        return None  # For simplicity, this function is not fully implemented
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@app.route('/create-user', methods=['POST'])
def create_user():
    user_id = generate_user_id()
    user_ids[user_id] = []  # Initialize with an empty list of URLs
    return jsonify({"user_id": user_id})

@app.route('/add-url', methods=['POST'])
def add_url():
    user_id = request.json.get('user_id')
    url = request.json.get('url')
    if user_id in user_ids:
        user_ids[user_id].append(url)
        return jsonify({"message": "URL added successfully"})
    else:
        return jsonify({"error": "User ID not found"}), 404

@app.route('/update-url', methods=['POST'])
def update_url():
    user_id = request.json.get('user_id')
    url_index = request.json.get('url_index')
    new_url = request.json.get('new_url')
    if user_id in user_ids and 0 <= url_index < len(user_ids[user_id]):
        user_ids[user_id][url_index] = new_url
        return jsonify({"message": "URL updated successfully"})
    else:
        return jsonify({"error": "Invalid user ID or URL index"}), 404

@app.route('/delete-url', methods=['POST'])
def delete_url():
    user_id = request.json.get('user_id')
    url_index = request.json.get('url_index')
    if user_id in user_ids and 0 <= url_index < len(user_ids[user_id]):
        del user_ids[user_id][url_index]
        return jsonify({"message": "URL deleted successfully"})
    else:
        return jsonify({"error": "Invalid user ID or URL index"}), 404

@app.route('/delete-user', methods=['POST'])
def delete_user():
    user_id = request.json.get('user_id')
    if user_id in user_ids:
        del user_ids[user_id]
        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"error": "User ID not found"}), 404

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json.get('user_id')
    user_query = request.json.get('message')
    url_index = request.json.get('url_index')
    theme = request.json.get('theme', 'default')  # Default to 'default' if no theme is provided

    if user_id not in user_ids:
        return jsonify({"error": "User ID not found"}), 404

    # Select the URL based on the index, fallback to the first URL if out of range
    url = user_ids[user_id][url_index] if url_index is not None and 0 <= url_index < len(user_ids[user_id]) else user_ids[user_id][0] if user_ids[user_id] else None

    if not url:
        return jsonify({"error": "No URLs available for this user"}), 404

    # Fetch and parse the HTML data from the selected URL
    soup = fetch_and_parse_html(url)
    data = "Failed to fetch data."
    if soup:
        # Simulating parsing logic for demonstration
        # paragraphs = soup.find_all('p')
        # data = " ".join([p.text.strip() for p in paragraphs[:5]])  # Extract the first 5 paragraphs
        pass

    # Generate a response using the Groq API (simplified for demonstration)
    response = f"User query: {user_query}. Data: {data}"

    # Generate the embed code based on the theme
    embed_code = f'<div id="chatbot" style="position: fixed; bottom: 10px; right: 10px; width: 300px; height: 400px;">'
    if theme == 'dark':
        embed_code += '<iframe src="/chatbot/dark" width="100%" height="100%" style="border: none; background-color: #121212; color: #FFFFFF;"></iframe>'
    else:
        embed_code += '<iframe src="/chatbot/light" width="100%" height="100%" style="border: none; background-color: #FFFFFF; color: #000000;"></iframe>'
    embed_code += '</div>'

    return jsonify({"response": response, "embed_code": embed_code})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
