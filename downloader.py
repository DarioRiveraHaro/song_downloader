import os
import json
import yt_dlp

DATA_FILE = "playlists.json"
DOWNLOAD_DIR = "/storage/emulated/0/Music/downloaded"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def create_playlist(data, name):
    if name in data:
        print("⚠️ Esa playlist ya existe.")
    else:
        data[name] = []
        save_data(data)
        print(f"✅ Playlist '{name}' creada.")

def list_playlists(data):
    if not data:
        print("No hay playlists aún.")
    else:
        for i, name in enumerate(data.keys(), 1):
            print(f"{i}. {name}")

def select_playlist(data):
    list_playlists(data)
    name = input("👉 Elige el nombre de la playlist: ").strip()
    if name in data:
        return name
    else:
        print("⚠️ Playlist no encontrada.")
        return None

def download_song_url(string, playlist_name, data):
    if playlist_name not in data:
        print("⚠️ Playlist no válida.")
        return download_song_url

    if string in data[playlist_name]:
        print("⚠️ Esta canción ya está en la playlist.")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:        info = ydl.extract_info(string, download=True)
            title = info.get("title", "Unknown")
            print(f"🎵 Descargado: {title}")
            data[playlist_name].append(string)
            save_data(data)
    except Exception as e:
        print(f"❌ Error: {e}")

def download_song_name(strnig, playlist_name, data):
    yt_dlp 

def main():
    data = load_data()

    while True:
        print("\n=== 🎶 Gestor de Playlists CLI ===")
        print("1. Crear playlist")
        print("2. Listar playlists")
        print("3. Seleccionar playlist y descargar canción")
        print("4. Salir")
        
        choice = input("👉 Elige una opción: ").strip()

        if choice == "1":
            name = input("Nombre de la playlist: ").strip()
            create_playlist(data, name)
        elif choice == "2":
            list_playlists(data)
        elif choice == "3":
            playlist = select_playlist(data)
            if playlist:
                url = input("URL de YouTube: ").strip()
                download_song_url(string, playlist, data)
        elif choice == "4":
            print("👋 Saliendo...")
            break
        else:
            print("⚠️ Opción no válida.")

if __name__ == "__main__":
    main()
