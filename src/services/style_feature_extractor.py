"""
风格特征提取模块
"""
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.config import settings
from src.models import db_manager


@dataclass
class StyleFeatures:
    """风格特征"""
    # 声学特征
    bpm: float
    key: str
    mode: str  # 'major' 或 'minor'
    
    # 频谱特征
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float
    mfcc: List[float]  # 13维MFCC
    
    # 节奏特征
    tempo: float
    
    # 风格向量
    style_embedding: List[float]  # 128维
    
    # 有默认值的参数放在最后
    time_signature: str = '4/4'
    beat_frames: Optional[List[int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'bpm': self.bpm,
            'key': self.key,
            'mode': self.mode,
            'time_signature': self.time_signature,
            'spectral_centroid': self.spectral_centroid,
            'spectral_bandwidth': self.spectral_bandwidth,
            'spectral_rolloff': self.spectral_rolloff,
            'mfcc': self.mfcc,
            'tempo': self.tempo,
            'beat_frames': self.beat_frames,
            'style_embedding': self.style_embedding
        }


class StyleFeatureExtractor:
    """风格特征提取器"""
    
    # 调式映射
    _KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self, sample_rate: int = 22050):
        """
        初始化特征提取器
        
        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate
    
    def _estimate_key(self, y: np.ndarray, sr: int) -> tuple[str, str]:
        """
        估计音频的调式
        
        Args:
            y: 音频数据
            sr: 采样率
            
        Returns:
            (key, mode) 元组
        """
        # 计算色度特征
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # 计算每个调的平均能量
        key_energy = np.mean(chroma, axis=1)
        
        # 找到能量最高的调
        key_idx = np.argmax(key_energy)
        key = self._KEYS[key_idx]
        
        # 简单估计大调/小调（通过比较大调和小调的典型和弦）
        # 这里用一个简化的方法
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        
        # 循环移位比较
        maj_corr = []
        min_corr = []
        for i in range(12):
            shifted_chroma = np.roll(key_energy, -i)
            maj_corr.append(np.corrcoef(shifted_chroma, major_profile)[0, 1])
            min_corr.append(np.corrcoef(shifted_chroma, minor_profile)[0, 1])
        
        if np.max(maj_corr) > np.max(min_corr):
            mode = 'major'
        else:
            mode = 'minor'
        
        return key, mode
    
    def extract_features(self, audio_path: Path) -> StyleFeatures:
        """
        从音频文件提取风格特征
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            风格特征对象
        """
        # 加载音频
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate, duration=30)  # 只使用前30秒
        
        # 1. 估计BPM和节拍
        try:
            # 尝试使用新版本的API
            tempo = librosa.beat.tempo(y=y, sr=sr)
            bpm = float(tempo) if np.isscalar(tempo) else float(tempo[0])
        except (ValueError, TypeError):
            # 如果失败，使用默认值
            bpm = 120.0
        
        # 估计节拍位置
        try:
            _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        except Exception:
            beat_frames = None
        
        # 2. 估计调式
        key, mode = self._estimate_key(y, sr)
        
        # 3. 频谱特征
        spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
        spectral_bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
        spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
        
        # 4. MFCC特征
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1).tolist()
        
        # 5. 生成风格嵌入（这里用一个简化的方法，实际可以用预训练模型）
        # 组合各种特征生成128维向量
        style_embedding = self._generate_style_embedding(
            bpm=bpm,
            spectral_centroid=spectral_centroid,
            spectral_bandwidth=spectral_bandwidth,
            spectral_rolloff=spectral_rolloff,
            mfcc=mfcc_mean
        )
        
        return StyleFeatures(
            bpm=bpm,
            key=key,
            mode=mode,
            spectral_centroid=spectral_centroid,
            spectral_bandwidth=spectral_bandwidth,
            spectral_rolloff=spectral_rolloff,
            mfcc=mfcc_mean,
            tempo=bpm,
            style_embedding=style_embedding,
            time_signature='4/4',  # 简化处理
            beat_frames=beat_frames.tolist() if (beat_frames is not None and len(beat_frames) > 0) else None
        )
    
    def _generate_style_embedding(
        self,
        bpm: float,
        spectral_centroid: float,
        spectral_bandwidth: float,
        spectral_rolloff: float,
        mfcc: List[float]
    ) -> List[float]:
        """
        生成风格嵌入向量
        
        Args:
            各种音频特征
            
        Returns:
            128维风格向量
        """
        # 归一化特征
        normalized_features = [
            bpm / 200.0,  # BPM通常在60-200之间
            spectral_centroid / 8000.0,
            spectral_bandwidth / 4000.0,
            spectral_rolloff / 8000.0,
        ] + [x / 100.0 for x in mfcc]
        
        # 生成128维向量（通过重复和填充）
        embedding = []
        feature_length = len(normalized_features)
        
        # 填充到128维
        for i in range(128):
            idx = i % feature_length
            # 添加一些变化
            value = normalized_features[idx] * (1 + 0.1 * np.sin(i * 0.1))
            embedding.append(float(value))
        
        # 归一化到 [-1, 1] 范围
        embedding = np.array(embedding)
        embedding = 2 * (embedding - np.min(embedding)) / (np.max(embedding) - np.min(embedding)) - 1
        
        return embedding.tolist()
    
    async def extract_and_save_features(self, song_id: str, audio_path: Path) -> StyleFeatures:
        """
        提取特征并保存到数据库
        
        Args:
            song_id: 歌曲ID
            audio_path: 音频文件路径
            
        Returns:
            风格特征对象
        """
        # 提取特征
        features = self.extract_features(audio_path)
        
        # 保存到数据库
        db_manager.save_style_features(
            song_id=song_id,
            features=features.to_dict(),
            style_embedding=np.array(features.style_embedding, dtype=np.float32)
        )
        
        return features


# 全局特征提取器实例
style_extractor = StyleFeatureExtractor()
