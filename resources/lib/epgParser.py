import xbmc
import xbmcaddon
import resources.lib.common as common
import requests
from datetime import datetime, timedelta
import traceback

__AddonID__ = 'plugin.video.annatel.tv'
__Addon__ = xbmcaddon.Addon(__AddonID__)
_EPG_URL_ = 'https://api-beta.annatel.tv/v1/epg/program'


class EpgParser:
    def __init__(self, token: str, channels_ids: list):
        self.token = token
        self.channels_ids = channels_ids

    def getChannelsData(self):
        """Fetch and parse EPG data for the provided channel IDs."""
        channels_data = []
        xbmc.log("---- Annatel ---- Starting to fetch EPG data", xbmc.LOGINFO)
        current_date = datetime.utcnow().strftime('%Y-%m-%d')  # Use UTC
        for channel_id in self.channels_ids:
            channel_data = self.GetProgramByDate(channel_id, current_date)
            if channel_data:
                channels_data.extend(channel_data)
            else:
                xbmc.log(f"---- Annatel ---- No data found for channel {channel_id}", xbmc.LOGWARNING)

        return self.parseEpg(channels_data)

    def generateHeader(self):
        return '''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE tv SYSTEM "xmltv.dtd">
        <tv>'''

    def generateChannel(self, xmltv_id):
        channel_name = xmltv_id.split('.')[0] if xmltv_id else "Unknown Channel"
        return f'''<channel id="{xmltv_id}">
             <display-name>{channel_name}</display-name>
        </channel>'''

    def generateProgramme(self, channel):
        start = datetime.utcfromtimestamp(channel['start']).strftime('%Y%m%d%H%M%S +0000')
        stop = datetime.utcfromtimestamp(channel['stop']).strftime('%Y%m%d%H%M%S +0000')
        title = channel.get('title', 'No Title')
        description = channel.get('description', 'No Description')
        image = channel.get('image', '')
        category = channel.get('category', 'Uncategorized')
        
        return f'''<programme start="{start}" stop="{stop}" channel="{channel['xmltv_id']}">
        <title lang="en">{title}</title>
            <desc lang="en">{description}</desc>
            <image type="poster" size="1" orient="P" system="tvdb">{image}</image>
            <category lang="en">{category}</category>
        </programme>'''

    def parseEpg(self, channels):
        """Parse the list of channels data into XMLTV format."""
        try:
            epg = [self.generateHeader()]
            unique_channels = set(channel['xmltv_id'] for channel in channels if 'xmltv_id' in channel)

            # Add channels to EPG
            epg.extend([self.generateChannel(channel_id) for channel_id in unique_channels])

            # Add programs to EPG
            epg.extend([self.generateProgramme(channel) for channel in channels])
            epg.append('</tv>')
            return '\n'.join(epg).replace('\r', '')
        except Exception as e:
            xbmc.log(f"---- Annatel ---- Error parsing EPG data: {str(e)}", xbmc.LOGERROR)
            traceback.print_exc()

    def GetHeaders(self):
        return {'Authorization': f'Bearer {self.token}'}

    def GetProgramByDate(self, channel_id, date):
        """Fetch program data for a specific channel and date."""
        headers = self.GetHeaders()
        params = {'uid': channel_id, 'date': date}
        try:
            response = requests.get(_EPG_URL_, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 'OK':
                    return data.get('data', [])
                else:
                    xbmc.log(f"---- Annatel ---- API response error for channel {channel_id}: {data.get('message')}", xbmc.LOGWARNING)
            else:
                xbmc.log(f"---- Annatel ---- HTTP error {response.status_code} for channel {channel_id}", xbmc.LOGWARNING)
        except requests.RequestException as e:
            xbmc.log(f"---- Annatel ---- Request exception for channel {channel_id}: {str(e)}", xbmc.LOGERROR)
            traceback.print_exc()
        return []
