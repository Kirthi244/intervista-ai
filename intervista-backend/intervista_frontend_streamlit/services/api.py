import requests

BACKEND_URL = "http://127.0.0.1:8000/api/interview"

def post_interview(payload: dict) -> dict:
    """
    Post to backend and always return a dict.
    Handles backend returning string or JSON.
    """
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=15)
        resp.raise_for_status()
        try:
            data = resp.json()
            return data if isinstance(data, dict) else {"interviewer_reply": str(data)}
        except ValueError:
            return {"interviewer_reply": resp.text}
    except Exception as e:
        return {"error": str(e)}
