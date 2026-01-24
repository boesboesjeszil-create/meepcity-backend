from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
import time
import json
import random  # For generating fake unique IDs

app = FastAPI()

# In-memory storage (replace with real database later, e.g., PostgreSQL on Render)
active_servers = {}
bad_sounds = []          # List of bad sound IDs (fake data for now)
banned_players = []      # List of banned user IDs (fake data for now)

@app.get("/")
async def root():
    return {"message": "Backend is alive! Use /docs for API docs."}

@app.get("/raw_unixtime")
async def get_unixtime():
    """Returns current Unix timestamp as plain text (matches your Roblox script's expectation)."""
    return PlainTextResponse(str(int(time.time())))

@app.post("/instance.php")
async def register_instance(request: Request):
    """
    Handles server registration from Roblox.
    Expects POST with query params (players counts) and JSON body (player list).
    Returns unique ID, server time, bad sounds, and banned players.
    """
    # Parse query params (e.g., ?unique=0&players_pc=0&... from Roblox script)
    query_params = dict(request.query_params)
    
    # Parse JSON body (player list array)
    try:
        body = await request.json()
    except:
        body = []  # Fallback if no body

    # Generate a unique ID (fake/random for now; make it persistent in real DB)
    unique_id = random.randint(10000, 99999)

    # Store server info (in real app, save to DB)
    active_servers[unique_id] = {
        "players": len(body),
        "platforms": {
            "pc": int(query_params.get("players_pc", 0)),
            "tablet": int(query_params.get("players_tablet", 0)),
            "phone": int(query_params.get("players_phone", 0)),
            "gamepad": int(query_params.get("players_gamepad", 0)),
        },
        "r15": int(query_params.get("players_r15", 0)),
        "silent": int(query_params.get("players_silent", 0)),
        "memory": int(query_params.get("memory", 0)),
        "jobid": query_params.get("jobid", ""),
        "last_seen": time.time()
    }

    # Fake data for bans/sounds (expand this later)
    if not bad_sounds:
        bad_sounds = [12345, 67890]  # Example bad sound IDs
    if not banned_players:
        banned_players = [99999, 88888]  # Example banned user IDs

    return JSONResponse({
        "Unique": unique_id,
        "ServerTime": int(time.time()),
        "BadSounds": bad_sounds,
        "BannedPlayers": banned_players
    })

@app.post("/create_party")
async def create_party(request: Request):
    """
    Placeholder for creating a new party server.
    Expects JSON body with party details (e.g., owner, settings).
    Returns party ID or error.
    """
    try:
        data = await request.json()
        # Fake creation logic - in real app, save to DB and generate ID
        party_id = random.randint(100000, 999999)
        
        active_servers[party_id] = {
            "type": "party",
            "owner": data.get("owner", 0),
            "players": 1,
            "created": time.time()
        }
        
        print(f"Created party {party_id} for owner {data.get('owner')}")
        
        return JSONResponse({
            "success": True,
            "party_id": party_id,
            "message": "Party created"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create party: {str(e)}")

# Optional: Add more endpoints as you expand (e.g., for errors, assets)
@app.post("/report_error")
async def report_error(request: Request):
    """Placeholder for error reporting from Roblox."""
    body = await request.json()
    # Log it somewhere (e.g., print or DB)
    print(f"Error reported: {body}")
    return JSONResponse({"status": "reported"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
