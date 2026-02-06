import asyncio
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, status
from loguru import logger

logger.add("api.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")

app = FastAPI()

async def safe_fetch(client: httpx.AsyncClient, url: str):
    try:
        response = await client.get(url, timeout=1.0)
        response.raise_for_status()
        logger.info(f"Aggregated response from api {url}")
        return {"data": response.json(), "status": "success"}
    except httpx.HTTPStatusError as e:
        logger.error(f"Error calling Web Search API: {e.response.is_error}")
        return {"error": f"API error : {e.response.status_code}", "status": "failed"}
    except httpx.TimeoutException:
        logger.error(f"Error Request timed out")
        return {"error": "Request timed out", "status": "failed"}
    except Exception as e:
        logger.error(f"Error calling Web Search API: {str(e)}")
        return {"error": str(e), "status": "failed"}
    
@app.get("/aggregate-results")
async def get_multi_api_data():
    urls = [
        "https://dummyjson.com/users/1",
        "https://dummyjson.com/quotes/1",
        "https://dummyjson.com/todos/1"
    ] 

    async with httpx.AsyncClient() as client:
        tasks = [safe_fetch(client, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "summary": "Aggregated results from multiple sources",
        "results": results
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)