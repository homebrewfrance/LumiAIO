# SCRIPT GENERE PAR INTELLIGENCE ARTIFICIELLE

import os
import requests
import zipfile
import shutil
import json
from io import BytesIO

# -------- CONFIGURATION --------
TMP_DIR = "tmp_pack"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
REPO = "homebrewfrance/LumiAIO"
RELEASE_TAG = "V1"

GENERATED_PACKS = []

# ---------------------------
# Fonctions utilitaires
def clean_tmp():
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

def download_github_release(repo, asset_name_contains=None, asset_name_exact=None):
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(api_url, headers=HEADERS)
    response.raise_for_status()
    release = response.json()
    
    for asset in release['assets']:
        if (asset_name_exact and asset['name'] == asset_name_exact) or \
           (asset_name_contains and asset_name_contains in asset['name']) or \
           (not asset_name_contains and not asset_name_exact):
            print(f"Téléchargement de {asset['name']} depuis {repo}...")
            r = requests.get(asset['browser_download_url'], headers=HEADERS)
            r.raise_for_status()
            return BytesIO(r.content), asset['name']
    
    raise ValueError(f"Asset correspondant non trouvé pour {repo}")

def download_cia_3ds(repo, cia_name, folder_3ds):
    folder_cia = os.path.join(TMP_DIR, "cias")
    os.makedirs(folder_cia, exist_ok=True)
    os.makedirs(folder_3ds, exist_ok=True)

    cia_io, _ = download_github_release(repo, asset_name_contains=f"{cia_name}.cia")
    with open(os.path.join(folder_cia, f"{cia_name}.cia"), "wb") as f:
        f.write(cia_io.read())

    x3ds_io, _ = download_github_release(repo, asset_name_contains=f"{cia_name}.3dsx")
    with open(os.path.join(folder_3ds, f"{cia_name}.3dsx"), "wb") as f:
        f.write(x3ds_io.read())

