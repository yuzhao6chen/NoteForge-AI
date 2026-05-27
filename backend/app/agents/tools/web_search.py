import requests
from app.core.config import settings


class WebSearchTool:
    """
    WebSearchTool:
    - tavily: 调用 Tavily Search API 做真实联网搜索

    建议：
    - 每次最多使用 3 个 query
    - 每个 query 最多取 3 条结果
    - 使用 basic search，速度快、消耗低
    """

    def search(self, queries: list[str], max_results_per_query: int = 3) -> list[dict]:
        provider = settings.search_provider.lower().strip()

        if provider != "tavily":
            raise ValueError("SEARCH_PROVIDER 仅支持 tavily。项目已移除本地 mock 搜索降级逻辑，请在 backend/.env 中配置真实搜索 API。")

        if not settings.tavily_api_key:
            raise ValueError("SEARCH_PROVIDER=tavily，但 TAVILY_API_KEY 为空。请检查 backend/.env。")

        return self._tavily_search(
            queries=queries,
            max_results_per_query=max_results_per_query,
        )

    def _tavily_search(self, queries: list[str], max_results_per_query: int = 3) -> list[dict]:
        all_results: list[dict] = []

        # 控制搜索数量，避免一次文章生成消耗太多 credits
        limited_queries = [q for q in queries if q.strip()][:3]

        for query in limited_queries:
            response = requests.post(
                "https://api.tavily.com/search",
                headers={
                    "Authorization": f"Bearer {settings.tavily_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "search_depth": "basic",
                    "max_results": max_results_per_query,
                    "include_answer": False,
                    "include_raw_content": False,
                    "include_images": False,
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            for item in data.get("results", []):
                all_results.append({
                    "query": query,
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "source": "tavily",
                    "published_at": item.get("published_date", ""),
                    "relevance_score": item.get("score", 0),
                })

        return all_results
