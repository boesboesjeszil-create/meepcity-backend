from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
import time
import random
import json

app = FastAPI(title="MeepCity Roblox Backend Clone")

# In-memory stores (fake data - use PostgreSQL on Render later)
active_parties = {}    # party_id -> details
banned_users = {999999: {"hours": 24}}  # userId -> ban info (example)

@app.get("/raw_unixtime")
async def get_unixtime():
    return PlainTextResponse(str(int(time.time())))

@app.post("/instance.php")
async def register_instance(request: Request):
    params = dict(request.query_params)
    try:
        player_list = await request.json()
    except:
        player_list = []

    unique = int(params.get("unique", random.randint(10000, 99999)))
    active_parties[unique] = {"type": "instance", "players": len(player_list)}  # simplified

    return JSONResponse({
        "Unique": unique,
        "ServerTime": int(time.time()),
        "BadSounds": [12345, 67890],  # fake
        "BannedPlayers": list(banned_users.keys())  # fake
    })

@app.post("/update_party")
async def update_party(request: Request):
    try:
        data = await request.json()
        p_id = data.get("p_id")
        players = data.get("players", 0)

        if p_id in active_parties:
            active_parties[p_id]["players"] = players
            active_parties[p_id]["last_updated"] = time.time()

        return JSONResponse({"PartyIsModerated": 0})  # never moderate for now
    except:
        raise HTTPException(400, "Invalid update_party")

@app.post("/create_party")
async def create_party(request: Request):
    try:
        body = await request.json() if await request.body() else {}
    except json.JSONDecodeError:
        body = {}

    uid = body.get("uid") or body.get("userId") or 0
    username = body.get("username", "Unknown")
    title = body.get("title", "Untitled Party")
    reserve = body.get("reserve")
    place_id = body.get("place_id")
    max_players = body.get("max_players", 10)
    estate_tier = body.get("estate_tier", 1)
    platform = body.get("platform", 1)

    if uid == 0:
        return JSONResponse({"Response": "ERROR", "message": "Missing uid"}, status_code=400)

    # Fake ban check
    if uid in banned_users:
        return JSONResponse({
            "Response": "BANNED",
            "BanHoursLeft": banned_users[uid]["hours"]
        }, status_code=200)  # 200 so script can read it

    # Create party
    party_id = random.randint(1000000, 9999999)
    active_parties[party_id] = {
        "PartyId": party_id,
        "PartyOwner": uid,
        "PartyOwnerName": username,
        "Title": title,
        "ReserveId": reserve,
        "PlaceId": place_id,
        "MaxPlayers": max_players,
        "EstateTier": estate_tier,
        "Platform": platform,
        "Created": time.time(),
        "Players": 1
    }

    print(f"[Backend] Created party {party_id} for UID {uid} ({username}) - Title: {title}")

    return JSONResponse({
        "Response": "SUCCESS",
        "PartyId": party_id
        # Add more keys if script expects them (e.g. "PartyReserveId": reserve)
    })

@app.post("/get_party_data")
async def get_party_data(request: Request):
    try:
        data = await request.json()
        p_id = data.get("p_id")

        if p_id not in active_parties:
            return JSONResponse({"Response": "ERROR", "message": "Party not found"}, status_code=404)

        party = active_parties[p_id]
        return JSONResponse({
            "Response": "SUCCESS",
            "PartyOwner": party["PartyOwner"],
            "PartyReserveId": party.get("ReserveId"),
            # Add more fields your script might use
        })
    except:
        raise HTTPException(400, "Invalid get_party_data")

@app.get("/")
async def root():
    return {"status": "online"}

# Optional: Suppress HEAD noise (Render health checks)
@app.head("/")
async def health_head():
    return Response(status_code=200)
