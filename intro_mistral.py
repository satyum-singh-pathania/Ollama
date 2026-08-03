import requests

BASE_URL = "http://localhost:11434"

response = requests.post(
  BASE_URL + "/api/generate",
  json={"model":"mistral","prompt":"What is AI?","stream":False}
)

print(response.json()["response"])
