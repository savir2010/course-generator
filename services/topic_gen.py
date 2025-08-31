import asyncio
from serpapi.google_search import GoogleSearch
from config import Config

class TopicGen:
    def __init__(self):
        self.serpapi_key = Config.SERPAPI_KEY

    async def get_video(self, query: str):
        def sync_search():
            params = {"engine": "youtube", "api_key": self.serpapi_key, "search_query": query}
            search = GoogleSearch(params)
            results = search.get_dict()
            for video in results.get("video_results", []):
                length = video.get("length", "0:00")
                mins = int(length.split(":")[0])
                if 15 <= mins <= 20:
                    return {"url": video["link"], "title": video["title"], "duration": mins}
            return None

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_search)
