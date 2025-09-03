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

def download_song_url(url, playlist_name, data):
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
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:        
            info = ydl.extract_info(string, download=True)
            title = info.get("title", "Unknown")
            print(f"🎵 Descargado: {title}")
            data[playlist_name].append(string)
            save_data(data)
    except Exception as e:
        print(f"❌ Error: {e}")

def search_and_download_song(strnig, playlist_name, data):
    # Funcion para buscar y descargar cancion por nombre
    print(f"🔍 Buscando: {song_name}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search' 'ytsearch1:',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YouTubeDl(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=False)
            if 'entries' in info:
                video = info['entries'][0]
                title = video.get('title', 'Unknown')
                url = video.get('webpage_url', '')

                print(f"✅ Encontrado: {title}")
                print(f"🌐 URL: {url}")

                confirm = input("¿Descargar esta canción? (s/n): ").strip().lower()

                if confirm == 's':
                    download_song_url(url, playlist_name, data)
                else:
                    print("❌ No se encontró la canción")
            
            except Exception as e:
                print(f"❌ Error en la búsqueda: {e}")

def main():
    data = load_data()

    while True:
        print("\n=== 🎶 Gestor de Playlists CLI ===")
        print("1. Crear playlist")
        print("2. Listar playlists")
        print("3. Descargar canción desde URL")
        print("4. Buscar y descargar canción por nombre")
        print("5. Salir")
        
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
            playlist = select_playlist(data)
            if playlist:
                song_name = input("Nombre de la cancion a buscar: ").strip()
                search_and_download_song(song_name, playlist, data)
        elif choice == "5":
            print("👋 Saliendo...")
            break
        else:
            print("⚠️ Opción no válida.")

if __name__ == "__main__":
    main()
