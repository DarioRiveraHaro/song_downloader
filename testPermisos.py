# Prueba rápida de permisos
test_dir = "/storage/emulated/0/Music/downloaded"
test_file = os.path.join(test_dir, "test.tmp")

try:
    os.makedirs(test_dir, exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("test")
    os.remove(test_file)
    print("✅ Tienes permisos de escritura")
except PermissionError:
    print("❌ NO tienes permisos de escritura")