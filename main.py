from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse, Response
import time
import random

app = FastAPI(title="MeepCity Roblox Backend Clone")

active_parties = {}
banned_users = {999999: {"hours": 24}}

# --------------------
# BASIC
# --------------------

@app.get("/")
async def root():
    return {"status": "online"}

@app.head("/")
async def health_head():
    return Response(status_code=200)

# --------------------
# TIME
# --------------------

@app.get("/raw_unixtime")
async def get_unixtime():
    return PlainTextResponse(str(int(time.time())))

# --------------------
# INSTANCE
# --------------------

@app.post("/instance.php")
async def register_instance(request: Request):
    params = dict(request.query_params)

    try:
        player_list = await request.json()
    except:
        player_list = []

    unique = int(params.get("unique") or random.randint(10000, 99999))

    active_parties[unique] = {
        "type": "instance",
        "players": len(player_list),
        "updated": time.time()
    }

    return JSONResponse({
        "Unique": unique,
        "ServerTime": int(time.time()),
        "BadSounds": [],
        "BannedPlayers": list(banned_users.keys())
    })

# --------------------
# CREATE PARTY
# --------------------

from urllib.parse import parse_qs

@app.post("/create_party")
async def create_party(request: Request):
    body_bytes = await request.body()

    data = {}

    # Try JSON first
    try:
        data = await request.json()
    except:
        pass

    # Fallback: Roblox form-encoded body
    if not data and body_bytes:
        try:
            parsed = parse_qs(body_bytes.decode())
            data = {k: v[0] for k, v in parsed.items()}
        except:
            pass

    uid = int(data.get("uid") or data.get("userId") or 0)
    username = data.get("username", "Unknown")
    title = data.get("title", "Untitled Party")

    if uid == 0:
        print("[Backend] create_party failed: missing uid")
        return JSONResponse({"Response": "ERROR"}, status_code=200)

    party_id = random.randint(1_000_000, 9_999_999)

    active_parties[party_id] = {
        "PartyId": party_id,
        "PartyOwner": uid,
        "PartyOwnerName": username,
        "Title": title,
        "Players": 1,
        "Created": time.time()
    }

    print(f"[Backend] PARTY CREATED {party_id} BY {uid}")

    return JSONResponse({
        "Response": "SUCCESS",
        "PartyId": party_id
    })

# --------------------
# UPDATE PARTY
# --------------------

@app.post("/update_party")
async def update_party(request: Request):
    try:
        data = await request.json()
    except:
        data = {}

    p_id = data.get("p_id")
    players = data.get("players", 0)

    if p_id in active_parties:
        active_parties[p_id]["Players"] = players
        active_parties[p_id]["Updated"] = time.time()

    return JSONResponse({"PartyIsModerated": 0})

# --------------------
# GET PARTY DATA
# --------------------

@app.post("/get_party_data")
async def get_party_data(request: Request):
    try:
        data = await request.json()
    except:
        data = {}

    p_id = data.get("p_id")

    if p_id not in active_parties:
        return JSONResponse(
            {"Response": "ERROR", "message": "Party not found"},
            status_code=404
        )

    party = active_parties[p_id]

    return JSONResponse({
        "Response": "SUCCESS",
        "PartyOwner": party["PartyOwner"],
        "PartyReserveId": None
    })

# =========================================================
# 🔁 ALIASES FOR ROBLOX (THIS IS THE IMPORTANT PART)
# =========================================================

@app.post("/createparty")
async def createparty_alias(request: Request):
    return await create_party(request)

@app.post("/updateparty")
async def updateparty_alias(request: Request):
    return await update_party(request)

@app.post("/getpartydata")
async def getpartydata_alias(request: Request):
    return await get_party_data(request)
