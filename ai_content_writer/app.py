from fastapi import FastAPI, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import os
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

@app.get("/")
def serve_homepage():
  return FileResponse(os.path.join("static","index.html"))

@app.post("/generate")
def generate_content(topic:str = Form(...),style:str=Form(...)):
  headers = {"Content-Type":"application/json"}
  try:
    # Send this input prompt to the llama3 model
    prompt = f"Write a detailed article about '{topic} in a {style} style."
    response = requests.post(
      OLLAMA_URL,
      headers=headers,
      json={"model":MODEL_NAME,"prompt":prompt,"stream":False}
    )

    # Print Response
    print("Ollama Response:", response.text)

    # Ensure valid JSON response
    response_data = response.text.strip()
    try:
      json_response = json.loads(response_data)
    except json.JSONDecodeError:
      raise HTTPException(status_code=500, detail="Invalid JSON response from Ollama API")

  except requests.exceptions.RequestException as e:
    raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")

# Run the server with uvicorn
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0",reload=True,port=8000)
