"""
版权检测与原创性验证模块
"""
import numpy as np
import librosa
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

from src.config import settings


@dataclass
class OriginalityReport:
    """原创性报告"""
    is_original: bool
    originality_score: float  # 0-1，越高越原创
    similar_songs: List[Dict[str, Any]]
    melody_similarity: Optional[float] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class MatchResult:
    """匹配结果"""
    song_id: str
    title: str
    artist: str
    similarity: float
    matched_segments: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.matched_segments is None:
            self.matched_segments = []


class CopyrightDetector:
    """版权检测器"""
    
    def __init__(self, sample_rate: int = 22050):
        """
        初始化版权检测器
        
        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate
        # 简单的音频指纹数据库（实际项目中应该使用更复杂的方案）
        self.fingerprint_database: Dict[str, Tuple[np.ndarray, Dict[str, Any]]] = {}
    
    def generate_fingerprint(self, audio_path: Path) -> np.ndarray:
        """
        生成音频指纹
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            音频指纹（numpy数组）
        """
        # 加载音频
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate, duration=30)
        
        # 提取多个特征作为指纹
        # 1. 梅尔频谱图
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
        
        # 2. MFCC特征
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # 3. 色度特征
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # 4. 频谱质心
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        
        # 将特征组合成指纹（使用统计特征降维）
        fingerprint_parts = []
        
        # 对每个特征计算统计量
        for feature in [mel_spectrogram_db, mfcc, chroma, spectral_centroid]:
            fingerprint_parts.extend([
                np.mean(feature),
                np.std(feature),
                np.percentile(feature, 25),
                np.percentile(feature, 50),
                np.percentile(feature, 75)
            ])
        
        # 计算频谱通量的统计特征
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        fingerprint_parts.extend([
            np.mean(onset_env),
            np.std(onset_env),
            np.max(onset_env) if len(onset_env) > 0 else 0.0
        ])
        
        fingerprint = np.array(fingerprint_parts, dtype=np.float32)
        
        # 归一化指纹
        if np.std(fingerprint) > 0:
            fingerprint = (fingerprint - np.mean(fingerprint)) / np.std(fingerprint)
        
        return fingerprint
    
    def _compute_similarity(self, fp1: np.ndarray, fp2: np.ndarray) -> float:
        """
        计算两个指纹之间的相似度（余弦相似度）
        
        Args:
            fp1: 第一个指纹
            fp2: 第二个指纹
            
        Returns:
            相似度（0-1）
        """
        # 余弦相似度
        dot_product = np.dot(fp1, fp2)
        norm1 = np.linalg.norm(fp1)
        norm2 = np.linalg.norm(fp2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        cosine_similarity = dot_product / (norm1 * norm2)
        
        # 转换到0-1范围
        return float((cosine_similarity + 1) / 2)
    
    def add_to_database(self, song_id: str, audio_path: Path, metadata: Optional[Dict[str, Any]] = None):
        """
        将歌曲添加到数据库
        
        Args:
            song_id: 歌曲ID
            audio_path: 音频文件路径
            metadata: 元数据
        """
        fingerprint = self.generate_fingerprint(audio_path)
        self.fingerprint_database[song_id] = (fingerprint, metadata or {})
    
    def search_similar(self, audio_path: Path, top_k: int = 5) -> List[MatchResult]:
        """
        搜索相似的歌曲
        
        Args:
            audio_path: 查询音频路径
            top_k: 返回的最相似歌曲数量
            
        Returns:
            匹配结果列表
        """
        query_fingerprint = self.generate_fingerprint(audio_path)
        
        results = []
        for song_id, (fp, metadata) in self.fingerprint_database.items():
            similarity = self._compute_similarity(query_fingerprint, fp)
            results.append({
                'song_id': song_id,
                'similarity': similarity,
                'metadata': metadata
            })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 转换为MatchResult对象
        match_results = []
        for result in results[:top_k]:
            metadata = result['metadata']
            match_results.append(MatchResult(
                song_id=result['song_id'],
                title=metadata.get('title', 'Unknown'),
                artist=metadata.get('artist', 'Unknown'),
                similarity=result['similarity'],
                matched_segments=[]
            ))
        
        return match_results
    
    def check_originality(
        self,
        audio_path: Path,
        reference_audio: Optional[Path] = None,
        similarity_threshold: float = 0.7,
        originality_threshold: float = 0.6
    ) -> OriginalityReport:
        """
        检查原创性
        
        Args:
            audio_path: 要检查的音频路径
            reference_audio: 参考音频路径（可选，用于和特定歌曲比较）
            similarity_threshold: 相似度阈值（超过此值视为相似）
            originality_threshold: 原创性阈值（低于此值视为不够原创）
            
        Returns:
            原创性报告
        """
        # 搜索相似歌曲
        similar_songs = self.search_similar(audio_path, top_k=5)
        
        # 如果有参考音频，计算和参考音频的相似度
        melody_similarity = None
        if reference_audio and reference_audio.exists():
            ref_fp = self.generate_fingerprint(reference_audio)
            query_fp = self.generate_fingerprint(audio_path)
            melody_similarity = self._compute_similarity(ref_fp, query_fp)
        
        # 计算原创性分数
        # 如果没有相似歌曲，原创性高
        if not similar_songs:
            originality_score = 0.95
        else:
            # 基于最相似的歌曲计算原创性
            top_similarity = similar_songs[0].similarity
            # 原创性分数和相似度成反比
            originality_score = max(0.0, min(1.0, 1.0 - top_similarity))
        
        # 生成修改建议
        recommendations = []
        if originality_score < originality_threshold:
            recommendations.append(
                f"检测到与歌曲 '{similar_songs[0].title}' 的相似度较高 ({similar_songs[0].similarity:.2f})，建议增加原创元素"
            )
        
        if melody_similarity and melody_similarity > 0.8:
            recommendations.append(
                f"与参考歌曲的旋律相似度较高 ({melody_similarity:.2f})，建议调整旋律线条"
            )
        
        # 判断是否原创
        is_original = originality_score >= originality_threshold
        
        # 转换similar_songs为字典格式
        similar_songs_dict = [
            {
                'song_id': s.song_id,
                'title': s.title,
                'artist': s.artist,
                'similarity': s.similarity
            }
            for s in similar_songs
        ]
        
        return OriginalityReport(
            is_original=is_original,
            originality_score=originality_score,
            similar_songs=similar_songs_dict,
            melody_similarity=melody_similarity,
            recommendations=recommendations
        )


# 全局版权检测器实例
copyright_detector = CopyrightDetector()
