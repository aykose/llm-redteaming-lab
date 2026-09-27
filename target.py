import requests

def send_prompt(prompt, model="llama3.2:3b") -> str:
    payload = {
            "model" : model,
            "prompt" : prompt,
            "stream" : False
    }

    reponse = requests.post("http://localhost:11434/api/generate", json=payload)

    return reponse.json()["response"]




