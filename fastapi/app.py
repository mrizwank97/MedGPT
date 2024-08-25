import requests

from fastapi import FastAPI, Response

app = FastAPI()

@app.get('/')
def home():
    return {"hello" : "World"}

@app.get('/ask')
def ask(prompt :str):
    res = requests.post('http://ollama:11434/api/generate', json={
        "prompt": prompt,
        "stream" : False,
        "model" : "qwen2:0.5b",
        "options" : {
            "num_predict" : 25
        }
    })

    return Response(content=res.text, media_type="application/json")