"""
高级AI音乐生成模块测试
"""
import pytest
import numpy as np
from pathlib import Path
import tempfile

from src.services.advanced_music_generator import (
    MusicGenIntegration,
    RiffusionIntegration,
    MusicGenerationFacade,
    AdvancedGeneratedSong
)
from src.services.style_feature_extractor import StyleFeatures


class TestMusicGenIntegration:
    """测试MusicGen集成"""
    
    @pytest.fixture
    def musicgen(self):
        return MusicGenIntegration()
    
    def test_initialization(self, musicgen):
        """测试初始化"""
        assert musicgen.sample_rate == 32000
        assert not musicgen.model_loaded
    
    def test_generate_with_prompt(self, musicgen):
        """测试使用提示生成音乐"""
        result = musicgen.generate_with_prompt(
            prompt="happy pop music",
            duration=5.0,
            sample_rate=22050
        )
        
        assert isinstance(result, AdvancedGeneratedSong)
        assert result.id
        assert result.duration == 5.0
        assert result.sample_rate == 22050
        assert result.style_similarity > 0
        assert Path(result.audio_path).exists()
    
    def test_generate_from_style(self, musicgen):
        """测试从风格特征生成音乐"""
        features = StyleFeatures(
            bpm=120.0,
            key="C",
            mode="major",
            spectral_centroid=500.0,
            spectral_bandwidth=1000.0,
            spectral_rolloff=2000.0,
            mfcc=[0.1] * 13,
            tempo=120.0,
            style_embedding=[0.1] * 128
        )
        
        result = musicgen.generate_from_style(
            style_features=features,
            lyrics="test lyrics",
            duration=5.0
        )
        
        assert isinstance(result, AdvancedGeneratedSong)
        assert result.duration == 5.0
        assert Path(result.audio_path).exists()


class TestRiffusionIntegration:
    """测试Riffusion集成"""
    
    @pytest.fixture
    def riffusion(self):
        return RiffusionIntegration()
    
    def test_initialization(self, riffusion):
        """测试初始化"""
        assert riffusion.api_endpoint == "http://localhost:5000/generate"
    
    def test_generate_from_spectrogram(self, riffusion):
        """测试从频谱图生成音乐"""
        result = riffusion.generate_from_spectrogram(
            prompt="electronic music",
            duration=5.0
        )
        
        assert isinstance(result, AdvancedGeneratedSong)
        assert result.id
        assert result.duration == 5.0
        assert result.style_similarity > 0


class TestMusicGenerationFacade:
    """测试音乐生成统一入口"""
    
    @pytest.fixture
    def facade(self):
        return MusicGenerationFacade()
    
    def test_set_model(self, facade):
        """测试设置模型"""
        facade.set_model("riffusion")
        assert facade.current_model == "riffusion"
        
        facade.set_model("musicgen")
        assert facade.current_model == "musicgen"
    
    def test_generate_music_with_prompt(self, facade):
        """测试使用提示生成音乐"""
        result = facade.generate_music(
            prompt="rock music",
            duration=5.0
        )
        
        assert isinstance(result, AdvancedGeneratedSong)
        assert result.duration == 5.0
    
    def test_generate_music_with_style(self, facade):
        """测试使用风格特征生成音乐"""
        features = StyleFeatures(
            bpm=120.0,
            key="C",
            mode="major",
            spectral_centroid=500.0,
            spectral_bandwidth=1000.0,
            spectral_rolloff=2000.0,
            mfcc=[0.1] * 13,
            tempo=120.0,
            style_embedding=[0.1] * 128
        )
        
        result = facade.generate_music(
            prompt="",
            duration=5.0,
            style_features=features,
            lyrics="test"
        )
        
        assert isinstance(result, AdvancedGeneratedSong)
        assert result.duration == 5.0
