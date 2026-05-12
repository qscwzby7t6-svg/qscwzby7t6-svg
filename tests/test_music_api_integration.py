"""
音乐API集成模块测试
"""
import pytest
from src.services.music_api_integration import (
    QQMusicAPI,
    NetEaseMusicAPI,
    MusicAPIFacade,
    RealSongInfo
)


class TestQQMusicAPI:
    """测试QQ音乐API"""
    
    @pytest.fixture
    def qq_api(self):
        return QQMusicAPI()
    
    def test_search_song(self, qq_api):
        """测试搜索歌曲"""
        results = qq_api.search_song("周杰伦", limit=5)
        assert isinstance(results, list)
        # 由于API可能不可用，测试结果可能为空
        for song in results:
            assert isinstance(song, RealSongInfo)
            assert song.title
            assert song.artist
            assert song.source == 'qqmusic'
    
    def test_generate_guid(self, qq_api):
        """测试GUID生成"""
        guid = qq_api._generate_guid()
        assert isinstance(guid, str)
        assert len(guid) > 0
    
    def test_generate_audio_url(self, qq_api):
        """测试音频URL生成"""
        url = qq_api._generate_audio_url("001")
        assert isinstance(url, str)
        assert "qqmusic" in url or "stream.qqmusic" in url


class TestNetEaseMusicAPI:
    """测试网易云音乐API"""
    
    @pytest.fixture
    def netease_api(self):
        return NetEaseMusicAPI()
    
    def test_search_song(self, netease_api):
        """测试搜索歌曲"""
        results = netease_api.search_song("陈奕迅", limit=5)
        assert isinstance(results, list)
        for song in results:
            assert isinstance(song, RealSongInfo)
            assert song.title
            assert song.artist
            assert song.source == 'netease'
    
    def test_generate_encryption_key(self, netease_api):
        """测试加密密钥生成"""
        key = netease_api._generate_encryption_key()
        assert isinstance(key, str)
        assert len(key) == 16


class TestMusicAPIFacade:
    """测试音乐API统一入口"""
    
    @pytest.fixture
    def facade(self):
        return MusicAPIFacade()
    
    def test_search_all(self, facade):
        """测试从所有平台搜索"""
        results = facade.search_all("晴天", limit=10)
        assert isinstance(results, list)
        assert len(results) <= 10
    
    def test_get_platform_songs_qqmusic(self, facade):
        """测试从QQ音乐平台搜索"""
        results = facade.get_platform_songs('qqmusic', "周杰伦", limit=5)
        assert isinstance(results, list)
        for song in results:
            assert song.source == 'qqmusic'
    
    def test_get_platform_songs_netease(self, facade):
        """测试从网易云音乐平台搜索"""
        results = facade.get_platform_songs('netease', "陈奕迅", limit=5)
        assert isinstance(results, list)
        for song in results:
            assert song.source == 'netease'
    
    def test_get_platform_songs_invalid(self, facade):
        """测试无效平台"""
        results = facade.get_platform_songs('invalid', "test", limit=5)
        assert results == []
