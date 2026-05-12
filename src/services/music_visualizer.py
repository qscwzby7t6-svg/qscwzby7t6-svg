"""
音乐可视化模块
支持波形图、频谱图、梅尔频谱图等可视化展示
"""
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import soundfile as sf
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
import io
import base64

from src.config import settings


@dataclass
class WaveformData:
    """波形数据"""
    samples: np.ndarray
    sample_rate: int
    duration: float
    peak_amplitude: float
    rms_energy: float


@dataclass
class SpectralData:
    """频谱数据"""
    frequencies: np.ndarray
    magnitudes: np.ndarray
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float


@dataclass
class VisualizationResult:
    """可视化结果"""
    image_base64: str
    width: int
    height: int
    title: str


class WaveformVisualizer:
    """波形可视化器"""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 4), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi
        self.colors = {
            'waveform': '#1f77b4',
            'background': '#ffffff',
            'grid': '#e0e0e0'
        }
    
    def generate_waveform(
        self,
        audio_path: str,
        title: str = "音频波形图",
        show_grid: bool = True,
        show_peak: bool = True
    ) -> VisualizationResult:
        """
        生成波形图
        
        Args:
            audio_path: 音频文件路径
            title: 图表标题
            show_grid: 是否显示网格
            show_peak: 是否显示峰值标记
            
        Returns:
            可视化结果
        """
        # 读取音频
        y, sr = sf.read(audio_path)
        
        # 转换为单声道
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # 计算波形数据
        waveform_data = WaveformData(
            samples=y,
            sample_rate=sr,
            duration=len(y) / sr,
            peak_amplitude=np.max(np.abs(y)),
            rms_energy=np.sqrt(np.mean(y**2))
        )
        
        # 创建图表
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # 绘制波形
        time = np.linspace(0, waveform_data.duration, len(y))
        ax.plot(time, y, color=self.colors['waveform'], linewidth=0.5, alpha=0.7)
        ax.fill_between(time, y, alpha=0.3, color=self.colors['waveform'])
        
        # 显示峰值
        if show_peak:
            ax.axhline(y=waveform_data.peak_amplitude, color='red', linestyle='--', alpha=0.5, label=f'峰值: {waveform_data.peak_amplitude:.3f}')
            ax.axhline(y=-waveform_data.peak_amplitude, color='red', linestyle='--', alpha=0.5)
        
        # 设置标题和标签
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('时间 (秒)', fontsize=10)
        ax.set_ylabel('振幅', fontsize=10)
        
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')
        
        ax.set_xlim(0, waveform_data.duration)
        ax.set_ylim(-1.1, 1.1)
        
        plt.tight_layout()
        
        # 转换为base64
        img_base64 = self._fig_to_base64(fig)
        
        return VisualizationResult(
            image_base64=img_base64,
            width=self.figsize[0] * self.dpi,
            height=self.figsize[1] * self.dpi,
            title=title
        )
    
    def generate_stereo_waveform(
        self,
        audio_path: str,
        title: str = "立体声波形图"
    ) -> VisualizationResult:
        """生成立体声波形图"""
        y, sr = sf.read(audio_path)
        
        # 创建图表
        fig, (ax_l, ax_r) = plt.subplots(2, 1, figsize=self.figsize, dpi=self.dpi)
        
        time = np.linspace(0, len(y) / sr, len(y))
        
        if len(y.shape) == 1:
            # 单声道复制为双声道
            ax_l.plot(time, y, color='#1f77b4', linewidth=0.5)
            ax_r.plot(time, y, color='#ff7f0e', linewidth=0.5)
        else:
            # 立体声
            ax_l.plot(time, y[:, 0], color='#1f77b4', linewidth=0.5)
            ax_r.plot(time, y[:, 1], color='#ff7f0e', linewidth=0.5)
        
        ax_l.set_title('左声道', fontsize=12)
        ax_l.set_ylabel('振幅')
        ax_l.grid(True, alpha=0.3)
        
        ax_r.set_title('右声道', fontsize=12)
        ax_r.set_xlabel('时间 (秒)')
        ax_r.set_ylabel('振幅')
        ax_r.grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        img_base64 = self._fig_to_base64(fig)
        
        return VisualizationResult(
            image_base64=img_base64,
            width=self.figsize[0] * self.dpi,
            height=self.figsize[1] * self.dpi,
            title=title
        )
    
    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图表转换为base64"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        buf.close()
        return img_base64


