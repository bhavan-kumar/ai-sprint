import os, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()
API = "https://api.nasa.gov/planetary/apod"
KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

def get_apod(date: str | None = None, retries: int = 3) -> dict:
    params = {"api_key": KEY}
    if date:
        params["date"] = date  # YYYY-MM-DD
    for attempt in range(1, retries + 1):
        r = requests.get(API, params=params, timeout=15)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503) and attempt < retries:
            wait = 2 ** attempt
            console.print(f"[yellow]{r.status_code}, retrying in {wait}s...[/]")
            time.sleep(wait)
            continue
        r.raise_for_status()

def save_image(url: str, date: str) -> Path:
    out = Path("downloads"); out.mkdir(exist_ok=True)
    path = out / f"apod_{date}.jpg"
    path.write_bytes(requests.get(url, timeout=30).content)
    return path

if __name__ == "__main__":
    data = get_apod(sys.argv[1] if len(sys.argv) > 1 else None)
    console.print(Panel(data["explanation"][:400] + "...",
                        title=f"🌌 {data['title']} ({data['date']})"))
    console.print(f"Media type: {data['media_type']}")
    if data["media_type"] == "image":
        p = save_image(data["url"], data["date"])
        console.print(f"[green]Saved → {p}[/]")
    else:
        console.print(f"Not an image today, watch it here: {data['url']}")