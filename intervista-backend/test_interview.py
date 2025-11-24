import requests
import json

URL = "http://127.0.0.1:5000/api/interview"

payload = {
    "role": "Software Engineer",
    "question_context": "Backend systems, distributed computing",
    "last_question": "Tell me about a complex backend challenge you solved.",
    "user_answer": "I improved our caching layer and reduced latency by 40%.",
    "history": [],
    "turn_count": 1
}

print("\nSending request...\n")

resp = requests.post(URL, json=payload)

print("Status:", resp.status_code)
print("\nResponse JSON:\n")
try:
    print(json.dumps(resp.json(), indent=4))
except Exception:
    print(resp.text)