class SpectrumVisualizer:
    """频谱可视化器"""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 6), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi
    
    def generate_spectrum(
        self,
        audio_path: str,
        title: str = "频谱分析图"
    ) -> VisualizationResult:
        """
        生成频谱图
        
        Args:
            audio_path: 音频文件路径
            title: 图表标题
            
        Returns:
            可视化结果
        """
        y, sr = sf.read(audio_path)
        
        # 转换为单声道
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # 计算FFT
        n_fft = 2048
        y_segment = y[:n_fft]
        spectrum = np.fft.fft(y_segment)
        frequencies = np.fft.fftfreq(n_fft, 1/sr)
        
        # 获取正频率部分
        positive_freq_idx = frequencies >= 0
        frequencies = frequencies[positive_freq_idx]
        magnitudes = np.abs(spectrum[positive_freq_idx])
        
        # 创建图表
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        ax.plot(frequencies, magnitudes, color='#2ca02c', linewidth=1)
        ax.fill_between(frequencies, magnitudes, alpha=0.3, color='#2ca02c')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('频率 (Hz)', fontsize=10)
        ax.set_ylabel('幅度', fontsize=10)
        ax.set_xlim(0, sr/2)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        img_base64 = self._fig_to_base64(fig)
        
        return VisualizationResult(
            image_base64=img_base64,
            width=self.figsize[0] * self.dpi,
            height=self.figsize[1] * self.dpi,
            title=title
        )
    
    def generate_spectrogram(
        self,
        audio_path: str,
        title: str = "语谱图"
    ) -> VisualizationResult:
        """
        生成语谱图
        
        Args:
            audio_path: 音频文件路径
            title: 图表标题
            
        Returns:
            可视化结果
        """
        y, sr = sf.read(audio_path)
        
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # 计算语谱图
        n_fft = 2048
        hop_length = 512
        
        D = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
        librosa.display.specshow(
            librosa.amplitude_to_db(D, ref=np.max),
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='log',
            ax=None
        )
        
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        img = librosa.display.specshow(
            librosa.amplitude_to_db(D, ref=np.max),
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='log',
            ax=ax
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('时间 (秒)', fontsize=10)
        ax.set_ylabel('频率 (Hz)', fontsize=10)
        
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        
        plt.tight_layout()
        
        img_base64 = self._fig_to_base64(fig)
        
        return VisualizationResult(
            image_base64=img_base64,
            width=self.figsize[0] * self.dpi,
            height=self.figsize[1] * self.dpi,
            title=title
        )
    
    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图表转换为base64"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        buf.close()
        return img_base64


class MelSpectrogramVisualizer:
    """梅尔频谱可视化器"""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 6), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi
    
    def generate_mel_spectrogram(
        self,
        audio_path: str,
        title: str = "梅尔频谱图",
        n_mels: int = 128
    ) -> VisualizationResult:
        """
        生成梅尔频谱图
        
        Args:
            audio_path: 音频文件路径
            title: 图表标题
            n_mels: 梅尔滤波器数量
            
        Returns:
            可视化结果
        """
        y, sr = sf.read(audio_path)
        
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # 计算梅尔频谱
        n_fft = 2048
        hop_length = 512
        
        mel_spec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=n_mels
        )
        
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        img = librosa.display.specshow(
            mel_spec_db,
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='mel',
            ax=ax,
            cmap='viridis'
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('时间 (秒)', fontsize=10)
        ax.set_ylabel('频率 (Hz) - 梅尔刻度', fontsize=10)
        
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        buf.close()
        
        return VisualizationResult(
            image_base64=img_base64,
            width=self.figsize[0] * self.dpi,
            height=self.figsize[1] * self.dpi,
            title=title
        )


class AudioAnalyzer:
    """音频分析器"""
    
    def __init__(self):
        self.waveform_visualizer = WaveformVisualizer()
        self.spectrum_visualizer = SpectrumVisualizer()
        self.mel_visualizer = MelSpectrogramVisualizer()
    
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        全面分析音频
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            分析结果字典
        """
        y, sr = sf.read(audio_path)
        
        if len(y.shape) > 1:
            y_mono = np.mean(y, axis=1)
        else:
            y_mono = y
        
        # 基本信息
        duration = len(y) / sr
        sample_rate = sr
        
        # 波形分析
        peak_amplitude = float(np.max(np.abs(y_mono)))
        rms_energy = float(np.sqrt(np.mean(y_mono**2)))
        
        # 频谱分析
        spectral_centroid = float(librosa.feature.spectral_centroid(y=y_mono, sr=sr)[0].mean())
        spectral_bandwidth = float(librosa.feature.spectral_bandwidth(y=y_mono, sr=sr)[0].mean())
        spectral_rolloff = float(librosa.feature.spectral_rolloff(y=y_mono, sr=sr)[0].mean())
        
        # 节奏分析
        try:
            tempo, _ = librosa.beat.beat_track(y=y_mono, sr=sr)
            tempo = float(tempo)
        except:
            tempo = 0.0
        
        # 音高分析
        pitches, magnitudes = librosa.piptrack(y=y_mono, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        avg_pitch = float(np.mean(pitch_values)) if pitch_values else 0.0
        
        return {
            'duration': duration,
            'sample_rate': sample_rate,
            'peak_amplitude': peak_amplitude,
            'rms_energy': rms_energy,
            'spectral_centroid': spectral_centroid,
            'spectral_bandwidth': spectral_bandwidth,
            'spectral_rolloff': spectral_rolloff,
            'tempo': tempo,
            'average_pitch': avg_pitch,
            'dynamic_range': float(20 * np.log10(peak_amplitude / (rms_energy + 1e-10)))
        }
    
    def generate_all_visualizations(
        self,
        audio_path: str
    ) -> Dict[str, VisualizationResult]:
        """
        生成所有可视化图表
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            可视化结果字典
        """
        results = {}
        
        # 波形图
        results['waveform'] = self.waveform_visualizer.generate_waveform(
            audio_path,
            title="音频波形图"
        )
        
        # 立体声波形图
        results['stereo_waveform'] = self.waveform_visualizer.generate_stereo_waveform(
            audio_path,
            title="立体声波形图"
        )
        
        # 频谱图
        results['spectrum'] = self.spectrum_visualizer.generate_spectrum(
            audio_path,
            title="频谱分析图"
        )
        
        # 语谱图
        results['spectrogram'] = self.spectrum_visualizer.generate_spectrogram(
            audio_path,
            title="语谱图"
        )
        
        # 梅尔频谱图
        results['mel_spectrogram'] = self.mel_visualizer.generate_mel_spectrogram(
            audio_path,
            title="梅尔频谱图"
        )
        
        return results


# 全局实例
audio_analyzer = AudioAnalyzer()
waveform_visualizer = WaveformVisualizer()
spectrum_visualizer = SpectrumVisualizer()
mel_visualizer = MelSpectrogramVisualizer()
