"""
数据模型定义模块
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SongInfo(BaseModel):
    """歌曲基础信息"""
    id: str = Field(..., description="歌曲唯一标识")
    title: str = Field(..., description="歌曲标题")
    artist: str = Field(..., description="艺术家")
    album: Optional[str] = Field(None, description="专辑名称")
    cover_url: Optional[str] = Field(None, description="封面图片URL")
    duration: Optional[int] = Field(None, description="歌曲时长（秒）")


class SongMetadata(SongInfo):
    """歌曲详细元数据"""
    genre: Optional[List[str]] = Field(None, description="音乐流派")
    release_date: Optional[str] = Field(None, description="发行日期")
    lyrics: Optional[str] = Field(None, description="歌词")
    bpm: Optional[float] = Field(None, description="BPM（每分钟节拍数）")
    key: Optional[str] = Field(None, description="调式")


class StyleFeatures(BaseModel):
    """风格特征"""
    # 声学特征
    bpm: float = Field(..., description="BPM")
    key: str = Field(..., description="调式")
    mode: str = Field(..., description="大调/小调")
    chord_progression: Optional[List[str]] = Field(None, description="和声进行")
    time_signature: str = Field("4/4", description="拍号")
    
    # 频谱特征
    spectral_centroid: float = Field(..., description="频谱质心")
    spectral_bandwidth: float = Field(..., description="频谱带宽")
    spectral_rolloff: float = Field(..., description="频谱滚降点")
    mfcc: List[float] = Field(..., description="MFCC特征（13维）")
    
    # 节奏特征
    tempo: float = Field(..., description=" tempo")
    beat_frames: Optional[List[int]] = Field(None, description="节拍帧位置")
    
    # 风格向量
    style_embedding: List[float] = Field(..., description="风格向量（128维）")


class GeneratedSong(BaseModel):
    """生成的歌曲"""
    id: str = Field(..., description="生成作品唯一标识")
    audio_data: Optional[bytes] = Field(None, description="音频数据（WAV格式）")
    audio_path: Optional[str] = Field(None, description="音频文件路径")
    sample_rate: int = Field(44100, description="采样率")
    duration: float = Field(..., description="时长（秒）")
    lyrics: Optional[str] = Field(None, description="歌词")
    structure: Optional[Dict[str, float]] = Field(None, description="歌曲结构（各部分时间点）")
    style_similarity: float = Field(..., description="与参考风格的相似度")
    tracks: Optional[Dict[str, bytes]] = Field(None, description="多轨分轨")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class OriginalityReport(BaseModel):
    """原创性报告"""
    is_original: bool = Field(..., description="是否原创")
    originality_score: float = Field(..., description="原创性评分（0-1）")
    similar_songs: List[Dict[str, Any]] = Field(default_factory=list, description="相似歌曲列表")
    melody_similarity: Optional[float] = Field(None, description="旋律相似度")
    recommendations: List[str] = Field(default_factory=list, description="修改建议")


class MatchResult(BaseModel):
    """匹配结果"""
    song_id: str = Field(..., description="歌曲ID")
    title: str = Field(..., description="歌曲标题")
    artist: str = Field(..., description="艺术家")
    similarity: float = Field(..., description="相似度")
    matched_segments: List[Dict[str, Any]] = Field(default_factory=list, description="匹配片段")


class GenerationRequest(BaseModel):
    """歌曲生成请求"""
    song_name: str = Field(..., description="参考歌曲名称")
    artist: str = Field(..., description="参考艺术家")
    lyrics_prompt: Optional[str] = Field(None, description="歌词提示")
    duration: int = Field(180, description="生成时长（秒）")
    style_weight: float = Field(0.8, description="风格权重（0-1）")


class GenerationResponse(BaseModel):
    """歌曲生成响应"""
    request_id: str = Field(..., description="请求ID")
    status: str = Field(..., description="状态：pending/processing/completed/failed")
    generated_song: Optional[GeneratedSong] = Field(None, description="生成的歌曲")
    originality_report: Optional[OriginalityReport] = Field(None, description="原创性报告")
    error_message: Optional[str] = Field(None, description="错误信息")
