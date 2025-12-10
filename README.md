# Skylander Editor v3.0

Éditeur de fichiers `.sky` pour Skylanders avec détection automatique du jeu d'origine et niveaux maximum adaptatifs.

## Fonctionnalités

- **Détection automatique du jeu** : Identifie automatiquement le jeu d'origine du Skylander (SSA, Giants, Swap Force, etc.)
- **Niveaux maximum adaptatifs** :
  - Spyro's Adventure : Niveau max 10, XP max 33,000
  - Giants : Niveau max 15, XP max 96,500
  - Swap Force / Trap Team / SuperChargers / Imaginators : Niveau max 20, XP max 197,000
- **Édition des stats** : XP, Niveau, Argent, Heroic Challenges
- **Max Stats** : Maximise toutes les stats en respectant les limites du jeu détecté
- **Visualiseur Hex** : Affiche les premiers 256 octets pour inspection

## Explication des Stats

### XP (Experience Points)
L'expérience accumulée par le Skylander. Détermine le niveau.

### Niveau
Calculé automatiquement à partir de l'XP. Augmente la santé max du Skylander.

### Argent (Money)
L'or collecté, utilisé pour acheter des améliorations. Max: 65,000.

### Heroics (Heroic Challenges)
Représente le nombre de **Heroic Challenges** complétés par ce Skylander.
- Chaque challenge complété donne un bonus permanent de stats (Speed, Armor, Critical Hit, Elemental Power)
- SSA a 32 challenges, Giants en a 50
- Max technique: 255 (byte 8-bit)
- Note: Les valeurs élevées (ex: 253) indiquent un Skylander qui a complété beaucoup de challenges

## Tables XP (Corrigées)

Les tables XP ont été corrigées pour refléter les vraies valeurs du jeu :

### Spyro's Adventure (Niveau max 10)
| Niveau | XP Minimum |
|--------|------------|
| 1 | 0 |
| 2 | 100 |
| 3 | 400 |
| 4 | 1,000 |
| 5 | 2,000 |
| 6 | 4,000 |
| 7 | 7,500 |
| 8 | 13,000 |
| 9 | 20,000 |
| 10 | 28,000 |
| Max XP | 33,000 |

### Giants (Niveau max 15)
| Niveau | XP Minimum |
|--------|------------|
| 11 | 33,000 |
| 12 | 45,000 |
| 13 | 58,000 |
| 14 | 73,000 |
| 15 | 88,000 |
| Max XP | 96,500 |

### Swap Force et suivants (Niveau max 20)
| Niveau | XP Minimum |
|--------|------------|
| 16 | 105,000 |
| 17 | 125,000 |
| 18 | 148,000 |
| 19 | 175,000 |
| 20 | 190,000 |
| Max XP | 197,000 |

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pycryptodome

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Exécution
```bash
python skylander_editor_gui.py
```

## Compilation en exécutable

### Windows
Double-cliquez sur `build_windows.bat` ou exécutez :
```cmd
build_windows.bat
```

### Linux/macOS
```bash
python build.py
```

L'exécutable sera créé dans le dossier `dist/`.

## Utilisation

1. **Ouvrir un fichier** : Cliquez sur "Ouvrir .sky" et sélectionnez votre fichier
2. **Visualiser les infos** : Le programme affiche automatiquement le nom, le jeu d'origine et le niveau maximum
3. **Modifier les stats** : Ajustez l'XP, le niveau, l'argent et les points héroïques
4. **Appliquer** : Cliquez sur "Appliquer" pour valider les modifications
5. **Max Stats** : Cliquez pour maximiser toutes les stats (respecte les limites du jeu)
6. **Sauvegarder** : Cliquez sur "Sauvegarder" pour écrire les modifications dans le fichier

## Base de données

L'éditeur contient une base de données de plus de 300 Skylanders avec leurs noms et jeux d'origine, permettant une identification automatique précise.

## Structure des fichiers .sky

- Taille : 1024 octets (64 blocs × 16 octets)
- Chiffrement : AES-128-ECB avec clé dérivée MD5
- Deux zones de données (0x80 et 0x240) pour redondance
- Checksums CRC-16-CCITT

## Avertissement

⚠️ **Faites toujours une sauvegarde de vos fichiers .sky avant de les modifier !**

## Crédits

- Tables XP basées sur les recherches de la communauté Skylanders
- Base de données des personnages issue de sources communautaires
- Algorithmes de chiffrement documentés par SkyReader et autres projets open-source

## Licence

Ce projet est à but éducatif. Skylanders est une marque déposée d'Activision.
