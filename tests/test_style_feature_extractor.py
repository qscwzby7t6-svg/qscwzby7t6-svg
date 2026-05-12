"""
风格特征提取模块单元测试
"""
import pytest
import numpy as np
import tempfile
import soundfile as sf
from pathlib import Path

from src.services.style_feature_extractor import StyleFeatureExtractor, StyleFeatures
from src.config import settings


def generate_test_audio(output_path: Path, duration: float = 5.0, sample_rate: int = 22050):
    """
    生成一个简单的测试音频文件
    
    Args:
        output_path: 输出文件路径
        duration: 时长（秒）
        sample_rate: 采样率
    """
    # 生成一个简单的正弦波（C大调和弦）
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # C大调和弦: C (261.63 Hz), E (329.63 Hz), G (392.00 Hz)
    y = (np.sin(2 * np.pi * 261.63 * t) + 
         np.sin(2 * np.pi * 329.63 * t) * 0.5 + 
         np.sin(2 * np.pi * 392.00 * t) * 0.3)
    
    # 添加一些打击乐节奏（模拟120 BPM）
    bpm = 120
    beat_interval = 60.0 / bpm
    for i in range(int(duration / beat_interval)):
        start_idx = int(i * beat_interval * sample_rate)
        end_idx = min(start_idx + int(0.1 * sample_rate), len(y))
        y[start_idx:end_idx] += 0.3 * np.random.randn(end_idx - start_idx)
    
    # 归一化
    y = y / np.max(np.abs(y)) * 0.9
    
    # 保存为WAV文件
    sf.write(str(output_path), y, sample_rate)


@pytest.fixture
def test_audio_path():
    """创建测试音频文件的fixture"""
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "test_audio.wav"
        generate_test_audio(audio_path)
        yield audio_path


@pytest.fixture
def feature_extractor():
    """创建特征提取器实例"""
    return StyleFeatureExtractor()


class TestStyleFeatureExtractor:
    """测试风格特征提取器"""
    
    def test_init(self, feature_extractor):
        """测试初始化"""
        assert feature_extractor.sample_rate == 22050
    
    def test_extract_features(self, feature_extractor, test_audio_path):
        """测试特征提取"""
        features = feature_extractor.extract_features(test_audio_path)
        
        # 检查返回类型
        assert isinstance(features, StyleFeatures)
        
        # 检查基本特征
        assert features.bpm > 0
        assert features.key in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        assert features.mode in ['major', 'minor']
        
        # 检查频谱特征
        assert features.spectral_centroid > 0
        assert features.spectral_bandwidth > 0
        assert features.spectral_rolloff > 0
        
        # 检查MFCC特征
        assert len(features.mfcc) == 13
        
        # 检查风格嵌入
        assert len(features.style_embedding) == 128
        # 检查嵌入值范围
        assert all(-1 <= x <= 1 for x in features.style_embedding)
    
    def test_to_dict(self, feature_extractor, test_audio_path):
        """测试转换为字典"""
        features = feature_extractor.extract_features(test_audio_path)
        feature_dict = features.to_dict()
        
        assert isinstance(feature_dict, dict)
        assert 'bpm' in feature_dict
        assert 'key' in feature_dict
        assert 'style_embedding' in feature_dict
    
    def test_style_embedding_range(self, feature_extractor, test_audio_path):
        """测试风格嵌入值范围"""
        features = feature_extractor.extract_features(test_audio_path)
        embedding = np.array(features.style_embedding)
        
        # 检查是否在[-1, 1]范围内
        assert np.all(embedding >= -1.001)  # 允许一点误差
        assert np.all(embedding <= 1.001)
        
        # 检查是否有变化（不全相同）
        assert not np.allclose(embedding, embedding[0])
