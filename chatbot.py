import requests
from config import HF_API_KEY

API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def detect_mood(user_input):
    # Enhanced mood detection based on keywords and sentiment analysis
    sad_keywords = ["sad", "depressed", "unhappy", "miserable", "lonely"]
    happy_keywords = ["happy", "joy", "excited", "cheerful", "great"]
    anxious_keywords = ["anxious", "nervous", "stressed", "worried", "scared"]
    
    if any(word in user_input.lower() for word in sad_keywords):
        return "sad"
    elif any(word in user_input.lower() for word in happy_keywords):
        return "happy"
    elif any(word in user_input.lower() for word in anxious_keywords):
        return "anxious"
    else:
        return "neutral"

def get_response(user_input, mood):
    try:
        payload = {"inputs": user_input}
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        
        # Check if the response is valid
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "Sorry, I couldn't understand that.")
            # Modify response based on mood
            if mood == "sad":
                return f"I'm sorry to hear that you're feeling this way. {generated_text}"
            elif mood == "happy":
                return f"That's great to hear! {generated_text}"
            elif mood == "anxious":
                return f"It sounds like you're feeling anxious. {generated_text}"
            else:
                return generated_text
        else:
            return "Sorry, I couldn't understand that."
    
    except requests.exceptions.RequestException as e:
        print(f"Hugging Face API error: {e}")
        return "Sorry, the chatbot is currently unavailable."