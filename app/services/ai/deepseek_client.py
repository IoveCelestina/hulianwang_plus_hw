import httpx
from app.core.config import settings

class DeepSeekClient:
    def __init__(self):
        self.base_url = settings.DEEPSEEK_BASE_URL.rstrip("/")
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL

    async def chat_completion(self, messages: list[dict], timeout_s: float = 25.0) -> str:
        # 这里按“通用 Chat Completions”形式写，具体字段你可按你账户实际返回适配。
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
