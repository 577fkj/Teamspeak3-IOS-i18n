import json
import plistlib
import zipfile
import shutil
import os

from tqdm import tqdm

infoPlist = "zh.lproj/InfoPlist.strings"
localizablePlist = "zh.lproj/Localizable.strings"

def load_translation():
    with open("IOS_Trans.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_plist(plist_path):
    with open(plist_path, 'rb') as f:
        return plistlib.load(f)

def save_plist(plist_path, plist_data):
    with open(plist_path, 'wb') as f:
        plistlib.dump(plist_data, f)

def extract_ipa(ipa_path):
    if os.path.exists("extracted"):
        shutil.rmtree("extracted")
    m_zip = zipfile.ZipFile(os.path.join(os.getcwd(), ipa_path))
    for filename in tqdm(m_zip.namelist(), desc='Extracting', unit=' file'):
        m_zip.extract(filename, os.path.join(os.getcwd(), 'extracted'))

def pack_ipa(ipa_path, output_path="extracted"):
    file_list = []
    m_zip = zipfile.ZipFile(ipa_path, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(os.path.join(output_path, 'Payload')):
        for filename in filenames:
            file_list.append(os.path.join(path, filename))

    for path in tqdm(file_list, desc='Pack', unit=' file'):
        m_zip.write(path, path[len(output_path):])

def main():
    translation = load_translation()
    localizable_plist = load_plist(localizablePlist)
    info_plist = load_plist(infoPlist)

    for key, value in info_plist.items():
        if key in translation:
            info_plist[key] = translation[key]
        else:
            translation[key] = value

    for key, value in localizable_plist.items():
        localizable_plist[key] = translation[key]

    save_plist(localizablePlist, localizable_plist)
    save_plist(infoPlist, info_plist)

    extract_ipa("TeamSpeak-3.6.7.ipa")
    shutil.copytree("zh.lproj", "extracted/Payload/TeamSpeak.app/zh.lproj")

    # copy sound
    for file in os.listdir("sound"):
        filename = file.split(".")[0]
        if os.path.exists(f"extracted/Payload/TeamSpeak.app/sound/default/{filename}.caf"):
            os.remove(f"extracted/Payload/TeamSpeak.app/sound/default/{filename}.caf")
            shutil.copyfile(f"sound/{file}", f"extracted/Payload/TeamSpeak.app/sound/default/{file}")

    pack_ipa("TeamSpeak-3.6.7-Chinese.ipa")

if __name__ == '__main__':
    main()