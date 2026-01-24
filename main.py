from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
import time
import random
import json

app = FastAPI(title="MeepCity-like Backend for Roblox")

# In-memory fake data (replace with real DB later)
active_servers = {}     # key: unique/party id
bad_sounds = [123456, 789012]          # example
banned_players = [9999999, 8888888]    # example banned UserIds

@app.get("/raw_unixtime")
async def raw_unixtime():
    return PlainTextResponse(str(int(time.time())))

@app.post("/instance.php")
async def instance_register(request: Request):
    # Query params from your script
    params = dict(request.query_params)

    # JSON body = player list
    try:
        player_list = await request.json()
    except:
        player_list = []

    # Fake unique ID if not provided (your script sends unique=0 first time)
    unique = int(params.get("unique", 0))
    if unique == 0:
        unique = random.randint(100000, 999999)

    # Store some info (you can expand)
    active_servers[unique] = {
        "players": len(player_list),
        "jobid": params.get("jobid", ""),
        "last_seen": time.time(),
        "player_count_pc": int(params.get("players_pc", 0)),
        # ... add others if you want
    }

    return JSONResponse({
        "Unique": unique,
        "ServerTime": int(time.time()),
        "BadSounds": bad_sounds,
        "BannedPlayers": banned_players
    })

@app.post("/update_party")
async def update_party(request: Request):
    try:
        data = await request.json()
        p_id = data.get("p_id")
        players = data.get("players", 0)

        if p_id not in active_servers:
            # For now, just accept it (your script assumes it exists)
            active_servers[p_id] = {"players": players, "type": "party"}
        else:
            active_servers[p_id]["players"] = players
            active_servers[p_id]["last_seen"] = time.time()

        # Moderated = 0 (no moderation yet)
        return JSONResponse({
            "PartyIsModerated": 0
        })
    except Exception as e:
        raise HTTPException(400, detail=f"Invalid update_party data: {str(e)}")

@app.post("/create_party")
async def create_party(request: Request):
    try:
        data = await request.json()
        # Minimal required fields (adjust based on what your full script sends)
        owner = data.get("owner") or data.get("UserId") or data.get("userId") or 0

        if owner == 0:
            return JSONResponse({
                "Response": "ERROR",
                "message": "Missing owner / UserId"
            }, status_code=400)

        # Fake party creation
        party_id = random.randint(1000000, 9999999)

        active_servers[party_id] = {
            "owner": owner,
            "players": 1,
            "type": "party",
            "created": time.time()
        }

        # Return format your script seems to expect
        return JSONResponse({
            "Response": "SUCCESS",
            "PartyId": party_id
            # You can add "ReserveId" if script expects it, but usually Roblox generates it
        })
    except json.JSONDecodeError:
        raise HTTPException(400, detail="Invalid JSON body")
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/report_error")
async def report_error(request: Request):
    try:
        data = await request.json()  # or use request.form() if query-like
        print("[REPORTED ERROR FROM ROBLOX]", data)
        return JSONResponse({"status": "ok"})
    except:
        return JSONResponse({"status": "error"}, status_code=400)

@app.get("/")
async def root():
    return {"status": "online", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
