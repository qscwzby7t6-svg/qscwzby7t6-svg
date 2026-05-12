"""
数据库管理模块
"""
import sqlite3
import json
import numpy as np
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Generator
from datetime import datetime

from src.config import settings


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_DIR / "app.db"
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建歌曲信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS songs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT,
                    cover_url TEXT,
                    duration INTEGER,
                    genre TEXT,
                    release_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建风格特征表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS style_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id TEXT NOT NULL,
                    bpm REAL,
                    key TEXT,
                    mode TEXT,
                    style_embedding BLOB,
                    features_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (song_id) REFERENCES songs(id)
                )
            ''')
            
            # 创建生成作品表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_songs (
                    id TEXT PRIMARY KEY,
                    reference_song_id TEXT,
                    style_similarity REAL,
                    originality_score REAL,
                    audio_path TEXT,
                    lyrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (reference_song_id) REFERENCES songs(id)
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # === 歌曲相关操作 ===
    
    def save_song(self, song_data: Dict[str, Any]) -> None:
        """保存歌曲信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM songs WHERE id = ?', (song_data['id'],))
            if cursor.fetchone():
                # 更新
                cursor.execute('''
                    UPDATE songs SET title=?, artist=?, album=?, cover_url=?, 
                    duration=?, genre=?, release_date=? WHERE id=?
                ''', (
                    song_data['title'],
                    song_data['artist'],
                    song_data.get('album'),
                    song_data.get('cover_url'),
                    song_data.get('duration'),
                    json.dumps(song_data.get('genre', [])),
                    song_data.get('release_date'),
                    song_data['id']
                ))
            else:
                # 插入
                cursor.execute('''
                    INSERT INTO songs (id, title, artist, album, cover_url, duration, genre, release_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    song_data['id'],
                    song_data['title'],
                    song_data['artist'],
                    song_data.get('album'),
                    song_data.get('cover_url'),
                    song_data.get('duration'),
                    json.dumps(song_data.get('genre', [])),
                    song_data.get('release_date')
                ))
            
            conn.commit()
    
    def get_song(self, song_id: str) -> Optional[Dict[str, Any]]:
        """获取歌曲信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM songs WHERE id = ?', (song_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                if result.get('genre'):
                    result['genre'] = json.loads(result['genre'])
                return result
            return None
    
    def search_songs(self, title: Optional[str] = None, artist: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索歌曲"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM songs WHERE 1=1'
            params = []
            
            if title:
                query += ' AND title LIKE ?'
                params.append(f'%{title}%')
            
            if artist:
                query += ' AND artist LIKE ?'
                params.append(f'%{artist}%')
            
            cursor.execute(query, params)
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get('genre'):
                    result['genre'] = json.loads(result['genre'])
                results.append(result)
            return results
    
    # === 风格特征相关操作 ===
    
    def save_style_features(self, song_id: str, features, style_embedding) -> None:
        """保存风格特征（支持Dict或StyleFeatures对象）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 删除旧的特征
            cursor.execute('DELETE FROM style_features WHERE song_id = ?', (song_id,))
            
            # 处理features参数
            if hasattr(features, 'to_dict'):
                features_dict = features.to_dict()
                bpm = features.bpm
                key = features.key
                mode = features.mode
            elif isinstance(features, dict):
                features_dict = features
                bpm = features.get('bpm')
                key = features.get('key')
                mode = features.get('mode')
            else:
                # 尝试从对象属性获取
                features_dict = {
                    'bpm': getattr(features, 'bpm', None),
                    'key': getattr(features, 'key', None),
                    'mode': getattr(features, 'mode', None),
                    'spectral_centroid': getattr(features, 'spectral_centroid', None),
                    'spectral_bandwidth': getattr(features, 'spectral_bandwidth', None),
                    'spectral_rolloff': getattr(features, 'spectral_rolloff', None),
                    'mfcc': getattr(features, 'mfcc', None),
                    'tempo': getattr(features, 'tempo', None),
                }
                bpm = getattr(features, 'bpm', None)
                key = getattr(features, 'key', None)
                mode = getattr(features, 'mode', None)
            
            # 处理style_embedding
            if isinstance(style_embedding, list):
                style_embedding = np.array(style_embedding, dtype=np.float32)
            
            # 插入新特征
            cursor.execute('''
                INSERT INTO style_features (song_id, bpm, key, mode, style_embedding, features_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                song_id,
                bpm,
                key,
                mode,
                style_embedding.tobytes(),
                json.dumps(features_dict)
            ))
            
            conn.commit()
    
    def get_style_features(self, song_id: str) -> Optional[Dict[str, Any]]:
        """获取风格特征"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM style_features WHERE song_id = ?', (song_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                if result.get('features_json'):
                    features = json.loads(result['features_json'])
                    if result.get('style_embedding'):
                        features['style_embedding'] = np.frombuffer(result['style_embedding'], dtype=np.float32).tolist()
                    return features
            return None
    
    # === 生成作品相关操作 ===
    
    def save_generated_song(self, song_id=None, audio_path=None, 
                           style_features=None, lyrics=None, 
                           style_similarity=None, **kwargs) -> None:
        """保存生成的作品（支持多种参数格式）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 处理不同的参数格式
            reference_song_id = None
            originality_score = None
            
            if isinstance(song_id, dict) and audio_path is None:
                # 如果第一个参数是字典，旧格式
                generated_data = song_id
                song_id = generated_data['id']
                audio_path = generated_data.get('audio_path')
                style_similarity = generated_data.get('style_similarity')
                lyrics = generated_data.get('lyrics')
                reference_song_id = generated_data.get('reference_song_id')
                originality_score = generated_data.get('originality_score')
            else:
                # 新格式，从参数和kwargs构建
                reference_song_id = kwargs.get('reference_song_id')
                originality_score = kwargs.get('originality_score')
            
            # 插入
            cursor.execute('''
                INSERT OR REPLACE INTO generated_songs (id, reference_song_id, style_similarity, 
                originality_score, audio_path, lyrics)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                song_id,
                reference_song_id,
                style_similarity,
                originality_score,
                audio_path,
                lyrics
            ))
            conn.commit()
    
    def get_generated_song(self, song_id: str) -> Optional[Dict[str, Any]]:
        """获取生成的作品"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM generated_songs WHERE id = ?', (song_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_recent_generated(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近生成的作品"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM generated_songs 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]


# 创建全局数据库实例
db_manager = DatabaseManager()
