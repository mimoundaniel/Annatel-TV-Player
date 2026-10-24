import resources.lib.myIPTVSimple as myIPTVSimple
from resources.lib.annatel import AnnatelTv, LoadLogin
import resources.lib.common as common
import threading
import xbmc
from resources.lib.epgParser import EpgParser
import traceback

tvThread = None
tvCounter = 0

UpdateInterval = 4 * 3600  # 4 hours
LoginInterval = 5  # 5 seconds
RetryInterval = 5 * 60  # 5 minutes
WaitInterval = 5  # 5 seconds


class Monitor(xbmc.Monitor):
    def onSettingsChanged(self):
        # New credentials: reload them and refresh the channels right away
        global tvCounter
        annatel.GetCredentials()
        tvCounter = 0


annatel = AnnatelTv()
monitor = Monitor()


def OnLoad() -> None:
    global tvCounter
    try:
        common.CleanTempFolder()
    except Exception as e:
        xbmc.log("Error cleaning temp folder: " + str(e), level=xbmc.LOGERROR)

    if not annatel.IsLoggedIn():
        LoadLogin()
    else:
        tvCounter = 0
        myIPTVSimple.GetIptvAddon(show_message=True)


def OnExit() -> None:
    global tvThread
    if tvThread is not None:
        tvThread.join()
        tvThread = None


def CanUpdate() -> bool:
    return not monitor.abortRequested() and annatel.IsLoggedIn() and myIPTVSimple.GetIptvAddon() is not None


def CheckUpdates() -> None:
    global tvCounter
    global tvThread
    while CanUpdate():
        tvCounter -= WaitInterval
        if tvCounter <= 0 and tvThread is None:
            tvCounter = UpdateInterval
            tvThread = threading.Thread(target=UpdateTVChannels)
            tvThread.start()
        if monitor.waitForAbort(WaitInterval):
            break


def UpdateTVChannels() -> None:
    global tvCounter
    global tvThread
    result = False
    try:
        channels_list = annatel.GetTVChannels()
        if channels_list:
            myIPTVSimple.RefreshIPTVlinks(channels_list)
            UpdateEpg(list(map(lambda x: x.uid, channels_list)))
            common.ShowNotification(f"{len(channels_list)} chaînes à jour", 5000)
            result = True

    except Exception as e:
        xbmc.log("Error: " + str(e), level=xbmc.LOGERROR)
        traceback.print_exc()
        result = False
    if result:
        tvCounter = UpdateInterval
    else:
        tvCounter = RetryInterval
    tvThread = None


def UpdateEpg(channel_list) -> None:
    try:
        epgParser = EpgParser(token=annatel.GetToken(), channels_ids=channel_list)
        data = epgParser.getChannelsData()
        if data:
            myIPTVSimple.replaceEpgFile(data)
            xbmc.log("---- Annatel ---- EPG updated", level=xbmc.LOGINFO)

    except Exception as e:
        xbmc.log("Error: " + str(e), level=xbmc.LOGERROR)
        traceback.print_exc()


OnLoad()
while not monitor.abortRequested():
    if CanUpdate():
        CheckUpdates()
    elif monitor.waitForAbort(LoginInterval):
        break
OnExit()
