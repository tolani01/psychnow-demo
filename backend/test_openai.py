import asyncio
from app.services.llm_service import llm_service

async def test():
    try:
        result = await llm_service.get_chat_completion([
            {'role': 'user', 'content': 'Say hello in one sentence'}
        ])
        print('[OK] OpenAI Response:', result)
        return True
    except Exception as e:
        print('[ERROR] Error:', str(e))
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    exit(0 if success else 1)

