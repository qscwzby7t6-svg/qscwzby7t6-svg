"""
真实音乐API集成模块
支持：QQ音乐、网易云音乐等真实API
"""
import hashlib
import time
import random
import base64
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

import requests
import yaml

from src.config import settings


@dataclass
class RealSongInfo:
    """真实歌曲信息"""
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[int] = None
    genre: Optional[List[str]] = None
    cover_url: Optional[str] = None
    play_count: Optional[int] = None
    release_date: Optional[str] = None
    source: Optional[str] = None
    audio_url: Optional[str] = None
    lyrics_url: Optional[str] = None


class MusicAPIIntegration:
    """音乐API集成基类"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = ""
    
    def search_song(self, keyword: str, limit: int = 10) -> List[RealSongInfo]:
        """搜索歌曲"""
        raise NotImplementedError
    
    def get_song_detail(self, song_id: str) -> Optional[RealSongInfo]:
        """获取歌曲详情"""
        raise NotImplementedError
    
    def get_song_url(self, song_id: str) -> Optional[str]:
        """获取歌曲播放链接"""
        raise NotImplementedError


class QQMusicAPI(MusicAPIIntegration):
    """QQ音乐API集成"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__(api_key, api_secret)
        self.base_url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
        self.lyrics_url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
    
    def _generate_guid(self):
        """生成GUID"""
        return f"{random.randint(100000000, 999999999)}.{int(time.time() * 1000)}"
    
    def search_song(self, keyword: str, limit: int = 10) -> List[RealSongInfo]:
        """
        搜索QQ音乐歌曲
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            歌曲列表
        """
        try:
            params = {
                'w': keyword,
                'format': 'json',
                'p': 1,
                'n': limit
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                songs = []
                
                for item in data.get('data', {}).get('song', {}).get('list', []):
                    song = RealSongInfo(
                        id=str(item.get('songid', '')),
                        title=item.get('songname', ''),
                        artist=','.join([s.get('name', '') for s in item.get('singer', [])]),
                        album=item.get('albumname', ''),
                        duration=item.get('interval', 0) * 1000,
                        source='qqmusic',
                        audio_url=self._generate_audio_url(item.get('songmid', '')),
                        lyrics_url=self._generate_lyrics_url(item.get('songmid', ''))
                    )
                    songs.append(song)
                
                return songs
            
        except Exception as e:
            print(f"QQ音乐搜索失败: {e}")
        
        return []
    
    def _generate_audio_url(self, song_mid: str) -> str:
        """生成音频URL"""
        guid = self._generate_guid()
        url = f"https://dl.stream.qqmusic.qq.com/{song_mid}.m4a?guid={guid}&vkey={self.api_key or ''}&uin=0&fromtag=66"
        return url
    
    def _generate_lyrics_url(self, song_mid: str) -> str:
        """生成歌词URL"""
        return f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?songmid={song_mid}&format=json"


class NetEaseMusicAPI(MusicAPIIntegration):
    """网易云音乐API集成"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__(api_key, api_secret)
        self.base_url = "https://music.163.com/api/search/get"
        self.detail_url = "https://music.163.com/api/song/detail"
    
    def _generate_encryption_key(self):
        """生成加密密钥"""
        return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 16))
    
    def search_song(self, keyword: str, limit: int = 10) -> List[RealSongInfo]:
        """
        搜索网易云音乐歌曲
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            歌曲列表
        """
        try:
            data = {
                's': keyword,
                'type': 1,
                'limit': limit,
                'offset': 0,
                'csrf_token': ''
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://music.163.com'
            }
            
            response = requests.post(
                self.base_url,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                songs = []
                
                for item in data.get('result', {}).get('songs', []):
                    song = RealSongInfo(
                        id=str(item.get('id', '')),
                        title=item.get('name', ''),
                        artist=','.join([a.get('name', '') for a in item.get('artists', [])]),
                        album=item.get('album', {}).get('name', '') if item.get('album') else '',
                        duration=item.get('duration', 0),
                        source='netease',
                        audio_url=f"https://music.163.com/song/media/outer/url?id={item.get('id', '')}.mp3",
                        lyrics_url=f"https://music.163.com/api/song/lyric?id={item.get('id', '')}&lv=1&kv=1&tv=-1"
                    )
                    songs.append(song)
                
                return songs
            
        except Exception as e:
            print(f"网易云音乐搜索失败: {e}")
        
        return []


class MusicAPIFacade:
    """音乐API统一入口"""
    
    def __init__(self):
        self.qqmusic = QQMusicAPI()
        self.netease = NetEaseMusicAPI()
    
    def search_all(self, keyword: str, limit: int = 20) -> List[RealSongInfo]:
        """
        从所有平台搜索歌曲
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            合并后的歌曲列表
        """
        all_songs = []
        
        # 并行搜索
        qq_songs = self.qqmusic.search_song(keyword, limit // 2)
        netease_songs = self.netease.search_song(keyword, limit // 2)
        
        all_songs.extend(qq_songs)
        all_songs.extend(netease_songs)
        
        # 去重
        seen = set()
        unique_songs = []
        for song in all_songs:
            if song.id not in seen:
                seen.add(song.id)
                unique_songs.append(song)
        
        return unique_songs[:limit]
    
    def get_platform_songs(self, platform: str, keyword: str, limit: int = 10) -> List[RealSongInfo]:
        """
        从指定平台搜索歌曲
        
        Args:
            platform: 平台名称 ('qqmusic' 或 'netease')
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            歌曲列表
        """
        if platform == 'qqmusic':
            return self.qqmusic.search_song(keyword, limit)
        elif platform == 'netease':
            return self.netease.search_song(keyword, limit)
        else:
            return []


# 全局实例
music_api_facade = MusicAPIFacade()
