"""
音乐可视化模块测试
"""
import pytest
import numpy as np
from pathlib import Path
import tempfile
import soundfile as sf

from src.services.music_visualizer import (
    WaveformVisualizer,
    SpectrumVisualizer,
    MelSpectrogramVisualizer,
    AudioAnalyzer,
    WaveformData,
    SpectralData,
    VisualizationResult
)


class TestWaveformVisualizer:
    """测试波形可视化器"""
    
    @pytest.fixture
    def visualizer(self):
        return WaveformVisualizer(figsize=(10, 4), dpi=80)
    
    @pytest.fixture
    def test_audio(self):
        """创建测试音频文件"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            sr = 22050
            duration = 5.0
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            y = np.sin(2 * np.pi * 440 * t) * 0.3
            sf.write(f.name, y, sr)
            return f.name
    
    def test_generate_waveform(self, visualizer, test_audio):
        """测试生成波形图"""
        result = visualizer.generate_waveform(
            audio_path=test_audio,
            title="测试波形图"
        )
        
        assert isinstance(result, VisualizationResult)
        assert result.image_base64
        assert result.width > 0
        assert result.height > 0
        assert result.title == "测试波形图"
    
    def test_generate_stereo_waveform(self, visualizer, test_audio):
        """测试生成立体声波形图"""
        result = visualizer.generate_stereo_waveform(
            audio_path=test_audio,
            title="测试立体声波形图"
        )
        
        assert isinstance(result, VisualizationResult)
        assert result.image_base64
        assert result.width > 0
        assert result.height > 0


class TestSpectrumVisualizer:
    """测试频谱可视化器"""
    
    @pytest.fixture
    def visualizer(self):
        return SpectrumVisualizer(figsize=(10, 6), dpi=80)
    
    @pytest.fixture
    def test_audio(self):
        """创建测试音频文件"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            sr = 22050
            duration = 5.0
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            y = np.sin(2 * np.pi * 440 * t) * 0.3
            sf.write(f.name, y, sr)
            return f.name
    
    def test_generate_spectrum(self, visualizer, test_audio):
        """测试生成频谱图"""
        result = visualizer.generate_spectrum(
            audio_path=test_audio,
            title="测试频谱图"
        )
        
        assert isinstance(result, VisualizationResult)
        assert result.image_base64
        assert result.width > 0
        assert result.height > 0
    
    def test_generate_spectrogram(self, visualizer, test_audio):
        """测试生成语谱图"""
        result = visualizer.generate_spectrogram(
            audio_path=test_audio,
            title="测试语谱图"
        )
        
        assert isinstance(result, VisualizationResult)
        assert result.image_base64
        assert result.width > 0
        assert result.height > 0


class TestMelSpectrogramVisualizer:
    """测试梅尔频谱可视化器"""
    
    @pytest.fixture
    def visualizer(self):
        return MelSpectrogramVisualizer(figsize=(10, 6), dpi=80)
    
    @pytest.fixture
    def test_audio(self):
        """创建测试音频文件"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            sr = 22050
            duration = 5.0
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            y = np.sin(2 * np.pi * 440 * t) * 0.3
            sf.write(f.name, y, sr)
            return f.name
    
    def test_generate_mel_spectrogram(self, visualizer, test_audio):
        """测试生成梅尔频谱图"""
        result = visualizer.generate_mel_spectrogram(
            audio_path=test_audio,
            title="测试梅尔频谱图",
            n_mels=128
        )
        
        assert isinstance(result, VisualizationResult)
        assert result.image_base64
        assert result.width > 0
        assert result.height > 0


class TestAudioAnalyzer:
    """测试音频分析器"""
    
    @pytest.fixture
    def analyzer(self):
        return AudioAnalyzer()
    
    @pytest.fixture
    def test_audio(self):
        """创建测试音频文件"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            sr = 22050
            duration = 5.0
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            y = np.sin(2 * np.pi * 440 * t) * 0.3
            sf.write(f.name, y, sr)
            return f.name
    
    def test_analyze_audio(self, analyzer, test_audio):
        """测试分析音频"""
        result = analyzer.analyze_audio(test_audio)
        
        assert isinstance(result, dict)
        assert 'duration' in result
        assert 'sample_rate' in result
        assert 'peak_amplitude' in result
        assert 'rms_energy' in result
        assert 'spectral_centroid' in result
        assert 'spectral_bandwidth' in result
        assert 'spectral_rolloff' in result
        assert 'tempo' in result
        assert 'average_pitch' in result
        assert 'dynamic_range' in result
        
        assert result['duration'] == 5.0
        assert result['sample_rate'] == 22050
        assert result['peak_amplitude'] > 0
        assert result['rms_energy'] > 0
    
    def test_generate_all_visualizations(self, analyzer, test_audio):
        """测试生成所有可视化"""
        results = analyzer.generate_all_visualizations(test_audio)
        
        assert isinstance(results, dict)
        assert 'waveform' in results
        assert 'stereo_waveform' in results
        assert 'spectrum' in results
        assert 'spectrogram' in results
        assert 'mel_spectrogram' in results
        
        for key, value in results.items():
            assert isinstance(value, VisualizationResult)
            assert value.image_base64
            assert value.width > 0
            assert value.height > 0
