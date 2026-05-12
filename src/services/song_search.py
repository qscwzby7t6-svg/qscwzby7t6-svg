"""
歌曲搜索与元数据获取模块
"""
import os
import uuid
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.config import settings
from src.models import db_manager


@dataclass
class SongInfo:
    """歌曲信息"""
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    cover_url: Optional[str] = None
    duration: Optional[int] = None
    genre: Optional[List[str]] = None
    release_date: Optional[str] = None
    play_count: Optional[int] = None  # 播放量
    trend_score: Optional[float] = None  # 热度分数


class SongSearchService:
    """歌曲搜索服务"""
    
    def __init__(self):
        # 模拟的歌曲数据库，实际项目中可以替换为真实的音乐API
        self._mock_songs = self._init_mock_songs()
    
    def _init_mock_songs(self) -> List[Dict[str, Any]]:
        """初始化模拟歌曲数据（包含播放量和热度）"""
        return [
            {
                'id': 'song_001',
                'title': '夜曲',
                'artist': '周杰伦',
                'album': '十一月的肖邦',
                'duration': 225,
                'genre': ['pop', 'r&b'],
                'release_date': '2005-11-01',
                'play_count': 158000000,
                'trend_score': 95.5
            },
            {
                'id': 'song_002',
                'title': '晴天',
                'artist': '周杰伦',
                'album': '叶惠美',
                'duration': 269,
                'genre': ['pop', 'rock'],
                'release_date': '2003-07-31',
                'play_count': 210000000,
                'trend_score': 98.2
            },
            {
                'id': 'song_003',
                'title': '稻香',
                'artist': '周杰伦',
                'album': '魔杰座',
                'duration': 223,
                'genre': ['pop', 'folk'],
                'release_date': '2008-10-15',
                'play_count': 95000000,
                'trend_score': 88.3
            },
            {
                'id': 'song_004',
                'title': '七里香',
                'artist': '周杰伦',
                'album': '七里香',
                'duration': 299,
                'genre': ['pop'],
                'release_date': '2004-08-03',
                'play_count': 185000000,
                'trend_score': 96.8
            },
            {
                'id': 'song_005',
                'title': '青花瓷',
                'artist': '周杰伦',
                'album': '我很忙',
                'duration': 239,
                'genre': ['chinese style', 'pop'],
                'release_date': '2007-11-02',
                'play_count': 256000000,
                'trend_score': 99.1
            },
            {
                'id': 'song_006',
                'title': '演员',
                'artist': '薛之谦',
                'album': '绅士',
                'duration': 330,
                'genre': ['pop', 'ballad'],
                'release_date': '2015-05-20',
                'play_count': 167000000,
                'trend_score': 94.6
            },
            {
                'id': 'song_007',
                'title': '告白气球',
                'artist': '周杰伦',
                'album': '周杰伦的床边故事',
                'duration': 215,
                'genre': ['pop'],
                'release_date': '2016-06-24',
                'play_count': 198000000,
                'trend_score': 97.5
            },
            {
                'id': 'song_008',
                'title': '光年之外',
                'artist': '邓紫棋',
                'album': '光年之外',
                'duration': 235,
                'genre': ['pop', 'electronic'],
                'release_date': '2016-12-30',
                'play_count': 312000000,
                'trend_score': 99.8
            },
            {
                'id': 'song_009',
                'title': '起风了',
                'artist': '买辣椒也用券',
                'album': '起风了',
                'duration': 325,
                'genre': ['pop', 'folk'],
                'release_date': '2017-02-22',
                'play_count': 145000000,
                'trend_score': 92.4
            },
            {
                'id': 'song_010',
                'title': '说散就散',
                'artist': '袁娅维',
                'album': '前任3：再见前任 电影原声带',
                'duration': 256,
                'genre': ['pop', 'ballad'],
                'release_date': '2017-12-10',
                'play_count': 138000000,
                'trend_score': 91.2
            },
            {
                'id': 'song_011',
                'title': '漠河舞厅',
                'artist': '柳爽',
                'album': '漠河舞厅',
                'duration': 263,
                'genre': ['folk', 'pop'],
                'release_date': '2020-06-15',
                'play_count': 420000000,
                'trend_score': 99.9
            },
            {
                'id': 'song_012',
                'title': '孤勇者',
                'artist': '陈奕迅',
                'album': '孤勇者',
                'duration': 226,
                'genre': ['pop', 'rock'],
                'release_date': '2021-11-08',
                'play_count': 510000000,
                'trend_score': 99.95
            },
            {
                'id': 'song_013',
                'title': '本草纲目',
                'artist': '周杰伦',
                'album': '依然范特西',
                'duration': 290,
                'genre': ['pop', 'chinese style', 'rap'],
                'release_date': '2006-09-05',
                'play_count': 178000000,
                'trend_score': 93.8
            },
            {
                'id': 'song_014',
                'title': '野狼disco',
                'artist': '宝石Gem',
                'album': '野狼disco',
                'duration': 230,
                'genre': ['rap', 'pop'],
                'release_date': '2019-09-02',
                'play_count': 298000000,
                'trend_score': 98.7
            },
            {
                'id': 'song_015',
                'title': '后来',
                'artist': '刘若英',
                'album': '我等你',
                'duration': 339,
                'genre': ['pop', 'ballad'],
                'release_date': '1999-01-01',
                'play_count': 165000000,
                'trend_score': 90.5
            }
        ]
    
    # 音乐分类列表
    MUSIC_GENRES = [
        '全部',
        '流行音乐',
        '摇滚',
        '民谣',
        'R&B',
        '电子音乐',
        '中国风',
        '说唱',
        '抒情'
    ]
    
    # 歌曲命名关键词库
    SONG_NAME_KEYWORDS = {
        'pop': ['心动', '爱情', '甜蜜', '时光', '遇见', '思念', '约定', '星光'],
        'rock': ['疯狂', '梦想', '力量', '燃烧', '自由', '叛逆', '嘶吼', '狂野'],
        'folk': ['故乡', '远方', '流浪', '岁月', '时光', '田野', '小溪', '炊烟'],
        'ballad': ['寂寞', '孤独', '回忆', '眼泪', '错过', '遗憾', '等待', '思念'],
        'electronic': ['未来', '科技', '霓虹', '赛博', '迷幻', '电子', '脉冲', '数字'],
        'chinese style': ['江南', '山水', '古风', '明月', '落花', '烟雨', '红尘', '江湖'],
        'rap': ['节奏', '态度', '态度', '说唱', '嘻哈', '街头', '态度', '自由'],
        'r&b': ['灵魂', '蓝调', '温柔', '浪漫', '深情', '律动', 'R&B', '节奏'],
        'default': ['旋律', '音符', '歌声', '乐章', '交响', '节拍', '和声', '曲调']
    }
    
    def get_song_by_rank(self, rank: int) -> Optional[SongInfo]:
        """
        根据播放量排名获取歌曲
        
        Args:
            rank: 排名（从1开始）
            
        Returns:
            指定排名的歌曲信息
        """
        if rank < 1:
            return None
        
        # 按播放量降序排序
        sorted_songs = sorted(
            self._mock_songs,
            key=lambda x: x.get('play_count', 0),
            reverse=True
        )
        
        if rank > len(sorted_songs):
            # 如果排名超出范围，返回最后一首
            rank = len(sorted_songs)
        
        song = sorted_songs[rank - 1]
        db_manager.save_song(song)
        
        return SongInfo(
            id=song['id'],
            title=song['title'],
            artist=song['artist'],
            album=song.get('album'),
            cover_url=song.get('cover_url'),
            duration=song.get('duration'),
            genre=song.get('genre'),
            release_date=song.get('release_date'),
            play_count=song.get('play_count'),
            trend_score=song.get('trend_score')
        )
    
    def generate_song_name(self, style_features: Dict[str, Any]) -> str:
        """
        根据风格特征自动生成歌曲名称
        
        Args:
            style_features: 风格特征
            
        Returns:
            自动生成的歌曲名称
        """
        import random
        
        # 获取流派信息
        genres = style_features.get('genre', [])
        bpm = style_features.get('bpm', 120)
        
        # 确定主要风格
        primary_style = 'default'
        if genres:
            genre_str = ' '.join(genres).lower()
            for style_key in self.SONG_NAME_KEYWORDS.keys():
                if style_key in genre_str:
                    primary_style = style_key
                    break
        
        # 根据BPM调整风格
        if bpm > 140 and primary_style == 'default':
            primary_style = 'rock'
        elif bpm < 100 and primary_style == 'default':
            primary_style = 'ballad'
        
        # 随机选择名称
        keywords = self.SONG_NAME_KEYWORDS.get(primary_style, self.SONG_NAME_KEYWORDS['default'])
        keyword = random.choice(keywords)
        
        # 生成歌曲名称
        name_templates = [
            f"《{keyword}》",
            f"《{keyword}的夜》",
            f"《{keyword}时光》",
            f"《{keyword}之歌》",
            f"《夜空中最闪亮的{keyword}》",
            f"《{keyword}与星辰》",
            f"《致{keyword}》",
            f"《{keyword}的旋律》",
            f"《追寻{keyword}》",
            f"《{keyword}在路上》"
        ]
        
        return random.choice(name_templates)
    
    def search_song(self, title: str, artist: Optional[str] = None) -> List[SongInfo]:
        """
        搜索歌曲
        
        Args:
            title: 歌曲标题
            artist: 艺术家名称（可选）
            
        Returns:
            匹配的歌曲列表
        """
        results = []
        title_lower = title.lower()
        
        for song in self._mock_songs:
            # 检查标题匹配
            if title_lower in song['title'].lower():
                # 如果指定了艺术家，也检查艺术家匹配
                if artist and artist.lower() not in song['artist'].lower():
                    continue
                
                # 保存到数据库
                db_manager.save_song(song)
                
                results.append(SongInfo(
                    id=song['id'],
                    title=song['title'],
                    artist=song['artist'],
                    album=song.get('album'),
                    cover_url=song.get('cover_url'),
                    duration=song.get('duration'),
                    genre=song.get('genre'),
                    release_date=song.get('release_date'),
                    play_count=song.get('play_count'),
                    trend_score=song.get('trend_score')
                ))
        
        # 如果没有找到匹配，也尝试只按艺术家搜索
        if not results and artist:
            for song in self._mock_songs:
                if artist.lower() in song['artist'].lower():
                    db_manager.save_song(song)
                    results.append(SongInfo(
                        id=song['id'],
                        title=song['title'],
                        artist=song['artist'],
                        album=song.get('album'),
                        cover_url=song.get('cover_url'),
                        duration=song.get('duration'),
                        genre=song.get('genre'),
                        release_date=song.get('release_date'),
                        play_count=song.get('play_count'),
                        trend_score=song.get('trend_score')
                    ))
        
        return results
    
    def get_song_by_id(self, song_id: str) -> Optional[SongInfo]:
        """
        根据ID获取歌曲信息
        
        Args:
            song_id: 歌曲ID
            
        Returns:
            歌曲信息，如果没有找到则返回None
        """
        # 先从数据库查找
        db_song = db_manager.get_song(song_id)
        if db_song:
            return SongInfo(
                id=db_song['id'],
                title=db_song['title'],
                artist=db_song['artist'],
                album=db_song.get('album'),
                cover_url=db_song.get('cover_url'),
                duration=db_song.get('duration'),
                genre=db_song.get('genre'),
                release_date=db_song.get('release_date'),
                play_count=db_song.get('play_count'),
                trend_score=db_song.get('trend_score')
            )
        
        # 从模拟数据查找
        for song in self._mock_songs:
            if song['id'] == song_id:
                db_manager.save_song(song)
                return SongInfo(
                    id=song['id'],
                    title=song['title'],
                    artist=song['artist'],
                    album=song.get('album'),
                    cover_url=song.get('cover_url'),
                    duration=song.get('duration'),
                    genre=song.get('genre'),
                    release_date=song.get('release_date'),
                    play_count=song.get('play_count'),
                    trend_score=song.get('trend_score')
                )
        
        return None
    
    def get_audio_sample(self, song_id: str) -> Optional[Path]:
        """
        获取歌曲音频样本
        
        Args:
            song_id: 歌曲ID
            
        Returns:
            音频文件路径，如果没有找到则返回None
        """
        # 在实际项目中，这里应该从音乐API获取音频样本
        # 这里我们返回None，在后面的模块中我们会提供测试音频文件
        # 或者允许用户上传自己的音频文件
        
        # 检查本地是否有该歌曲的音频文件
        audio_dir = settings.AUDIO_DIR
        for ext in ['.wav', '.mp3', '.flac']:
            audio_path = audio_dir / f"{song_id}{ext}"
            if audio_path.exists():
                return audio_path
        
        return None
    
    def get_all_songs(self) -> List[SongInfo]:
        """获取所有可用的歌曲"""
        return [
            SongInfo(
                id=song['id'],
                title=song['title'],
                artist=song['artist'],
                album=song.get('album'),
                cover_url=song.get('cover_url'),
                duration=song.get('duration'),
                genre=song.get('genre'),
                release_date=song.get('release_date'),
                play_count=song.get('play_count'),
                trend_score=song.get('trend_score')
            )
            for song in self._mock_songs
        ]
    
    def get_top_trending_songs(self, limit: int = 10) -> List[SongInfo]:
        """
        获取全网播放量最高的歌曲（网红歌曲自动搜索）
        
        Args:
            limit: 返回数量限制
            
        Returns:
            按播放量降序排列的歌曲列表
        """
        # 按播放量降序排序
        sorted_songs = sorted(
            self._mock_songs,
            key=lambda x: x.get('play_count', 0),
            reverse=True
        )[:limit]
        
        results = []
        for song in sorted_songs:
            db_manager.save_song(song)
            results.append(SongInfo(
                id=song['id'],
                title=song['title'],
                artist=song['artist'],
                album=song.get('album'),
                cover_url=song.get('cover_url'),
                duration=song.get('duration'),
                genre=song.get('genre'),
                release_date=song.get('release_date'),
                play_count=song.get('play_count'),
                trend_score=song.get('trend_score')
            ))
        
        return results
    
    def get_top_songs_by_genre(self, genre: str, limit: int = 10) -> List[SongInfo]:
        """
        按分类获取播放量最高的歌曲
        
        Args:
            genre: 音乐分类（如：流行音乐、摇滚、民谣等）
            limit: 返回数量限制
            
        Returns:
            按播放量降序排列的该分类歌曲列表
        """
        # 分类映射
        genre_mapping = {
            '全部': None,
            '流行音乐': ['pop'],
            '摇滚': ['rock'],
            '民谣': ['folk'],
            'R&B': ['r&b'],
            '电子音乐': ['electronic'],
            '中国风': ['chinese style'],
            '说唱': ['rap'],
            '抒情': ['ballad']
        }
        
        target_genres = genre_mapping.get(genre)
        
        # 筛选符合分类的歌曲
        filtered_songs = []
        for song in self._mock_songs:
            song_genres = [g.lower() for g in song.get('genre', [])]
            
            if target_genres is None:
                # 全部分类
                filtered_songs.append(song)
            else:
                # 检查是否匹配目标分类
                for target in target_genres:
                    if target.lower() in song_genres:
                        filtered_songs.append(song)
                        break
        
        # 按播放量降序排序
        sorted_songs = sorted(
            filtered_songs,
            key=lambda x: x.get('play_count', 0),
            reverse=True
        )[:limit]
        
        results = []
        for song in sorted_songs:
            db_manager.save_song(song)
            results.append(SongInfo(
                id=song['id'],
                title=song['title'],
                artist=song['artist'],
                album=song.get('album'),
                cover_url=song.get('cover_url'),
                duration=song.get('duration'),
                genre=song.get('genre'),
                release_date=song.get('release_date'),
                play_count=song.get('play_count'),
                trend_score=song.get('trend_score')
            ))
        
        return results


# 全局服务实例
song_search_service = SongSearchService()
