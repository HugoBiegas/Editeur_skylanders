#!/usr/bin/env python3
"""
Script de build pour Skylander Editor v3
Compatible Windows, macOS et Linux
"""

import os
import sys
import subprocess
import shutil

def main():
    print("=" * 60)
    print("Skylander Editor v3 - Build Script")
    print("=" * 60)
    
    # Vérifier les dépendances
    print("\n[1/4] Vérification des dépendances...")
    try:
        import PyInstaller
        print("  ✓ PyInstaller trouvé")
    except ImportError:
        print("  ✗ PyInstaller non trouvé. Installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    try:
        from Crypto.Cipher import AES
        print("  ✓ pycryptodome trouvé")
    except ImportError:
        print("  ✗ pycryptodome non trouvé. Installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pycryptodome"])
    
    # Nettoyer les anciens builds
    print("\n[2/4] Nettoyage des anciens builds...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  ✓ Supprimé: {folder}")
    
    # Compiler
    print("\n[3/4] Compilation avec PyInstaller...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SkylanderEditor",
        "--add-data", f"skylander_core.py{os.pathsep}.",
        "skylander_editor_gui.py"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n✗ Erreur lors de la compilation!")
        return 1
    
    # Vérifier le résultat
    print("\n[4/4] Vérification du build...")
    
    if sys.platform == 'win32':
        exe_path = os.path.join('dist', 'SkylanderEditor.exe')
    else:
        exe_path = os.path.join('dist', 'SkylanderEditor')
    
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"  ✓ Build réussi: {exe_path} ({size:.1f} MB)")
    else:
        print("  ✗ Fichier exécutable non trouvé!")
        return 1
    
    print("\n" + "=" * 60)
    print("Build terminé avec succès!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
