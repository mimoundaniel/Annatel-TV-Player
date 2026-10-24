import os
import xbmcvfs
import xbmcgui
import xbmc
import xbmcaddon
import codecs
import requests

__AddonID__ = 'plugin.video.annatel.tv'
__Addon__ = xbmcaddon.Addon(id=__AddonID__)
__AddonPath__ = xbmcvfs.translatePath(__Addon__.getAddonInfo('path'))
__AddonDataPath__ = os.path.join(xbmcvfs.translatePath(
    "special://userdata/addon_data"), __AddonID__)
__DefaultTitle__ = __Addon__.getAddonInfo('name')
__AddonIcon__ = __Addon__.getAddonInfo('icon')
__TempPath__ = os.path.join(__AddonDataPath__, "temp")
RequestTimeout = 20  # seconds


def CleanTempFolder():
    if (os.path.exists(__TempPath__)):
        for f in os.listdir(__TempPath__):
            tmpfile = os.path.join(__TempPath__, f)
            if (os.path.isfile(tmpfile)):
                os.remove(tmpfile)


def OpenSettings():
    __Addon__.openSettings()


def ShowNotification(msg, duration, title=__DefaultTitle__, addon=None, sound=False):
    """duration is in milliseconds"""
    icon = addon.getAddonInfo('icon') if addon is not None else __AddonIcon__
    dlg = xbmcgui.Dialog()
    dlg.notification(title, msg, icon, duration, sound)


def YesNoDialog(message,  heading=__DefaultTitle__, nolabel=None, yeslabel=None):
    dlg = xbmcgui.Dialog()
    response = dlg.yesno(heading, message, nolabel or "", yeslabel or "")
    return response


def OKmsg(line1, line2="", heading=__DefaultTitle__):
    dlg = xbmcgui.Dialog()
    dlg.ok(heading, f"{line1}\n{line2}".strip())


def DownloadFile(url, filePath):
    """Returns True when the file was downloaded"""
    try:
        response = requests.get(url, timeout=RequestTimeout)
    except requests.RequestException as e:
        xbmc.log(f'Failed to download {url}: {e}', level=xbmc.LOGERROR)
        return False

    if response.status_code != 200:
        xbmc.log(
            f'Failed to download image. Status code: {response.status_code} link:{url}', level=xbmc.LOGERROR)
        return False

    directory = os.path.dirname(filePath)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filePath, 'wb+') as f:
        f.write(response.content)
    return True


def ReadFile(file_path):
    text = None
    if (os.path.exists(file_path)):
        with codecs.open(file_path, "r", encoding='utf-8') as openFile:
            text = openFile.read()
    return text


def WriteFile(text, file_path, utf8=False):
    if (text is not None):
        local_dir = os.path.dirname(file_path)
        if (not os.path.exists(local_dir)):
            os.makedirs(local_dir)

        with codecs.open(file_path, "w+", encoding='utf-8') as openFile:
            openFile.write(text)

    else:
        DeleteFile(file_path)


def DeleteFile(file_path):
    if (os.path.exists(file_path)):
        os.remove(file_path)
