from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import json
import urllib.parse

from database import init_db, get_db_connection, hash_password
from models import UserRegister, FavoriteItem, TokenRequest

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

RECITERS = {
    "ar.alafasy": "مشاری بن راشد العفاسی",
    "ar.abdulbasit": "عبدالباسط عبدالصمد",
    "ar.sudais": "عبدالرحمٰن السدیس"
}

@app.get("/", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")

@app.get("/search", response_class=HTMLResponse)
async def search_quran(request: Request, query: str):
    conn = get_db_connection()
    try:
        conn.cursor().execute("INSERT IGNORE INTO search_history (search_term) VALUES (%s)", (query,))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

    encoded_query = urllib.parse.quote(query)
    api_url = f"https://api.alquran.cloud/v1/search/{encoded_query}/all/ur.jalandhry"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        results = []
        count = 0
        if response.status_code == 200:
            data = response.json()
            results = data["data"]["matches"]
            count = data["data"]["count"]
            
        return templates.TemplateResponse(
            request=request, 
            name="home.html", 
            context={"results": results, "query": query, "count": count}
        )

@app.get("/surah/{surah_number}", response_class=HTMLResponse)
async def get_surah_audio(request: Request, surah_number: int, reciter: str = "ar.alafasy"):
    if reciter not in RECITERS: reciter = "ar.alafasy"
    api_url = f"https://api.alquran.cloud/v1/surah/{surah_number}/{reciter}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        if response.status_code == 200:
            data = response.json()
            surah_name = data["data"]["name"]
            audio_links = [ayah["audio"] for ayah in data["data"]["ayahs"]]
            
            return templates.TemplateResponse(
                request=request, name="surah.html", 
                context={"surah_name": surah_name, "reciter_name": RECITERS[reciter], "audios": json.dumps(audio_links)}
            )
        raise HTTPException(status_code=404, detail="سورہ نہیں ملی۔")

@app.get("/ayah/{surah_number}/{ayah_number}", response_class=HTMLResponse)
async def get_ayah_audio(request: Request, surah_number: int, ayah_number: int, reciter: str = "ar.alafasy"):
    if reciter not in RECITERS: reciter = "ar.alafasy"
    api_url = f"https://api.alquran.cloud/v1/ayah/{surah_number}:{ayah_number}/{reciter}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return templates.TemplateResponse(
                request=request, name="ayah.html", 
                context={"text": data["data"]["text"], "reciter_name": RECITERS[reciter], "audio_url": data["data"]["audio"]}
            )
        raise HTTPException(status_code=404, detail="آیت نہیں ملی۔")

# ================= نیا پیج: فیورٹ دیکھنے کے لیے =================
@app.get("/my-favorites", response_class=HTMLResponse)
async def my_favorites_page(request: Request):
    return templates.TemplateResponse(request=request, name="favorites.html")

# ================= APIs =================
@app.post("/api/register")
async def register_user(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s OR custom_token = %s", (user.username, user.custom_token))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="یہ یوزر نیم یا ٹوکن پہلے سے موجود ہے۔ کوئی اور ٹوکن چنیں۔")
    
    hashed_pw = hash_password(user.password)
    cursor.execute("INSERT INTO users (username, password_hash, custom_token) VALUES (%s, %s, %s)", 
                   (user.username, hashed_pw, user.custom_token))
    conn.commit()
    conn.close()
    return {"message": "آپ کا اکاؤنٹ اور ٹوکن کامیابی سے بن گیا ہے!"}

@app.post("/api/favorites")
async def add_favorite(item: FavoriteItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE custom_token = %s", (item.custom_token,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="آپ کا ٹوکن غلط ہے۔")
        
    user_id = user['id'] if isinstance(user, dict) else user[0]
        
    cursor.execute("INSERT INTO favorites (user_id, surah_number, ayah_number, note) VALUES (%s, %s, %s, %s)",
                   (user_id, item.surah_number, item.ayah_number, item.note))
    conn.commit()
    conn.close()
    return {"message": "کامیابی سے آپ کے اکاؤنٹ میں محفوظ ہو گئی ہے۔"}

@app.post("/api/get_favorites")
async def fetch_favorites(token_req: TokenRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE custom_token = %s", (token_req.custom_token,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="ٹوکن غلط ہے۔ کوئی ڈیٹا نہیں ملا۔")
        
    user_id = user['id'] if isinstance(user, dict) else user[0]
    
    cursor.execute("SELECT surah_number, ayah_number, note FROM favorites WHERE user_id = %s ORDER BY id DESC", (user_id,))
    favorites = cursor.fetchall()
    conn.close()
    
    return {"favorites": favorites}