def generate_pack_txt(pack_name, apps_list):
    header = f"================| LumiAIO {pack_name.upper()} |================\n\nCe pack contient :\n"
    content = "\n".join(f"- {app}" for app in apps_list)
    txt_path = os.path.join(TMP_DIR, f"PACK - {pack_name.upper()}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(header + content)

def create_zip(pack_name):
    zip_file_name = f"LumiAIO-{pack_name.upper()}.zip"
    shutil.make_archive(pack_name, 'zip', TMP_DIR)
    os.rename(f"{pack_name}.zip", zip_file_name)  # renommer le zip
    print(f"Pack {zip_file_name} créé avec succès !")
    GENERATED_PACKS.append(zip_file_name)


# ---------------------------
# 1. Créer Vanilla.zip
clean_tmp()
apps_vanilla = []

# Luma3DS
luma_zip_io, _ = download_github_release("LumaTeam/Luma3DS")
with zipfile.ZipFile(luma_zip_io) as z:
    for f in ["boot.firm", "boot.3dsx"]:
        z.extract(f, TMP_DIR)
apps_vanilla.append("Luma3DS")

# Boot9Strap
api_url = "https://api.github.com/repos/SciresM/boot9strap/releases/latest"
response = requests.get(api_url, headers=HEADERS)
response.raise_for_status()
release = response.json()
tag_name = release['tag_name']
asset_name_exact = f"boot9strap-{tag_name}.zip"
boot9_io, _ = download_github_release("SciresM/boot9strap", asset_name_exact=asset_name_exact)
boot9_dir = os.path.join(TMP_DIR, "boot9strap")
os.makedirs(boot9_dir, exist_ok=True)
with zipfile.ZipFile(boot9_io) as z:
    z.extract("boot9strap.firm", boot9_dir)
    z.extract("boot9strap.firm.sha", boot9_dir)
apps_vanilla.append("Boot9Strap")

# FBI
fbi_cia_dir = os.path.join(TMP_DIR, "cias")
fbi_3ds_dir = os.path.join(TMP_DIR, "3ds")
os.makedirs(fbi_cia_dir, exist_ok=True)
os.makedirs(fbi_3ds_dir, exist_ok=True)
fbi_cia_io, _ = download_github_release("Steveice10/FBI", "FBI.cia")
fbi_3ds_io, _ = download_github_release("Steveice10/FBI", "FBI.3dsx")
with open(os.path.join(fbi_cia_dir, "FBI.cia"), "wb") as f: f.write(fbi_cia_io.read())
with open(os.path.join(fbi_3ds_dir, "FBI.3dsx"), "wb") as f: f.write(fbi_3ds_io.read())
apps_vanilla.append("FBI")

# Universal-Updater
uu_io, _ = download_github_release("Universal-Team/Universal-Updater", "Universal-Updater.cia")
with open(os.path.join(fbi_cia_dir, "Universal-Updater.cia"), "wb") as f: f.write(uu_io.read())
apps_vanilla.append("Universal-Updater")

# GodMode9
gm9_io, _ = download_github_release("d0k3/GodMode9")
with zipfile.ZipFile(gm9_io) as z:
    for name in z.namelist():
        if name.startswith("sample") or name.startswith("gm9"):
            z.extract(name, TMP_DIR)
        elif os.path.basename(name) == "GodMode9.firm":
            luma_payload_dir = os.path.join(TMP_DIR, "luma", "payloads")
            os.makedirs(luma_payload_dir, exist_ok=True)
            z.extract(name, luma_payload_dir)
apps_vanilla.append("GodMode9")

# SafeB9SInstaller
safeb9s_io, _ = download_github_release("d0k3/safeb9sinstaller", "SafeB9SInstaller-")
with zipfile.ZipFile(safeb9s_io) as z:
    for name in z.namelist():
        if os.path.basename(name) == "SafeB9SInstaller.bin":
            with z.open(name) as source, open(os.path.join(TMP_DIR, "SafeB9SInstaller.bin"), "wb") as target:
                shutil.copyfileobj(source, target)
apps_vanilla.append("SafeB9SInstaller")

# Homebrew_Launcher
homebrew_io, _ = download_github_release("PabloMK7/homebrew_launcher_dummy", "Homebrew_Launcher.cia")
with open(os.path.join(fbi_cia_dir, "Homebrew_Launcher.cia"), "wb") as f: f.write(homebrew_io.read())
apps_vanilla.append("Homebrew_Launcher")

# Anemone3DS et Checkpoint
download_cia_3ds("astronautlevel2/Anemone3DS", "Anemone3DS", fbi_3ds_dir)
apps_vanilla.append("Anemone3DS")
download_cia_3ds("BernardoGiordano/Checkpoint", "Checkpoint", fbi_3ds_dir)
apps_vanilla.append("Checkpoint")

# Génération du TXT et du pack Vanilla
generate_pack_txt("Vanilla", apps_vanilla)
create_zip("VANILLA")

# ---------------------------
# 2. Ntrboot.zip (Vanilla + ntrboot_flasher.firm)
clean_tmp()
with zipfile.ZipFile("LumiAIO-VANILLA.zip") as z:
    z.extractall(TMP_DIR)

ntr_dir = os.path.join(TMP_DIR, "luma", "payloads")
os.makedirs(ntr_dir, exist_ok=True)
ntr_io, _ = download_github_release("ntrteam/ntrboot_flasher", "ntrboot_flasher.firm")
with open(os.path.join(ntr_dir, "ntrboot_flasher.firm"), "wb") as f: f.write(ntr_io.read())
apps_ntrboot = apps_vanilla + ["ntrboot_flasher"]
generate_pack_txt("Ntrboot", apps_ntrboot)
vanilla_txt = os.path.join(TMP_DIR, "PACK - VANILLA.txt")
if os.path.exists(vanilla_txt):
    os.remove(vanilla_txt)
create_zip("NTRBOOTHAX")

# ---------------------------
# 3. KartMiner7.zip
clean_tmp()
with zipfile.ZipFile("LumiAIO-VANILLA.zip") as z:
    z.extractall(TMP_DIR)

menuhax_io, _ = download_github_release("zoogie/menuhax67")
with zipfile.ZipFile(menuhax_io) as z:
    for name in z.namelist():
        if "NEW3DS" in name or "OLD3DS" in name or name.endswith("menuhax_67_installer.3dsx"):
            z.extract(name, os.path.join(TMP_DIR, "3ds"))

nimds_io, _ = download_github_release("luigoalma/nimdsphax")
with zipfile.ZipFile(nimds_io) as z:
    for name in z.namelist():
        if name.startswith("nimdsphax"):
            z.extract(name, os.path.join(TMP_DIR, "3ds"))

apps_kartminer7 = apps_vanilla + ["Menuhax67", "NimDSPhax"]
generate_pack_txt("KartMiner7", apps_kartminer7)
vanilla_txt = os.path.join(TMP_DIR, "PACK - VANILLA.txt")
if os.path.exists(vanilla_txt):
    os.remove(vanilla_txt)
create_zip("KARTMINER7")

# ---------------------------
# 4. Browserhax.zip
clean_tmp()
with zipfile.ZipFile("LumiAIO-VANILLA.zip") as z:
    z.extractall(TMP_DIR)

api_url = "https://api.github.com/repos/zoogie/old-browserhax/releases/latest"
response = requests.get(api_url, headers=HEADERS)
response.raise_for_status()
release = response.json()
tag_name = release['tag_name']
asset_name_exact = f"release_old3ds_{tag_name}.zip"
browserhax_io, _ = download_github_release("zoogie/old-browserhax", asset_name_exact=asset_name_exact)

with zipfile.ZipFile(browserhax_io) as z:
    for name in z.namelist():
        if name.startswith("EUROPE/") and not name.endswith('/'):
            relative_path = os.path.relpath(name, "EUROPE")
            target_path = os.path.join(TMP_DIR, relative_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with z.open(name) as source, open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)

apps_browserhax = apps_vanilla + ["Browserhax"]
generate_pack_txt("Browserhax", apps_browserhax)
vanilla_txt = os.path.join(TMP_DIR, "PACK - VANILLA.txt")
if os.path.exists(vanilla_txt):
    os.remove(vanilla_txt)
create_zip("BROWSERHAX")

# ---------------------------
# 5. MSET9.zip
clean_tmp()
with zipfile.ZipFile("LumiAIO-VANILLA.zip") as z:
    z.extractall(TMP_DIR)

api_url = "https://api.github.com/repos/zoogie/MSET9/releases/latest"
response = requests.get(api_url, headers=HEADERS)
response.raise_for_status()
release = response.json()
tag_name = release['tag_name']
asset_name_exact = f"Release_{tag_name}.zip"
mset9_io, _ = download_github_release("zoogie/MSET9", asset_name_exact=asset_name_exact)
with zipfile.ZipFile(mset9_io) as z:
    z.extractall(TMP_DIR)

apps_mset9 = apps_vanilla + ["MSET9"]
generate_pack_txt("MSET9", apps_mset9)
vanilla_txt = os.path.join(TMP_DIR, "PACK - VANILLA.txt")
if os.path.exists(vanilla_txt):
    os.remove(vanilla_txt)
create_zip("MSET9")

# ---------------------------
# Upload sur GitHub Release
GITHUB_API = "https://api.github.com"

def get_release_by_tag(repo, tag):
    url = f"{GITHUB_API}/repos/{repo}/releases/tags/{tag}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def delete_asset(asset_id):
    url = f"{GITHUB_API}/repos/{REPO}/releases/assets/{asset_id}"
    r = requests.delete(url, headers=HEADERS)
    if r.status_code == 204:
        print(f"Suppression de l'asset existant: {asset_id}")
    else:
        print(f"Erreur suppression asset {asset_id}: {r.status_code}, {r.text}")

def upload_asset(release, file_path):
    name = os.path.basename(file_path)
    upload_url = release["upload_url"].replace("{?name,label}", f"?name={name}")
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/zip"
    with open(file_path, "rb") as f:
        r = requests.post(upload_url, headers=headers, data=f)
    r.raise_for_status()
    print(f"Upload réussi: {name}")

# ---------------------------
# Récupérer la release
release = get_release_by_tag(REPO, RELEASE_TAG)

# Supprimer les assets existants
for asset in release.get("assets", []):
    delete_asset(asset["id"])

# Uploader tous les packs générés
for pack in GENERATED_PACKS:
    upload_asset(release, pack)
