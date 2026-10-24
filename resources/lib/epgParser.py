import xbmc
import requests
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape, quoteattr
import traceback

_EPG_URL_ = 'https://api-beta.annatel.tv/v1/epg/program'
_EPG_DAYS_ = 2  # today and tomorrow, so the guide does not stop at midnight
RequestTimeout = 20  # seconds


class EpgParser:
    def __init__(self, token: str, channels_ids: list):
        self.token = token
        self.channels_ids = channels_ids

    def getChannelsData(self):
        """Fetch and parse EPG data for the provided channel IDs."""
        channels_data = {}
        xbmc.log("---- Annatel ---- Starting to fetch EPG data", xbmc.LOGINFO)
        today = datetime.now(timezone.utc)
        dates = [(today + timedelta(days=d)).strftime('%Y-%m-%d') for d in range(_EPG_DAYS_)]
        for channel_id in self.channels_ids:
            programmes = []
            for date in dates:
                programmes.extend(self.GetProgramByDate(channel_id, date))
            if programmes:
                channels_data[channel_id] = programmes
            else:
                xbmc.log(f"---- Annatel ---- No data found for channel {channel_id}", xbmc.LOGWARNING)

        return self.parseEpg(channels_data)

    def generateHeader(self):
        return '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv>'''

    def generateChannel(self, channel_id):
        return f'''<channel id={quoteattr(channel_id)}>
    <display-name>{escape(channel_id)}</display-name>
</channel>'''

    def formatTime(self, timestamp):
        return datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y%m%d%H%M%S +0000')

    def generateProgramme(self, channel_id, programme):
        start = self.formatTime(programme['start'])
        stop = self.formatTime(programme['stop'])
        title = escape(programme.get('title') or 'No Title')
        description = escape(programme.get('description') or '')
        image = programme.get('image')
        category = escape(programme.get('category') or '')

        lines = [f'<programme start="{start}" stop="{stop}" channel={quoteattr(channel_id)}>',
                 f'    <title lang="fr">{title}</title>']
        if description:
            lines.append(f'    <desc lang="fr">{description}</desc>')
        if category:
            lines.append(f'    <category lang="fr">{category}</category>')
        if image:
            lines.append(f'    <icon src={quoteattr(programme["image"])} />')
        lines.append('</programme>')
        return '\n'.join(lines)

    def parseEpg(self, channels):
        """Parse {channel uid: [programmes]} into XMLTV format.

        Channels are identified by the uid used as tvg-id in the M3U file,
        so IPTV Simple can match each programme to its channel."""
        try:
            epg = [self.generateHeader()]
            epg.extend([self.generateChannel(channel_id) for channel_id in channels])

            seen = set()
            for channel_id, programmes in channels.items():
                for programme in programmes:
                    if 'start' not in programme or 'stop' not in programme:
                        continue
                    key = (channel_id, programme['start'])
                    if key in seen:
                        continue
                    seen.add(key)
                    epg.append(self.generateProgramme(channel_id, programme))
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
            response = requests.get(_EPG_URL_, headers=headers, params=params, timeout=RequestTimeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 'OK':
                    return data.get('data') or []
                else:
                    xbmc.log(f"---- Annatel ---- API response error for channel {channel_id}: {data.get('message')}", xbmc.LOGWARNING)
            else:
                xbmc.log(f"---- Annatel ---- HTTP error {response.status_code} for channel {channel_id}", xbmc.LOGWARNING)
        except (requests.RequestException, ValueError) as e:
            xbmc.log(f"---- Annatel ---- Request exception for channel {channel_id}: {str(e)}", xbmc.LOGERROR)
        return []
