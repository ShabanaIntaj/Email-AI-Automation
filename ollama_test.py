import json
import urllib.request


url = "http://localhost:11434/api/generate"

data = {
    "model": "gemma3:latest",
    "prompt": "Explain Artificial Intelligence in simple Hinglish in 3-4 lines.",
    "stream": False
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request, timeout=120) as response:
    result = json.loads(
        response.read().decode("utf-8")
    )

print("\nGemma Response:\n")
print(result["response"])