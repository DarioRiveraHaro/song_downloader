import os
import json
import yt_dlp
import time
from tqdm import tqdm

# URL hardcodeada - cambia por la que necesites
URL = "https://www.youtube.com/watch?v=xqJurrQKNdE"

# Prueba de permisos y descarga
test_dir = "/storage/emulated/0/Music"
test_file = os.path.join(test_dir, "test.tmp")
download_success = False

try:
    os.makedirs(test_dir, exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("test")
    os.remove(test_file)
    print("✅ Tienes permisos de escritura en Music")
    download_dir = test_dir
except PermissionError:
    print("❌ NO tienes permisos de escritura en Music")
    print("⚠️  Descargando en carpeta Download...")
    download_dir = "/storage/emulated/0/Music/emo"

# Configuración de yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'progress_hooks': [],
}

# Función para progress bar
def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"📥 Descargando: {d.get('_percent_str', '0%')} - {d.get('_eta_str', 'N/A')}")
    elif d['status'] == 'finished':
        print("✅ Conversión a MP3 completada")

ydl_opts['progress_hooks'].append(progress_hook)

# Intentar descargar
print(f"🎵 Iniciando descarga desde: {URL}")
print(f"📁 Guardando en: {download_dir}")

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URL, download=True)
        download_success = True
        print(f"✅ Descarga completada: {info['title']}")
        print(f"📊 Duración: {info['duration']} segundos")
        
except Exception as e:
    print(f"❌ Error en la descarga: {str(e)}")
    download_success = False

# Mover archivo si se descargó en Download pero queremos en Music
if download_success and download_dir != test_dir:
    try:
        # Buscar el archivo descargado
        downloaded_files = [f for f in os.listdir(download_dir) if f.endswith('.mp3')]
        if downloaded_files:
            latest_file = max(downloaded_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
            src_path = os.path.join(download_dir, latest_file)
            dest_path = os.path.join(test_dir, latest_file)
            
            os.makedirs(test_dir, exist_ok=True)
            os.rename(src_path, dest_path)
            print(f"📦 Archivo movido a Music: {latest_file}")
            
    except Exception as e:
        print(f"⚠️  No se pudo mover a Music: {str(e)}")
        print(f"📁 El archivo está en: {download_dir}")

print("🎉 Proceso completado")
