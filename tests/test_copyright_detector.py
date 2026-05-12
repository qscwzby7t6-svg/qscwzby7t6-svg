"""
版权检测模块单元测试
"""
import pytest
import numpy as np
import tempfile
import soundfile as sf
from pathlib import Path

from src.services.copyright_detector import CopyrightDetector, OriginalityReport


def generate_test_audio(output_path: Path, duration: float = 5.0, sample_rate: int = 22050, 
                        freq: float = 440.0, add_noise: bool = True):
    """
    生成测试音频文件
    
    Args:
        output_path: 输出路径
        duration: 时长
        sample_rate: 采样率
        freq: 频率
        add_noise: 是否添加噪声
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 生成正弦波
    y = np.sin(2 * np.pi * freq * t)
    
    # 添加一些谐波
    y += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    y += 0.2 * np.sin(2 * np.pi * freq * 3 * t)
    
    # 添加噪声
    if add_noise:
        y += 0.05 * np.random.randn(len(y))
    
    # 归一化
    y = y / np.max(np.abs(y)) * 0.9
    
    # 保存为WAV文件
    sf.write(str(output_path), y, sample_rate)


@pytest.fixture
def copyright_detector():
    """创建版权检测器实例"""
    return CopyrightDetector()


@pytest.fixture
def test_audio_dir():
    """创建测试音频目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 生成几个测试音频
        audio1 = temp_path / "audio1.wav"
        audio2 = temp_path / "audio2.wav"
        audio3 = temp_path / "audio3.wav"
        
        generate_test_audio(audio1, freq=440.0)  # A4
        generate_test_audio(audio2, freq=523.25)  # C5
        generate_test_audio(audio3, freq=440.0, add_noise=True)  # A4 with different noise
        
        yield temp_path


class TestCopyrightDetector:
    """测试版权检测器"""
    
    def test_init(self, copyright_detector):
        """测试初始化"""
        assert copyright_detector.sample_rate == 22050
        assert isinstance(copyright_detector.fingerprint_database, dict)
        assert len(copyright_detector.fingerprint_database) == 0
    
    def test_generate_fingerprint(self, copyright_detector, test_audio_dir):
        """测试生成音频指纹"""
        audio_path = test_audio_dir / "audio1.wav"
        fingerprint = copyright_detector.generate_fingerprint(audio_path)
        
        assert isinstance(fingerprint, np.ndarray)
        assert len(fingerprint) > 0
        assert fingerprint.dtype == np.float32
    
    def test_compute_similarity(self, copyright_detector, test_audio_dir):
        """测试计算相似度"""
        audio1 = test_audio_dir / "audio1.wav"
        audio2 = test_audio_dir / "audio2.wav"
        audio3 = test_audio_dir / "audio3.wav"
        
        fp1 = copyright_detector.generate_fingerprint(audio1)
        fp2 = copyright_detector.generate_fingerprint(audio2)
        fp3 = copyright_detector.generate_fingerprint(audio3)
        
        # 同一个音频的相似度应该很高
        sim_self = copyright_detector._compute_similarity(fp1, fp1)
        assert sim_self > 0.9
        
        # 相似音频的相似度应该比不相似的高（允许微小误差）
        sim13 = copyright_detector._compute_similarity(fp1, fp3)
        sim12 = copyright_detector._compute_similarity(fp1, fp2)
        assert sim13 >= sim12 - 0.0001  # 允许微小误差
    
    def test_add_and_search_database(self, copyright_detector, test_audio_dir):
        """测试添加和搜索数据库"""
        audio1 = test_audio_dir / "audio1.wav"
        audio2 = test_audio_dir / "audio2.wav"
        
        # 添加到数据库
        copyright_detector.add_to_database(
            "song1", audio1, 
            metadata={"title": "Test Song 1", "artist": "Test Artist 1"}
        )
        copyright_detector.add_to_database(
            "song2", audio2,
            metadata={"title": "Test Song 2", "artist": "Test Artist 2"}
        )
        
        # 搜索相似音频
        results = copyright_detector.search_similar(audio1, top_k=2)
        
        assert len(results) == 2
        # 最相似的应该是自己
        assert results[0].song_id == "song1"
        assert results[0].similarity > 0.9
    
    def test_check_originality_new_song(self, copyright_detector, test_audio_dir):
        """测试检查全新歌曲的原创性"""
        audio = test_audio_dir / "audio1.wav"
        
        # 空数据库，应该认为是原创的
        report = copyright_detector.check_originality(audio)
        
        assert isinstance(report, OriginalityReport)
        assert report.is_original is True
        assert report.originality_score > 0.8
        assert len(report.similar_songs) == 0
    
    def test_check_originality_with_reference(self, copyright_detector, test_audio_dir):
        """测试有参考音频的原创性检查"""
        audio1 = test_audio_dir / "audio1.wav"
        audio3 = test_audio_dir / "audio3.wav"
        
        # 添加到数据库
        copyright_detector.add_to_database(
            "song1", audio1,
            metadata={"title": "Test Song 1", "artist": "Test Artist 1"}
        )
        
        # 检查相似歌曲的原创性
        report = copyright_detector.check_originality(
            audio3,
            reference_audio=audio1,
            originality_threshold=0.5
        )
        
        assert isinstance(report, OriginalityReport)
        assert report.melody_similarity is not None
        assert len(report.similar_songs) > 0
