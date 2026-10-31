from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, JSONResponse
from urllib.parse import parse_qs
import time
import random

app = FastAPI(title="MeepCity Roblox Backend Clone")

# In-memory stores
active_parties = {}  # party_id -> details
banned_users = {999999: {"hours": 24}}  # example banned users
asset_sales = {}  # placeholder for get_asset_sales

# --------------------
# BASIC / HEALTH
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
async def raw_unixtime():
    return PlainTextResponse(str(int(time.time())))

# --------------------
# REPORT ERROR
# --------------------
@app.post("/report_error")
async def report_error(request: Request):
    try:
        data = await request.json()
    except:
        data = await request.body()
    print("[REPORT_ERROR]", data)
    return {"ok": True}

# --------------------
# INSTANCE
# --------------------
@app.post("/instance.php")
async def instance(request: Request):
    params = dict(request.query_params)
    try:
        players = await request.json()
    except:
        players = []

    unique = int(params.get("unique") or random.randint(10000, 99999))

    return {
        "Unique": unique,
        "ServerTime": int(time.time()),
        "BadSounds": [12345, 67890],  # fake bad sounds
        "BannedPlayers": list(banned_users.keys())
    }

# --------------------
# CREATE PARTY
# --------------------
@app.post("/create_party")
@app.post("/createparty")
async def create_party(request: Request):
    raw = await request.body()
    data = {}
    try:
        data = await request.json()
    except:
        pass
    if not data and raw:
        try:
            parsed = parse_qs(raw.decode())
            data = {k: v[0] for k, v in parsed.items()}
        except:
            pass

    uid = int(data.get("uid") or data.get("userId") or 0)
    username = data.get("username", "Unknown")
    title = data.get("title", "Untitled Party")

    if uid == 0:
        return {"Response": "ERROR"}

    if uid in banned_users:
        return {"Response": "BANNED", "BanHoursLeft": banned_users[uid]["hours"]}

    party_id = random.randint(1_000_000, 9_999_999)
    active_parties[party_id] = {
        "PartyId": party_id,
        "PartyOwner": uid,
        "PartyOwnerName": username,
        "Title": title,
        "Players": 1,
        "Created": time.time()
    }

    print(f"[BACKEND] PARTY CREATED {party_id} BY {uid}")
    return {"Response": "SUCCESS", "PartyId": party_id}

# --------------------
# UPDATE PARTY
# --------------------
@app.post("/update_party")
@app.post("/updateparty")
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
    return {"PartyIsModerated": 0}

# --------------------
# GET PARTY DATA
# --------------------
@app.post("/get_party_data")
@app.post("/getpartydata")
async def get_party_data(request: Request):
    try:
        data = await request.json()
    except:
        data = {}

    p_id = data.get("p_id")
    if p_id not in active_parties:
        return {"Response": "ERROR"}
    party = active_parties[p_id]
    return {"Response": "SUCCESS", "PartyOwner": party["PartyOwner"], "PartyReserveId": None}

# --------------------
# GET PARTIES LIST
# --------------------
@app.post("/get_parties")
@app.post("/getparties")
async def get_parties(request: Request):
    party_list = []
    for pid, party in active_parties.items():
        party_list.append({
            "PartyId": party["PartyId"],
            "PartyOwner": party["PartyOwner"],
            "Title": party.get("Title", "Untitled Party"),
            "Players": party.get("Players", 1)
        })
    return {"Response": "SUCCESS", "Parties": party_list}

# --------------------
# GET ASSET SALES
# --------------------
@app.post("/get_asset_sales")
async def get_asset_sales(request: Request):
    # This is a placeholder; return empty list for now
    return {"Response": "SUCCESS", "Sales": []}
