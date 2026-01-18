import aiohttp
import aiofiles
import os
from urllib.parse import urlparse
import yt_dlp
from bot.config import Config

class Leecher:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def detect_site(self, url):
        """Detect which site the URL belongs to"""
        url_lower = url.lower()
        for site in Config.LEECH_SITES:
            if site in url_lower:
                return site
        return None
    
    async def download_youtube(self, url, progress_callback=None):
        """Download from YouTube/Instagram using yt-dlp"""
        output_path = os.path.join(Config.STORAGE_PATH, "%(title)s.%(ext)s")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'progress_hooks': [progress_callback] if progress_callback else [],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return {
                    'success': True,
                    'filename': filename,
                    'title': info.get('title'),
                    'size': info.get('filesize', 0)
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def download_direct(self, url, filename=None, progress_callback=None):
        """Download from direct link"""
        session = await self.get_session()
        
        if not filename:
            filename = os.path.basename(urlparse(url).path) or "downloaded_file"
        
        filepath = os.path.join(Config.STORAGE_PATH, filename)
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return {'success': False, 'error': f'HTTP {response.status}'}
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                async with aiofiles.open(filepath, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 64):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size:
                            progress = (downloaded / total_size) * 100
                            await progress_callback(downloaded, total_size, progress)
                
                return {
                    'success': True,
                    'filename': filepath,
                    'size': downloaded
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def download_from_url(self, url, progress_callback=None):
        """Main download function - auto-detect and download"""
        site = await self.detect_site(url)
        
        if not site:
            return {'success': False, 'error': 'Unsupported site bhai 😕'}
        
        # YouTube/Instagram
        if 'youtube' in site or 'youtu.be' in site or 'instagram' in site:
            return await self.download_youtube(url, progress_callback)
        
        # For other sites (Terabox, Hubdrive, etc.)
        # You'll need specific extractors or APIs
        # For now, treating as direct download
        return await self.download_direct(url, progress_callback=progress_callback)

leecher = Leecher()
