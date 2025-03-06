from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import sys

# Load environment variables
load_dotenv()

# Check API key
NYT_API_KEY = os.getenv("NYT_API_KEY")
print(f"Current working directory: {os.getcwd()}")
print(f"API Key loaded: {'YES' if NYT_API_KEY else 'NO'}")
print(f"API Key value: {NYT_API_KEY}")

if not NYT_API_KEY or NYT_API_KEY == "your_api_key_here":
    raise ValueError("Valid NYT_API_KEY not found in environment variables")

app = FastAPI(title="NYT MCP Server")

class MCPMessage(BaseModel):
    message_type: str
    content: Dict[str, Any]
    timestamp: str

# Configure NYT API credentials
NYT_API_KEY = os.getenv("NYT_API_KEY")
if not NYT_API_KEY:
    raise ValueError("NYT_API_KEY environment variable is not set")

print(f"Using API key: {NYT_API_KEY}")  # This will show the actual key being used

BASE_URL = "https://api.nytimes.com/svc"

async def make_nyt_request(client: httpx.AsyncClient, endpoint: str, params: Dict[str, Any]) -> Dict:
    """Helper function to make NYT API requests"""
    params = {k: v for k, v in params.items() if v is not None and v != "" and v != 0}
    params["api-key"] = NYT_API_KEY
    
    url = f"{BASE_URL}/{endpoint}"
    print(f"\nMaking request to: {url}")
    print(f"With params: {params}")
    
    response = await client.get(url, params=params)
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    response.raise_for_status()
    return response.json()

@app.post("/mcp/message")
async def handle_mcp_message(message: MCPMessage):
    """
    Handle incoming MCP messages and forward them to appropriate NYT endpoints
    """
    try:
        async with httpx.AsyncClient() as client:
            content = message.content
            
            if message.message_type == "article_search":
                query = content.get("query", "").strip()
                
                params = {
                    "q": query,
                    "sort": content.get("sort", "newest")
                }
                
                # Add date parameters only if specified
                if "begin_date" in content:
                    params["begin_date"] = content["begin_date"]
                if "end_date" in content:
                    params["end_date"] = content["end_date"]
                
                # Only add page if it's greater than 0
                page = content.get("page")
                if page and page > 0:
                    params["page"] = page
                
                response = await make_nyt_request(client, "search/v2/articlesearch.json", params)
                
                # Format the response to show only essential information
                if "response" in response and "docs" in response["response"]:
                    return {
                        "articles": [
                            {
                                "headline": doc.get("headline", {}).get("main", ""),
                                "snippet": doc.get("snippet", ""),
                                "web_url": doc.get("web_url", ""),
                                "pub_date": doc.get("pub_date", "")
                            }
                            for doc in response["response"]["docs"]
                        ],
                        "total_hits": response["response"].get("meta", {}).get("hits", 0)
                    }
                return response

            elif message.message_type == "top_stories":
                section = content.get("section", "home")
                response = await make_nyt_request(client, f"topstories/v2/{section}.json", {})
                # Format top stories response
                if "results" in response:
                    return {
                        "stories": [
                            {
                                "title": story.get("title", ""),
                                "abstract": story.get("abstract", ""),
                                "url": story.get("url", ""),
                                "section": story.get("section", ""),
                                "published_date": story.get("published_date", "")
                            }
                            for story in response["results"]
                        ],
                        "num_results": len(response["results"])
                    }
                return response

            elif message.message_type == "times_wire":
                response = await make_nyt_request(client, "news/v3/content/all/all.json", {
                    "limit": content.get("limit", 20),
                    "offset": content.get("offset", 0),
                    "source": content.get("source", "nyt")
                })
                
                # Format times wire response
                if "results" in response:
                    return {
                        "news_items": [
                            {
                                "title": item.get("title", ""),
                                "abstract": item.get("abstract", ""),
                                "url": item.get("url", ""),
                                "section": item.get("section", ""),
                                "subsection": item.get("subsection", ""),
                                "published_date": item.get("published_date", ""),
                                "byline": item.get("byline", "")
                            }
                            for item in response["results"]
                        ],
                        "num_results": len(response["results"])
                    }
                return response

            elif message.message_type == "most_popular":
                popular_type = content.get("type", "viewed")
                time_period = content.get("time_period", "1")
                response = await make_nyt_request(
                    client, 
                    f"mostpopular/v2/{popular_type}/{time_period}.json",
                    {}
                )
                # Format most popular response
                if "results" in response:
                    return {
                        "articles": [
                            {
                                "title": article.get("title", ""),
                                "abstract": article.get("abstract", ""),
                                "url": article.get("url", ""),
                                "published_date": article.get("published_date", "")
                            }
                            for article in response["results"]
                        ],
                        "num_results": len(response["results"])
                    }
                return response

            elif message.message_type == "archive":
                year = content.get("year", datetime.now().year)
                month = content.get("month", datetime.now().month)
                return await make_nyt_request(
                    client,
                    f"archive/v1/{year}/{month}.json",
                    {}
                )

            elif message.message_type == "books":
                list_name = content.get("list", "hardcover-fiction")
                return await make_nyt_request(
                    client,
                    f"books/v3/lists/current/{list_name}.json",
                    {
                        "offset": content.get("offset", 0)
                    }
                )

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported message type: {message.message_type}"
                )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 