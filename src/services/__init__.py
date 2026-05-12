"""
服务模块
"""
from src.services.song_search import SongSearchService, song_search_service, SongInfo
from src.services.style_feature_extractor import (
    StyleFeatureExtractor,
    StyleFeatures,
    style_extractor
)
from src.services.copyright_detector import (
    CopyrightDetector,
    OriginalityReport,
    MatchResult,
    copyright_detector
)
from src.services.music_generator import (
    MusicGenerator,
    GeneratedSong,
    music_generator
)

__all__ = [
    'SongSearchService',
    'song_search_service',
    'SongInfo',
    'StyleFeatureExtractor',
    'StyleFeatures',
    'style_extractor',
    'CopyrightDetector',
    'OriginalityReport',
    'MatchResult',
    'copyright_detector',
    'MusicGenerator',
    'GeneratedSong',
    'music_generator'
]
