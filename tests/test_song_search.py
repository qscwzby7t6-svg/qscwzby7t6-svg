"""
歌曲搜索模块单元测试
"""
import pytest
from pathlib import Path

from src.services.song_search import SongSearchService, SongInfo
from src.config import settings


@pytest.fixture
def song_service():
    """创建歌曲搜索服务实例"""
    return SongSearchService()


class TestSongSearchService:
    """测试歌曲搜索服务"""
    
    def test_get_all_songs(self, song_service):
        """测试获取所有歌曲"""
        songs = song_service.get_all_songs()
        assert len(songs) > 0
        assert all(isinstance(song, SongInfo) for song in songs)
    
    def test_search_song_by_title(self, song_service):
        """测试按标题搜索歌曲"""
        results = song_service.search_song("夜曲")
        assert len(results) >= 1
        assert any("夜曲" in song.title for song in results)
    
    def test_search_song_by_title_and_artist(self, song_service):
        """测试按标题和艺术家搜索歌曲"""
        results = song_service.search_song("夜曲", "周杰伦")
        assert len(results) >= 1
        assert all(song.artist == "周杰伦" for song in results)
    
    def test_search_song_by_artist_only(self, song_service):
        """测试只按艺术家搜索歌曲"""
        results = song_service.search_song("不存在的歌曲", "薛之谦")
        assert len(results) >= 1
        assert all(song.artist == "薛之谦" for song in results)
    
    def test_search_no_results(self, song_service):
        """测试搜索没有结果的情况"""
        results = song_service.search_song("完全不存在的歌曲名称")
        assert len(results) == 0
    
    def test_get_song_by_id(self, song_service):
        """测试根据ID获取歌曲"""
        # 先搜索一个歌曲获取ID
        search_results = song_service.search_song("夜曲")
        assert len(search_results) > 0
        song_id = search_results[0].id
        
        # 测试获取歌曲
        song = song_service.get_song_by_id(song_id)
        assert song is not None
        assert song.id == song_id
    
    def test_get_song_invalid_id(self, song_service):
        """测试获取不存在的歌曲ID"""
        song = song_service.get_song_by_id("invalid_id_12345")
        assert song is None
    
    def test_get_audio_sample_not_found(self, song_service):
        """测试获取不存在的音频样本"""
        audio_path = song_service.get_audio_sample("song_001")
        # 应该返回None，因为我们还没有实际的音频文件
        assert audio_path is None
    
    def test_get_top_trending_songs(self, song_service):
        """测试获取热门歌曲（播放量最高的歌曲）"""
        top_songs = song_service.get_top_trending_songs(limit=5)
        
        assert len(top_songs) <= 5
        assert all(isinstance(song, SongInfo) for song in top_songs)
        
        # 检查是否按播放量降序排列
        play_counts = [song.play_count for song in top_songs if song.play_count is not None]
        assert play_counts == sorted(play_counts, reverse=True)
    
    def test_get_top_songs_by_genre(self, song_service):
        """测试按分类获取热门歌曲"""
        # 测试流行音乐分类
        pop_songs = song_service.get_top_songs_by_genre("流行音乐", limit=5)
        assert len(pop_songs) > 0
        
        # 测试摇滚分类
        rock_songs = song_service.get_top_songs_by_genre("摇滚", limit=5)
        assert len(rock_songs) > 0
        
        # 测试全部分类
        all_songs = song_service.get_top_songs_by_genre("全部", limit=10)
        assert len(all_songs) <= 10
    
    def test_music_genres_list(self, song_service):
        """测试音乐分类列表"""
        genres = song_service.MUSIC_GENRES
        assert len(genres) > 0
        assert "流行音乐" in genres
        assert "摇滚" in genres
        assert "民谣" in genres
    
    def test_get_song_by_rank(self, song_service):
        """测试根据排名获取歌曲"""
        # 测试第1名（播放量最高）
        top_song = song_service.get_song_by_rank(1)
        assert top_song is not None
        assert top_song.play_count is not None
        
        # 测试第10名
        rank10_song = song_service.get_song_by_rank(10)
        assert rank10_song is not None
        
        # 测试超出范围的情况
        out_of_range = song_service.get_song_by_rank(100)
        assert out_of_range is not None  # 应该返回最后一首
    
    def test_generate_song_name(self, song_service):
        """测试自动生成歌曲名称"""
        # 测试流行风格
        pop_style = {'genre': ['pop'], 'bpm': 120}
        pop_name = song_service.generate_song_name(pop_style)
        assert pop_name is not None
        assert len(pop_name) > 0
        assert '《' in pop_name and '》' in pop_name
        
        # 测试摇滚风格
        rock_style = {'genre': ['rock'], 'bpm': 150}
        rock_name = song_service.generate_song_name(rock_style)
        assert rock_name is not None
        
        # 测试默认风格
        default_style = {'genre': [], 'bpm': 100}
        default_name = song_service.generate_song_name(default_style)
        assert default_name is not None
