import os
import json
import yt_dlp
import time
from tqdm import tqdm

DATA_FILE = "playlists.json"
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "storage", "music")

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

def rename_playlist(data, old_name):
    """Renombrar una playlist existente"""
    if old_name not in data:
        print("⚠️ Playlist no encontrada.")
        return False
    
    new_name = input(f"Nuevo nombre para '{old_name}': ").strip()
    
    if not new_name:
        print("❌ El nombre no puede estar vacío.")
        return False
    
    if new_name in data:
        print("⚠️ Ya existe una playlist con ese nombre.")
        return False
    
    data[new_name] = data.pop(old_name)
    save_data(data)
    print(f"✅ Playlist renombrada de '{old_name}' a '{new_name}'.")
    return True

def delete_playlist(data, name):
    if name not in data:
        print("⚠️ Playlist no encontrada.")
        return False
    
    print(f"🗑️  Playlist a eliminar: {name}")
    print(f"📊 Canciones en la playlist: {len(data[name])}")

    delete_files = input("¿Eliminar también los archivos de audio? (s/n): ").strip().lower()

    deleted_count = 0
    if delete_files == 's':
        for url in data[name]:
            try:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    filename = f"{title}.mp3"
                    filepath = os.path.join(DOWNLOAD_DIR, filename)

                    if os.path.exists(filepath):
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"🗑️  Eliminado: {filename}")
            except:
                continue
        print(f"📊 Archivos eliminados: {deleted_count}")
    
    del data[name]
    save_data(data)
    print(f"✅ Playlist '{name}' eliminada.")
    return True

def list_playlists(data):
    if not data:
        print("No hay playlists aún.")
    else:
        print("\n📋 Playlists disponibles:")
        for i, (name, songs) in enumerate(data.items(), 1):
            print(f"{i}. {name} ({len(songs)} canciones)")

def select_playlist(data):
    list_playlists(data)
    if not data:
        return None
        
    name = input("👉 Elige el nombre de la playlist: ").strip()
    if name in data:
        return name
    else:
        print("⚠️ Playlist no encontrada.")
        return None

