import os
import json
import inquirer
from yt_dlp import YoutubeDL

# --- Configuración ---
# Directorio de descarga apuntando al almacenamiento compartido del teléfono
DOWNLOAD_FOLDER = os.path.expanduser('~/storage/music/emo')
LOG_FILE = 'downloaded_log.json'

# --- Funciones ---

def create_files_and_folders():
    """Crea la carpeta de descargas y el archivo de registro si no existen."""
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
        print(f"📂 Carpeta '{DOWNLOAD_FOLDER}' creada en el almacenamiento del teléfono.")

    # El archivo de log se mantiene dentro de la carpeta del script en Termux
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)
        print(f"📝 Archivo de registro '{LOG_FILE}' creado.")

def load_downloaded_log():
    """Carga los IDs de los videos ya descargados desde el archivo de registro."""
    with open(LOG_FILE, 'r') as f:
        return json.load(f)

def save_to_downloaded_log(video_id):
    """Guarda el ID de un video recién descargado en el archivo de registro."""
    log = load_downloaded_log()
    if video_id not in log:
        log.append(video_id)
        with open(LOG_FILE, 'w') as f:
            json.dump(log, f, indent=4)

def download_audio(url, is_playlist=False):
    """Descarga el audio de una URL de YouTube (video o playlist)."""
    downloaded_ids = load_downloaded_log()

    def hook(d):
        """Función hook para mostrar el estado de la descarga."""
        if d['status'] == 'finished':
            print(f"\n✅ Descarga completa: {d['filename']}")
            video_id = d['info_dict']['id']
            save_to_downloaded_log(video_id)
        if d['status'] == 'downloading':
            # Limpia la línea e imprime el progreso
            print(f"\rDownloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}", end="")


    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [hook],
        'ignoreerrors': True,  # Continúa si un video de la playlist falla
        'download_archive': LOG_FILE
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            
            if is_playlist and 'entries' in info_dict:
                print(f"\n🎧 Descargando playlist: {info_dict.get('title')}")
                for video in info_dict['entries']:
                    if video and video.get('id') in downloaded_ids:
                        print(f"\n⏭️  Saltando (ya descargado): {video.get('title')}")
                        continue
                    if video:
                        ydl.download([video['webpage_url']])

            elif not is_playlist:
                video_id = info_dict.get('id')
                if video_id in downloaded_ids:
                    print(f"\n🤔 '{info_dict.get('title')}' ya fue descargado. Saltando.")
                    return
                print(f"\n🎵 Descargando: {info_dict.get('title')}")
                ydl.download([url])

        except Exception as e:
            print(f"\n❌ Ocurrió un error: {e}")

def main_menu():
    """Muestra el menú principal y maneja la selección del usuario."""
    while True:
        questions = [
            inquirer.List('choice',
                          message="🎶 ¿Qué te gustaría hacer?",
                          choices=['Descargar una sola canción por url', 'Descargar una sola cancion por nombre','Descargar una playlist', 'Salir'],
                          ),
        ]
        choice = inquirer.prompt(questions)['choice']

        if choice == 'Descargar una sola canción':
            url = input("🔗 Pega el link del video de YouTube: ")
            if url:
                download_audio(url)
        elif choice == 'Descargar una sola cancion por nombre':
            url = input("Ingresa el nombre dee la cancion: ")
            if url:
                
        elif choice == 'Descargar una playlist':
            url = input("🔗 Pega el link de la playlist de YouTube: ")
            if url:
                download_audio(url, is_playlist=True)
        elif choice == 'Salir':
            print("👋 ¡Hasta luego!")
            break
        
        input("\nPresiona Enter para volver al menú...")
        os.system('clear')

# --- Inicio del Script ---
if __name__ == "__main__":
    os.system('clear')
    print("==========================================")
    print("    🎵 YouTube Music Downloader 🎵")
    print("==========================================")
    create_files_and_folders()
    main_menu()

