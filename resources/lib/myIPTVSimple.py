import xbmc
import xbmcaddon
import traceback
import xbmcvfs
import os
import resources.lib.common as common
import xml.etree.ElementTree as ET

__AddonID__ = 'plugin.video.annatel.tv'
__Addon__ = xbmcaddon.Addon(__AddonID__)
__IPTVSimple__AddonDataPath____ = os.path.join(xbmcvfs.translatePath("special://userdata/addon_data"), "pvr.iptvsimple")
__AddonDataPath__ = os.path.join(xbmcvfs.translatePath("special://userdata/addon_data"), __AddonID__)

if not os.path.exists(__AddonDataPath__):
    os.makedirs(__AddonDataPath__)

def GetIptvAddon(show_message=False):
    iptvAddon = None

    try:
        iptvAddon = xbmcaddon.Addon("pvr.iptvsimple")
        if not iptvAddon.getSettingBool("enabled"):
            iptvAddon.setSettingBool("enabled", True)
            xbmc.executebuiltin('UpdateLocalAddons')
    except Exception as e:
        if show_message:
            msg1 = "PVR IPTVSimple is not installed or disabled."
            msg2 = "Please install or enable the IPTVSimple add-on."
            common.OKmsg(msg1, msg2)
        xbmc.log("Error loading IPTVSimple addon: " + str(e), level=xbmc.LOGERROR)

    return iptvAddon

def RefreshIPTVlinks(channel_list):
    iptvAddon = GetIptvAddon()
    if iptvAddon is None:
        return False

    common.ShowNotification("Updating IPTV links...", 300000, addon=__Addon__)

    try:
        finalM3Ulist = MakeM3U(channel_list)
        finalM3Ufilename = os.path.join(__AddonDataPath__, 'iptv.m3u')
        current_file = common.ReadFile(finalM3Ufilename)

        if current_file is None or finalM3Ulist != current_file:
            common.WriteFile(finalM3Ulist, finalM3Ufilename, utf8=True)
            UpdateIPTVSimpleSettings(iptvAddon, restart_pvr=True)
        else:
            UpdateIPTVSimpleSettings(iptvAddon, restart_pvr=False)
    except Exception as e:
        traceback.print_exc()
        common.ShowNotification(f"Error: {e}", 5000, addon=__Addon__)
        xbmc.log("Error updating IPTV links: " + str(e), xbmc.LOGERROR)
        return False

    common.ShowNotification("IPTV update complete.", 2000, addon=__Addon__)
    return True

def MakeM3U(channel_list, is_logo_extension=True):
    M3Ulist = ["#EXTM3U\n"]

    for item in channel_list:
        tvg_logo = GetLogo(item.tvg_logo, is_logo_extension)
        M3Ulist.append(item.GetM3uLine(tvg_logo))

    return "\n".join(M3Ulist)

def DeleteCache():
    if os.path.exists(__IPTVSimple__AddonDataPath____):
        for f in os.listdir(__IPTVSimple__AddonDataPath____):
            if f.endswith('cache'):
                os.remove(os.path.join(__IPTVSimple__AddonDataPath____, f))

def UpdateIPTVSimpleSettings(iptvAddon=None, restart_pvr=False):
    if iptvAddon is None:
        iptvAddon = GetIptvAddon()
        if iptvAddon is None:
            return

    iptvSettingsFile = os.path.join(__IPTVSimple__AddonDataPath____, "instance-settings-1.xml")
    if not os.path.isfile(iptvSettingsFile):
        iptvAddon.setSetting("epgPathType", "0")

    try:
        tree = ReadSettings(iptvSettingsFile)
    except FileNotFoundError:
        xbmc.log("Settings file not found, creating new settings file.", level=xbmc.LOGWARNING)
        tree = ET.ElementTree(ET.Element("settings"))

    newSettings = {
        "epgPathType": "0",
        "epgPath": os.path.join(__AddonDataPath__, 'epg.xml'),
        "logoPathType": "0",
        "logoPath": os.path.join(__AddonDataPath__, 'logos'),
        "m3uPathType": "0",
        "m3uPath": os.path.join(__AddonDataPath__, 'iptv.m3u'),
        "kodi_addon_instance_name": "Annatel",
    }
    ReplaceSetting(newSettings, tree, iptvSettingsFile)

    if restart_pvr:
        RefreshIPTVSimple()

def RefreshIPTVSimple():
    xbmc.executebuiltin('StartPVRManager')

def ReadSettings(source):
    try:
        tree = ET.parse(source)
    except ET.ParseError as e:
        xbmc.log("Error parsing settings file: " + str(e), level=xbmc.LOGERROR)
        tree = ET.ElementTree(ET.Element("settings"))
    return tree

def ReplaceSetting(newSettings, tree, path):
    root = tree.getroot()
    for key, value in newSettings.items():
        setting = root.find(f".//setting[@id='{key}']")
        if setting is not None:
            setting.set('value', value)
        else:
            ET.SubElement(root, "setting", id=key, value=value)
    tree.write(path)

def replaceEpgFile(epg_data):
    finalEpgFile = os.path.join(__AddonDataPath__, 'epg.xml')
    common.WriteFile(epg_data, finalEpgFile)

def GetLogo(link, is_logo_extension):
    logos_path = os.path.join(__AddonDataPath__, 'logos')
    if not os.path.exists(logos_path):
        os.makedirs(logos_path)

    if link and len(link) > 4:
        filename = os.path.basename(link)
        full_filename = os.path.join(logos_path, filename)
        if os.path.exists(full_filename) or common.DownloadFile(link, full_filename):
            return filename if is_logo_extension else filename.rsplit('.', 1)[0]
    return ""
