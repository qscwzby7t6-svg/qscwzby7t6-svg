"""
数据库模块单元测试
"""
import pytest
import tempfile
import time
import numpy as np
from pathlib import Path
from src.models.database import DatabaseManager


@pytest.fixture
def temp_db():
    """创建临时数据库"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    db = DatabaseManager(db_path)
    yield db
    
    # 清理
    if db_path.exists():
        db_path.unlink()


class TestDatabaseManager:
    """测试DatabaseManager类"""
    
    def test_init_database(self, temp_db):
        """测试数据库初始化"""
        # 检查表是否创建成功
        with temp_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'songs' in tables
            assert 'style_features' in tables
            assert 'generated_songs' in tables
    
    def test_save_and_get_song(self, temp_db):
        """测试保存和获取歌曲"""
        # 保存歌曲
        song_data = {
            'id': 'test_song_001',
            'title': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'duration': 180,
            'genre': ['pop', 'rock'],
            'release_date': '2024-01-01'
        }
        temp_db.save_song(song_data)
        
        # 获取歌曲
        retrieved = temp_db.get_song('test_song_001')
        assert retrieved is not None
        assert retrieved['id'] == 'test_song_001'
        assert retrieved['title'] == 'Test Song'
        assert retrieved['artist'] == 'Test Artist'
        assert retrieved['genre'] == ['pop', 'rock']
    
    def test_search_songs(self, temp_db):
        """测试搜索歌曲"""
        # 保存测试歌曲
        songs = [
            {'id': 's1', 'title': 'Hello World', 'artist': 'Artist A'},
            {'id': 's2', 'title': 'Test Track', 'artist': 'Artist B'},
            {'id': 's3', 'title': 'Another Song', 'artist': 'Artist A'},
        ]
        for song in songs:
            temp_db.save_song(song)
        
        # 按标题搜索
        results = temp_db.search_songs(title='Hello')
        assert len(results) == 1
        assert results[0]['id'] == 's1'
        
        # 按艺术家搜索
        results = temp_db.search_songs(artist='Artist A')
        assert len(results) == 2
    
    def test_save_and_get_style_features(self, temp_db):
        """测试保存和获取风格特征"""
        # 先保存歌曲
        temp_db.save_song({
            'id': 'test_song_002',
            'title': 'Test Song 2',
            'artist': 'Test Artist'
        })
        
        # 保存风格特征
        features = {
            'bpm': 120.0,
            'key': 'C',
            'mode': 'major',
            'spectral_centroid': 1000.0,
            'spectral_bandwidth': 500.0,
            'spectral_rolloff': 800.0,
            'mfcc': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13],
            'tempo': 120.0
        }
        style_embedding = np.random.rand(128).astype(np.float32)
        
        temp_db.save_style_features('test_song_002', features, style_embedding)
        
        # 获取风格特征
        retrieved = temp_db.get_style_features('test_song_002')
        assert retrieved is not None
        assert retrieved['bpm'] == 120.0
        assert retrieved['key'] == 'C'
        assert 'style_embedding' in retrieved
        assert len(retrieved['style_embedding']) == 128
    
    def test_save_and_get_generated_song(self, temp_db):
        """测试保存和获取生成的歌曲"""
        # 先保存参考歌曲
        temp_db.save_song({
            'id': 'ref_song_001',
            'title': 'Reference Song',
            'artist': 'Reference Artist'
        })
        
        # 保存生成的歌曲
        generated_data = {
            'id': 'gen_song_001',
            'reference_song_id': 'ref_song_001',
            'style_similarity': 0.85,
            'originality_score': 0.9,
            'audio_path': '/path/to/audio.wav',
            'lyrics': 'Test lyrics...'
        }
        temp_db.save_generated_song(generated_data)
        
        # 获取生成的歌曲
        retrieved = temp_db.get_generated_song('gen_song_001')
        assert retrieved is not None
        assert retrieved['id'] == 'gen_song_001'
        assert retrieved['style_similarity'] == 0.85
        assert retrieved['originality_score'] == 0.9
    
    def test_get_recent_generated(self, temp_db):
        """测试获取最近生成的作品"""
        # 保存多个生成的歌曲
        song_ids = []
        for i in range(5):
            song_id = f'gen_song_{i:03d}'
            temp_db.save_generated_song({
                'id': song_id,
                'reference_song_id': 'ref_song',
                'style_similarity': 0.8,
                'originality_score': 0.9
            })
            song_ids.append(song_id)
        
        # 获取最近的
        recent = temp_db.get_recent_generated(3)
        assert len(recent) == 3
        # 检查返回的歌曲ID都在我们保存的ID中
        recent_ids = [song['id'] for song in recent]
        for song_id in recent_ids:
            assert song_id in song_ids