def download_with_progress(url, output_path):
    """Descarga con barra de progreso"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [lambda d: progress_hook(d, output_path)],
        'nopart': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
            return result == 0
    except Exception as e:
        print(f"❌ Error en la descarga: {e}")
        return False

def progress_hook(d, output_path):
    """Hook para mostrar progreso de descarga"""
    if d['status'] == 'downloading':
        filename = os.path.basename(output_path)
        if 'total_bytes' in d and d['total_bytes'] > 0:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            print(f"📥 {filename}: {percent:.1f}% ({d['downloaded_bytes']}/{d['total_bytes']} bytes)", end='\r')
        elif 'downloaded_bytes' in d:
            print(f"📥 {filename}: {d['downloaded_bytes']} bytes descargados", end='\r')
    elif d['status'] == 'finished':
        print(f"\n✅ Descarga completada: {os.path.basename(output_path)}")

def download_song_url(url, playlist_name, data, retry_count=0):
    """Descarga una canción con reintentos"""
    if playlist_name not in data:
        print("⚠️ Playlist no válida.")
        return False

    if url in data[playlist_name]:
        print("⚠️ Esta canción ya está en la playlist.")
        return False

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    try:
        # Primero obtener información para el nombre del archivo
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown")
            output_path = os.path.join(DOWNLOAD_DIR, f"{title}.%(ext)s")
        
        # Descargar con barra de progreso
        success = download_with_progress(url, output_path)
        
        if success:
            data[playlist_name].append(url)
            save_data(data)
            print(f"🎵 '{title}' añadida a '{playlist_name}'")
            return True
        else:
            if retry_count < 3:
                print(f"🔄 Reintentando descarga ({retry_count + 1}/3)...")
                time.sleep(2)
                return download_song_url(url, playlist_name, data, retry_count + 1)
            else:
                print("❌ Demasiados intentos fallidos. Saltando canción.")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def download_youtube_playlist(playlist_url, playlist_name, data):
    """Descargar una playlist completa de YouTube"""
    print(f"📥 Descargando playlist: {playlist_url}")
    
    try:
        # Obtener información de la playlist
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' not in playlist_info:
                print("❌ No se pudo obtener la playlist.")
                return False
            
            total_songs = len(playlist_info['entries'])
            print(f"🎵 Encontradas {total_songs} canciones en la playlist")
            
            # Crear playlist si no existe
            if playlist_name not in data:
                data[playlist_name] = []
            
            # Descargar cada canción
            success_count = 0
            for i, entry in enumerate(playlist_info['entries'], 1):
                if 'url' in entry:
                    print(f"\n📋 [{i}/{total_songs}] Procesando canción...")
                    if download_song_url(entry['url'], playlist_name, data):
                        success_count += 1
            
            print(f"\n✅ Descarga completada: {success_count}/{total_songs} canciones descargadas")
            return True
            
    except Exception as e:
        print(f"❌ Error al descargar playlist: {e}")
        return False

def check_corrupted_files(data):
    """Verificar archivos corruptos o duplicados"""
    print("🔍 Verificando archivos...")
    
    all_files = {}
    corrupted_files = []
    missing_files = []
    
    # Recolectar todos los archivos
    for playlist_name, urls in data.items():
        for url in urls:
            try:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    filename = f"{title}.mp3"
                    filepath = os.path.join(DOWNLOAD_DIR, filename)
                    
                    # Verificar si el archivo existe
                    if not os.path.exists(filepath):
                        missing_files.append((filename, playlist_name))
                    else:
                        # Verificar duplicados
                        if filename in all_files:
                            all_files[filename].append(playlist_name)
                        else:
                            all_files[filename] = [playlist_name]
                            
                        # Verificar si el archivo está corrupto (tamaño muy pequeño)
                        if os.path.getsize(filepath) < 1024:  # Menos de 1KB
                            corrupted_files.append((filename, playlist_name))
                            
            except Exception as e:
                print(f"⚠️ Error verificando {url}: {e}")
    
    # Mostrar resultados
    if missing_files:
        print("\n❌ Archivos faltantes:")
        for filename, playlist in missing_files:
            print(f"   - {filename} (en {playlist})")
    
    if corrupted_files:
        print("\n❌ Archivos corruptos (tamaño muy pequeño):")
        for filename, playlist in corrupted_files:
            print(f"   - {filename} (en {playlist})")
    
    duplicates = {f: p for f, p in all_files.items() if len(p) > 1}
    if duplicates:
        print("\n⚠️ Archivos duplicados en múltiples playlists:")
        for filename, playlists in duplicates.items():
            print(f"   - {filename}: {', '.join(playlists)}")
    
    if not missing_files and not corrupted_files and not duplicates:
        print("✅ Todos los archivos están en buen estado y sin duplicados.")
    
    return len(missing_files) + len(corrupted_files)

def search_and_download_song(song_name, playlist_name, data):
    print(f"🔍 Buscando: {song_name}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1:',
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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
        print("5. Descargar playlist completa de YouTube")
        print("6. Renombrar playlist")
        print("7. Verificar archivos")
        print("8. Borrar playlist")
        print("9. Salir")
        
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
                download_song_url(url, playlist, data)
        elif choice == "4":
            playlist = select_playlist(data)
            if playlist:
                song_name = input("Nombre de la canción a buscar: ").strip()
                search_and_download_song(song_name, playlist, data)
        elif choice == "5":
            playlist_name = input("Nombre para la nueva playlist: ").strip()
            if playlist_name:
                playlist_url = input("URL de la playlist de YouTube: ").strip()
                download_youtube_playlist(playlist_url, playlist_name, data)
        elif choice == "6":
            playlist = select_playlist(data)
            if playlist:
                rename_playlist(data, playlist)
        elif choice == "7":
            check_corrupted_files(data)
        elif choice == "8":
            playlist = select_playlist(data)
            if playlist:
                confirm = input(f"¿Estás seguro de borrar la playlist '{playlist}'? (s/n): ").strip().lower()
                if confirm == 's':
                    delete_playlist(data, playlist)
                else:
                    print("❌ Operación cancelada.")
        elif choice == "9":
            print("👋 Saliendo...")
            break
        else:
            print("⚠️ Opción no válida.")

if __name__ == "__main__":
    main()