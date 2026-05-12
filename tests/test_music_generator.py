"""
AI音乐生成模块单元测试
"""
import pytest
import numpy as np
import soundfile as sf
from pathlib import Path

from src.services.music_generator import MusicGenerator, GeneratedSong
from src.services.style_feature_extractor import StyleFeatures


@pytest.fixture
def music_generator():
    """创建音乐生成器实例"""
    return MusicGenerator()


@pytest.fixture
def sample_style_features():
    """创建示例风格特征"""
    return StyleFeatures(
        bpm=120.0,
        key='C',
        mode='major',
        spectral_centroid=1000.0,
        spectral_bandwidth=500.0,
        spectral_rolloff=800.0,
        mfcc=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13],
        tempo=120.0,
        style_embedding=[0.5] * 128
    )


class TestMusicGenerator:
    """测试音乐生成器"""
    
    def test_init(self, music_generator):
        """测试初始化"""
        assert music_generator.sample_rate == 44100
        assert len(music_generator.SCALE_FREQS) > 0
        assert len(music_generator.CHORD_PROGRESSIONS) > 0
    
    def test_generate_tone(self, music_generator):
        """测试生成单个音调"""
        tone = music_generator._generate_tone(440.0, duration=0.5)
        
        assert isinstance(tone, np.ndarray)
        assert len(tone) == int(music_generator.sample_rate // 2)
        assert np.max(np.abs(tone)) > 0
    
    def test_generate_chord(self, music_generator):
        """测试生成和弦"""
        chord = music_generator._generate_chord(['C4', 'E4', 'G4'], duration=1.0)
        
        assert isinstance(chord, np.ndarray)
        assert len(chord) == music_generator.sample_rate
    
    def test_generate_melody(self, music_generator):
        """测试生成旋律"""
        duration = 5.0
        melody = music_generator._generate_melody(None, duration)
        
        assert isinstance(melody, np.ndarray)
        assert len(melody) == int(music_generator.sample_rate * duration)
    
    def test_generate_accompaniment(self, music_generator):
        """测试生成伴奏"""
        duration = 5.0
        accompaniment = music_generator._generate_accompaniment(None, duration)
        
        assert isinstance(accompaniment, np.ndarray)
        assert len(accompaniment) == int(music_generator.sample_rate * duration)
    
    def test_generate_song_simple(self, music_generator):
        """测试简单生成歌曲"""
        generated = music_generator.generate_song(
            duration=5,
            structure="intro-outro"
        )
        
        assert isinstance(generated, GeneratedSong)
        assert generated.id is not None
        assert generated.duration == 5
        assert generated.audio_path is not None
        assert Path(generated.audio_path).exists()
    
    def test_generate_song_with_features(self, music_generator, sample_style_features):
        """测试带风格特征的歌曲生成"""
        generated = music_generator.generate_song(
            style_features=sample_style_features,
            duration=3,
            lyrics_prompt="test song"
        )
        
        assert isinstance(generated, GeneratedSong)
        assert generated.id is not None
        assert generated.lyrics is not None
        assert "test song" in generated.lyrics
        assert generated.style_similarity > 0.5
    
    def test_generate_with_reference(self, music_generator, sample_style_features):
        """测试基于参考的歌曲生成"""
        generated = music_generator.generate_with_reference(
            reference_features=sample_style_features,
            style_weight=0.8,
            duration=3
        )
        
        assert isinstance(generated, GeneratedSong)
        assert generated.id is not None
        assert generated.style_similarity > 0.5
    
    def test_structure_parsing(self, music_generator):
        """测试歌曲结构解析"""
        generated = music_generator.generate_song(
            duration=8,
            structure="verse-chorus-verse"
        )
        
        assert isinstance(generated.structure, dict)
        assert len(generated.structure) == 3
        assert any("verse" in k for k in generated.structure.keys())
        assert any("chorus" in k for k in generated.structure.keys())
