from fastapi import FastAPI,HTTPException,Query
# FastAPI imports for building the web application, handling request HTTP exceptions, and parsing query parameters.
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import os
import json

app = FastAPI()

# Frontend static files
app.mount("/static", StaticFiles(directory="static"),name="static")

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral" # Using Mistral 7B for summarization.

@app.get("/")
def serve_homepage():
  """ Serve the index.html file when accessing the root URL. """
  return FileResponse(os.path.join("static","index.html"))

@app.post("/summarize")
def summarize_text(text: str = Form(...)):
  headers = {"Content-Type":"application/json"}
  """ Handle chat requests by sending the prompt to the Ollama API and returning the response. """
  try:
    # Send the input text to the Ollama for summarization
    response = requests.post(
      OLLAMA_URL,
      json={"model": MODEL_NAME, "prompt": f"Summarize this : {text}", "stream": False}
      headers=headers
    )

    # Log the response for debugging
    print("Ollama API Response Raw", response)
    print("Ollama API Response:", response.text)

    # Ensure valid JSON response
    response_data = response.text.strip()
    try:
      # Parse the JSON response
      json_response = json.loads(response_data)
      print("Parsed JSON Response:", json_response)
    except json.JSONDecodeError:
      raise HTTPException(status_code=500, detail="Invalid JSON response from Ollama API")

    # Extract AI-generated response
    ai_response = json_response.get("response")
    if not ai_response:
      raise HTTPException(status_code=500, detail="No response from Ollama API")

    return {"response": ai_response}
  except requests.RequestException as e:
    # Handle request exceptions
    raise HTTPException(status_code=500, detail=f"Error communicating with Ollama API: {str(e)}")


"""Run the Server"""
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app,host="0.0.0.0",port=8000,reload=True)
