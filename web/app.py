from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from bot.config import Config
from bot.utils.database import db
from bot.utils.security import verify_password
from pyrogram import Client
import asyncio
import io

app = FastAPI(title="ABS Stream Fucker")

# Templates
templates = Jinja2Templates(directory="web/templates")

# Static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Initialize Pyrogram client for file access
bot_client = None

async def get_bot_client():
    global bot_client
    if not bot_client:
        bot_client = Client(
            "web_session",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )
        await bot_client.start()
    return bot_client

@app.on_event("startup")
async def startup_event():
    await get_bot_client()

@app.on_event("shutdown")
async def shutdown_event():
    if bot_client:
        await bot_client.stop()

@app.get("/")
async def home(request: Request):
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>{Config.BOT_NAME}</title>
    <style>
        body {{
            background: #0a0a0a;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        h1 {{
            font-size: 3em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        p {{
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        .btn {{
            background: #fff;
            color: #667eea;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s;
            display: inline-block;
        }}
        .btn:hover {{
            transform: scale(1.1);
            box-shadow: 0 10px 30px rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 {Config.BOT_NAME} 🔥</h1>
        <p>Stream & Download Files Like a Boss</p>
        <a href="https://t.me/{Config.BOT_NAME.lower()}_bot" class="btn">Start Bot on Telegram</a>
    </div>
</body>
</html>
""")

@app.get("/stream/{token}")
async def stream_page(request: Request, token: str):
    file_doc = await db.get_file_by_token(token)
    
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    # Increment view
    await db.increment_view(token)
    
    # Check if password protected
    has_password = file_doc.get("password") is not None
    
    return templates.TemplateResponse("stream.html", {
        "request": request,
        "token": token,
        "file_name": file_doc.get("file_name"),
        "has_password": has_password
    })

@app.post("/verify_password/{token}")
async def verify_password_endpoint(token: str, password: str = Form(...)):
    file_doc = await db.get_file_by_token(token)
    
    if not file_doc:
        return {"success": False, "message": "File not found"}
    
    stored_password = file_doc.get("password")
    
    if not stored_password:
        return {"success": True}
    
    # Check password
    if verify_password(password, stored_password):
        return {"success": True}
    else:
        # Increment attempt
        # For now, just return error
        return {"success": False, "message": "Wrong password bhai! 🚫"}

@app.get("/api/stream/{token}")
async def stream_file(token: str, password: str = None):
    file_doc = await db.get_file_by_token(token)
    
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    # Check password if protected
    if file_doc.get("password"):
        if not password:
            raise HTTPException(status_code=401, detail="Password required")
        
        if not verify_password(password, file_doc.get("password")):
            raise HTTPException(status_code=403, detail="Wrong password")
    
    # Get file from Telegram
    client = await get_bot_client()
    file_id = file_doc.get("file_id")
    
    try:
        # Download file in chunks
        async def file_streamer():
            async for chunk in client.stream_media(file_id):
                yield chunk
        
        return StreamingResponse(
            file_streamer(),
            media_type=file_doc.get("mime_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'inline; filename="{file_doc.get("file_name")}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{token}")
async def download_page(request: Request, token: str):
    file_doc = await db.get_file_by_token(token)
    
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    # Check if password protected
    has_password = file_doc.get("password") is not None
    
    return templates.TemplateResponse("download.html", {
        "request": request,
        "token": token,
        "file_name": file_doc.get("file_name"),
        "file_size": file_doc.get("file_size"),
        "has_password": has_password
    })

@app.get("/api/download/{token}")
async def download_file(token: str, password: str = None):
    file_doc = await db.get_file_by_token(token)
    
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    # Check password if protected
    if file_doc.get("password"):
        if not password:
            raise HTTPException(status_code=401, detail="Password required")
        
        if not verify_password(password, file_doc.get("password")):
            raise HTTPException(status_code=403, detail="Wrong password")
    
    # Increment download
    await db.increment_download(token)
    
    # Get file from Telegram
    client = await get_bot_client()
    file_id = file_doc.get("file_id")
    
    try:
        async def file_streamer():
            async for chunk in client.stream_media(file_id):
                yield chunk
        
        return StreamingResponse(
            file_streamer(),
            media_type=file_doc.get("mime_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'attachment; filename="{file_doc.get("file_name")}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=Config.WEB_PORT)
