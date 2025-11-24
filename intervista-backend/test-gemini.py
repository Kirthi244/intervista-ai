import asyncio
from app.utils import call_gemini_chat

async def main():
    prompt = "Write a short story about a robot learning to code."
    result = await call_gemini_chat(prompt)
    print(result)

asyncio.run(main())
