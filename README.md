# NYT MCP Server

A Message Concentrator Protocol (MCP) server that provides a unified, simple interface to the New York Times APIs. This server simplifies interaction with multiple NYT APIs through a single endpoint.

## Overview

This MCP server acts as a unified gateway to various New York Times APIs, including:
- Article Search
- Top Stories
- Times Wire (Real-time news)
- Most Popular
- Archive
- Books API

## Features

- Single Endpoint: Access all NYT APIs through one consistent interface
- Clean Responses: Formatted and simplified API responses
- Real-time Updates: Live news feed via Times Wire
- Flexible Search: Comprehensive article search capabilities
- Error Handling: Robust error management
- Health Monitoring: Built-in health check endpoint
- Easy Integration: Simple to integrate with any application

## Requirements

- Python 3.8+
- NYT API Key (get one at [NYT Developer Portal](https://developer.nytimes.com/))
- Required Python packages (see requirements.txt)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-username/nyt-mcp-server.git
cd nyt-mcp-server
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
NYT_API_KEY=your_api_key_here
MCP_PORT=8000
MCP_HOST=0.0.0.0
```

5. Run the server:
```bash
python src/server.py
```

## Project Structure

```
nyt-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py
│   └── config.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### POST /mcp/message
Main endpoint for all NYT API interactions.

#### GET /health
Health check endpoint.

### Example Usage

```python
import httpx
import asyncio

async def get_news():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/message",
            json={
                "message_type": "times_wire",
                "content": {"limit": 5},
                "timestamp": "2025-03-05T21:00:00Z"
            }
        )
        return response.json()

# Run the async function
asyncio.run(get_news())
```

## Message Types

### 1. Article Search
```json
{
    "message_type": "article_search",
    "content": {
        "query": "technology",
        "sort": "newest",
        "page": 0
    },
    "timestamp": "2025-03-05T21:00:00Z"
}
```

### 2. Top Stories
```json
{
    "message_type": "top_stories",
    "content": {
        "section": "technology"
    },
    "timestamp": "2025-03-05T21:00:00Z"
}
```

### 3. Times Wire
```json
{
    "message_type": "times_wire",
    "content": {
        "limit": 5,
        "source": "nyt"
    },
    "timestamp": "2025-03-05T21:00:00Z"
}
```

### 4. Most Popular
```json
{
    "message_type": "most_popular",
    "content": {
        "type": "viewed",
        "time_period": "7"
    },
    "timestamp": "2025-03-05T21:00:00Z"
}
```

### 5. Archive
```json
{
    "message_type": "archive",
    "content": {
        "year": 2025,
        "month": 3
    },
    "timestamp": "2025-03-05T21:00:00Z"
}
```

### 6. Books
```json
{
    "message_type": "books",
    "content": {
        "list": "hardcover-fiction"
    },
    "timestamp": "2025-03-05T21:00:00Z"
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License

## Security Note

- Never commit your `.env` file
- Keep your NYT API key private
- Use environment variables for sensitive data

## Contact

Create an issue for bug reports or feature requests.