import requests
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import sys
import os
import urllib

from datetime import datetime, timedelta
import resources.lib.common as common

URL_TV_FEED = 'https://api-beta.annatel.tv/v1/tv/liveWithUrls'
LOGIN_URL = "https://api-beta.annatel.tv/v1/auth/signin"
AddonID = 'plugin.video.annatel.tv'
Addon = xbmcaddon.Addon(AddonID)
AddonDataPath = os.path.join(xbmcvfs.translatePath("special://userdata/addon_data"), AddonID)


class TV:
    def __init__(self, url, channel_name, tvg_id, tvg_logo=None, tvg_shift=0, group_title=None, radio=False, uid=None):
        self.url = url
        self.tvg_id = tvg_id.replace('\xe9', '\\u00e9').replace(' ', '_')
        self.tvg_name = self.tvg_id
        self.tvg_logo = tvg_logo
        self.tvg_shift = tvg_shift
        self.group_title = group_title
        self.radio = radio
        self.channel_name = channel_name
        self.uid = uid

    def GetM3uLine(self, tvg_logo):
        return '#EXTINF:-1 tvg-id="{0}" tvg-name="{1}" group-title="{2}" tvg-logo="{3}",{4}\n{5}\n'.format(
            self.uid.encode("utf-8").decode("utf-8"),
            self.tvg_name.encode("utf-8").decode("utf-8"),
            (self.group_title or "").encode("utf-8").decode("utf-8"),
            tvg_logo,
            self.channel_name.encode("utf-8").decode("utf-8"),
            self.url
        )

    def __str__(self) -> str:
        return f"TV(url={self.url}, channel_name={self.channel_name}, tvg_id={self.tvg_id}, tvg_logo={self.tvg_logo}, tvg_shift={self.tvg_shift}, group_title={self.group_title}, radio={self.radio})"


class AnnatelTv:
    token = None
    dateToken = None

    def __init__(self) -> None:
        self.GetCredentials()

    def GetCredentials(self):
        self.username = Addon.getSetting('username')
        self.password = Addon.getSetting('password')

    def IsLoggedIn(self):
        return bool(self.username) and bool(self.password)

    def GetToken(self):
        if self.token and self.dateToken and (datetime.now() - self.dateToken) < timedelta(hours=1):
            return self.token
        
        payload = {
            'login': self.username,
            'password': self.password,
            'rememberMe': 0
        }
        response = requests.post(LOGIN_URL, data=payload)
        
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get('code') == 'OK':
                self.token = json_data['data']['token']
                self.dateToken = datetime.now()
                return self.token

        raise Exception('Credentials are not valid or authentication failed.')

    def GetTVChannels(self):
        if self.IsLoggedIn():
            try:
                token = self.GetToken()
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(URL_TV_FEED, headers=headers)
                
                common.ShowNotification("TV channels loading", 10, addon=Addon)
                xbmc.log("TV channels loading", level=xbmc.LOGINFO)
                
                if response.status_code == 200:
                    json_data = response.json()
                    if json_data.get('code') == 'OK':
                        common.ShowNotification("TV channels loaded", 10, addon=Addon)
                        return self.ParseChannels(json_data['data'])
                raise Exception('Error while getting TV channels')

            except Exception as e:
                common.ShowNotification(f"Error while getting TV channels: {str(e)}", 10, addon=Addon)
                xbmc.log(str(e), level=xbmc.LOGERROR)

    def ParseChannels(self, apiResponse):
        channels = []
        for channel in apiResponse:
            channels.append(TV(
                url=channel.get('url', ''),
                channel_name=channel.get('name', 'Unknown Channel'),
                tvg_id=channel.get('name', '').replace(' ', '_'),
                tvg_logo=f"http://client.annatel.tv/images/channels/{channel.get('css_class', 'default')}.png",
                uid=channel.get('uid')
            ))
        return channels


def LoadLogin():
    message = "Il faut configurer votre login et mot de passe Annatel TV!\nCliquez sur Yes pour configurer votre login et mot de passe"
    resp = common.YesNoDialog(
        message=message,
        heading="Authentification!",
        nolabel="Non",
        yeslabel="Oui"
    )
    if resp:
        common.OpenSettings()
    else:
        common.ShowNotification(
            "Authentification!\nMerci d'entrer votre login et mot de passe Annatel TV", 10, addon=Addon
        )
