import os
import re
import requests
from urllib.parse import unquote
import urllib.request
import chardet

class Channel:
    def __init__(self, name="", url="", logo="", group="", quality=""):
        self.name = name
        self.url = url
        self.logo = logo
        self.group = group
        self.quality = quality
        
    def __str__(self):
        return f"{self.name} ({self.group})"

class M3UParser:
    """Parser for M3U playlist files"""
    
    def __init__(self):
        self.channels = []
        self.groups = set()
    
    def load_from_file(self, file_path):
        """Load M3U playlist from a file"""
        try:
            # Detect file encoding to properly handle Arabic and other non-ASCII characters
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return self._parse_content(content)
        except UnicodeDecodeError as e:
            print(f"Unicode decode error: {e}. Trying with UTF-8...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self._parse_content(content)
            except Exception as e:
                print(f"Failed to load playlist: {e}")
                return False
        except Exception as e:
            print(f"Error loading playlist {file_path}: {e}")
            return False
    
    def load_from_url(self, url):
        """Load M3U playlist from a URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.text
            return self._parse_content(content)
        except Exception as e:
            print(f"Error loading playlist from URL {url}: {e}")
            return False
    
    def _parse_content(self, content):
        """Parse M3U playlist content"""
        lines = content.splitlines()
        if not lines or not lines[0].strip().startswith('#EXTM3U'):
            print("Invalid M3U format: Missing #EXTM3U header")
            return False
        
        self.channels = []
        self.groups = set()
        
        channel = None
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            
            if line.startswith('#EXTINF:'):
                # Extract channel info
                try:
                    # Extract duration and attributes
                    extinf_pattern = r'#EXTINF:(-?\d+)\s*(.*?)(?:,(.*))?$'
                    match = re.match(extinf_pattern, line)
                    if match:
                        duration = match.group(1)
                        attributes = match.group(2) or ""
                        name = match.group(3) or "Unknown"
                        
                        # Extract group-title if available
                        group_match = re.search(r'group-title="(.*?)"', attributes)
                        group = group_match.group(1) if group_match else "Unknown"
                        
                        # Extract tvg-logo if available
                        logo_match = re.search(r'tvg-logo="(.*?)"', attributes)
                        logo = logo_match.group(1) if logo_match else ""
                        
                        # Extract tvg-id if available
                        tvg_id_match = re.search(r'tvg-id="(.*?)"', attributes)
                        tvg_id = tvg_id_match.group(1) if tvg_id_match else ""
                        
                        channel = {
                            'name': name,
                            'group': group,
                            'logo': logo,
                            'tvg_id': tvg_id,
                            'duration': duration,
                            'url': None
                        }
                        
                        self.groups.add(group)
                except Exception as e:
                    print(f"Error parsing EXTINF line: {e}")
                    channel = None
            
            elif not line.startswith('#') and channel:
                # This is a URL line
                channel['url'] = line
                self.channels.append(channel)
                channel = None
        
        return True
    
    def get_channels_by_group(self, group):
        """Get channels filtered by group"""
        return [c for c in self.channels if c['group'] == group]
    
    def search_channels(self, query):
        """Search channels by name"""
        query = query.lower()
        return [c for c in self.channels if query in c['name'].lower()]
