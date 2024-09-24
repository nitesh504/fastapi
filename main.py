from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/api/data")
async def get_data(ticker: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://cdn.cboe.com/api/global/delayed_quotes/options/{ticker}.json"
            )
            response.raise_for_status()  
            data = response.json().get("data", {}).get("options", [])
            
            formatted_data = [
                {
                    "option": item.get("option_symbol"),  
                    "bid": item.get("bid"),
                    "ask": item.get("ask"),
                    "volume": item.get("volume"),
                    "open_interest": item.get("open_interest"),
                    "last_trade_price": item.get("last_trade_price"),
                } for item in data if item  
            ]
            
            logging.info(f"Fetched data for {ticker}: {formatted_data}")
            return formatted_data
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")
            raise HTTPException(status_code=500, detail="Error fetching data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
