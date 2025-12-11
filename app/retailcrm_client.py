import httpx
from app.config import settings


class RetailCRMClient:
    def __init__(self, api_url: str | None = None, api_key: str | None = None):
        self.api_url = api_url or settings.retailcrm_api_url
        self.api_key = api_key or settings.retailcrm_api_key
        self._client = httpx.AsyncClient(base_url=self.api_url)

    async def get(self, path: str, params: dict | None = None):
        params = params or {}
        params["apiKey"] = self.api_key
        response = await self._client.get(path, params=params)
        print("CRM GET", path, response.status_code, response.text)
        return response.json()

    async def post(self, path: str, data: dict):
        params = {"apiKey": self.api_key}
        response = await self._client.post(path, params=params, data=data)
        print("CRM POST", path, response.status_code, response.text)
        return response.json()

    async def close(self):
        await self._client.aclose()
