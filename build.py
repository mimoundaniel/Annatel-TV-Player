"""Builds the add-on zips and the Kodi repository served by GitHub Pages from docs/.

Usage: python build.py
"""
import hashlib
import os
import re
import shutil
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, 'docs')
ADDON_ID = 'plugin.video.annatel.tv'
ADDON_FILES = ['addon.py', 'addon.xml', 'icon.jpeg', 'fanart.jpeg', 'resources']
REPO_ID = 'repository.annatel'
IGNORED = ('.DS_Store', '__pycache__', '.pyc')


def read_version(addon_xml):
    with open(addon_xml, encoding='utf-8') as f:
        return re.search(r'<addon[^>]*\sversion="([^"]+)"', f.read()).group(1)


def zip_addon(addon_id, source_dir, files):
    version = read_version(os.path.join(source_dir, 'addon.xml'))
    out_dir = os.path.join(DOCS, addon_id)
    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, f'{addon_id}-{version}.zip')
    # Kodi needs the folder inside the zip to be named after the add-on id
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in files:
            path = os.path.join(source_dir, name)
            walk = os.walk(path) if os.path.isdir(path) else [(source_dir, [], [name])]
            for folder, dirs, filenames in walk:
                dirs[:] = [d for d in dirs if d not in IGNORED]
                for filename in filenames:
                    if filename.endswith(IGNORED):
                        continue
                    full = os.path.join(folder, filename)
                    z.write(full, os.path.join(addon_id, os.path.relpath(full, source_dir)))
    for asset in ('icon.jpeg', 'fanart.jpeg'):
        if os.path.exists(os.path.join(source_dir, asset)):
            shutil.copy(os.path.join(source_dir, asset), out_dir)
    print('built', os.path.relpath(zip_path, ROOT))
    return zip_path


def addon_xml_body(addon_xml):
    with open(addon_xml, encoding='utf-8') as f:
        return re.sub(r'<\?xml[^>]*\?>', '', f.read()).strip()


def main():
    if os.path.exists(DOCS):
        shutil.rmtree(DOCS)
    os.makedirs(DOCS)
    repo_dir = os.path.join(ROOT, REPO_ID)
    addon_zip = zip_addon(ADDON_ID, ROOT, ADDON_FILES)
    repo_zip = zip_addon(REPO_ID, repo_dir, ['addon.xml', 'icon.jpeg'])

    addons = [addon_xml_body(os.path.join(ROOT, 'addon.xml')),
              addon_xml_body(os.path.join(repo_dir, 'addon.xml'))]
    addons_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n' + '\n\n'.join(addons) + '\n</addons>\n'
    with open(os.path.join(DOCS, 'addons.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(addons_xml)
    with open(os.path.join(DOCS, 'addons.xml.md5'), 'w') as f:
        f.write(hashlib.md5(addons_xml.encode('utf-8')).hexdigest())

    # Kodi's file manager lists an http source from the links on its index page
    links = [os.path.relpath(p, DOCS).replace(os.sep, '/') for p in (repo_zip, addon_zip)]
    with open(os.path.join(DOCS, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>Annatel TV pour Kodi</title></head><body>\n')
        f.writelines(f'<a href="{link}">{os.path.basename(link)}</a><br>\n' for link in links)
        f.write('</body></html>\n')
    open(os.path.join(DOCS, '.nojekyll'), 'w').close()


if __name__ == '__main__':
    main()
