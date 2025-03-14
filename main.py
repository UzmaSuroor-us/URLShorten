from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import shortuuid
import pymysql
import os

app = FastAPI()

# Database Connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "urlshortener")

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    short_url VARCHAR(10) NOT NULL,
    original_url TEXT NOT NULL
)
""")
conn.commit()

class URLRequest(BaseModel):
    original_url: str

@app.post("/shorten")
def shorten_url(request: URLRequest):
    short_url = shortuuid.ShortUUID().random(length=6)
    cursor.execute("INSERT INTO urls (short_url, original_url) VALUES (%s, %s)", (short_url, request.original_url))
    conn.commit()
    return {"short_url": f"https://short.ly/{short_url}"}

@app.get("/{short_url}")
def redirect_url(short_url: str):
    cursor.execute("SELECT original_url FROM urls WHERE short_url = %s", (short_url,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"original_url": result[0]}
