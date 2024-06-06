import json
import requests
from urllib.parse import quote
from django.conf import settings


def get_song_lyrics(artist, title):
    artist_query = quote(artist)
    title_query = quote(title)
    url = f"https://api.musixmatch.com/ws/1.1/matcher.lyrics.get?q_track={title_query}&q_artist={artist_query}&apikey={settings.MUSIXMATCH_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['message']['header']['status_code'] == 200:
        return data['message']['body']['lyrics']['lyrics_body']
    return None

def summarize_lyrics(lyrics):
    openai_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }

    # Define the prompt components
    task = "Create a dictionary containing two objects: 'summary' and 'countries'."
    context = ("You will be given song lyrics. The 'summary' should encapsulate the lyrics in one sentence, "
            "and 'countries' should list any countries mentioned in the lyrics.")
    exemplars = ("Example: Given the lyrics provided, the output should be: "
                '{"summary": "The lyrics describe the economic hardships and struggles faced by tradesmen, soldiers, and sailors in old England, with a hope for better times to come.", "countries": ["England"]}.')
    persona = "You are an expert in natural language processing and text summarization."
    format = "Return the output as a dictionary with the 'summary' and 'countries' keys."
    tone = "The tone should be concise and informative."

    # Combine all components into the prompt
    prompt = f"""
    Task: {task}

    Context: {context}

    Exemplars: {exemplars}

    Persona: {persona}

    Format: {format}

    Tone: {tone}
    """
    # Construct the data payload
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": prompt + "\nGiven the following lyrics, create a dictionary containing two objects: 'summary' and 'countries'."
            },
            {
                "role": "user",
                "content": lyrics
            }
        ]
    }

    # Make the API request
    response = requests.post(openai_url, headers=headers, json=data)
    content = None
    try:
        if response.status_code == 200:
            result = response.json()
            choices = result["choices"]
            for choice in choices:
                message = choice.get("message")
                if message and message.get("role") == "assistant":
                    content = message.get("content").replace("json",'').replace('python','').replace('```',"'").replace("\n",'')
                    print("Received content from OpenAI API:", content)
                    data=json.loads(content.strip())
                    break
        else:
            data = None
    except Exception as e:
        print("Error=====>>>>>>",e)
        print("content",content)
        data = None
    return data





