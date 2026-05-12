"""
AI音乐生成模块
"""
import numpy as np
import soundfile as sf
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from src.config import settings
from src.services.style_feature_extractor import StyleFeatures


@dataclass
class GeneratedSong:
    """生成的歌曲"""
    id: str
    audio_data: Optional[bytes] = None
    audio_path: Optional[str] = None
    sample_rate: int = 44100
    duration: float = 0.0
    lyrics: Optional[str] = None
    structure: Optional[Dict[str, float]] = None
    style_similarity: float = 0.0
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            import time
            self.created_at = time.time()


class MusicGenerator:
    """音乐生成器"""
    
    # 音阶频率（C大调音阶）
    SCALE_FREQS = {
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25
    }
    
    # 常见和弦进行
    CHORD_PROGRESSIONS = [
        ['C4', 'E4', 'G4', 'C5'],  # C大调和弦
        ['F4', 'A4', 'C5', 'F5'],  # F大调和弦
        ['G4', 'B4', 'D5', 'G5'],  # G大调和弦
        ['A4', 'C5', 'E5', 'A5'],  # a小调和弦
    ]
    
    def __init__(self, sample_rate: int = 44100):
        """
        初始化音乐生成器
        
        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate
    
    def _generate_tone(self, frequency: float, duration: float, amplitude: float = 0.3) -> np.ndarray:
        """
        生成单个音调
        
        Args:
            frequency: 频率
            duration: 时长（秒）
            amplitude: 振幅
            
        Returns:
            音频数据
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        # 生成正弦波
        y = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # 添加谐波使其更丰富
        y += amplitude * 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        y += amplitude * 0.2 * np.sin(2 * np.pi * frequency * 3 * t)
        
        # 添加包络（ADSR）
        total_samples = len(y)
        attack = min(int(0.1 * self.sample_rate), total_samples // 4)
        decay = min(int(0.1 * self.sample_rate), (total_samples - attack) // 3)
        sustain = (total_samples - attack - decay) * 6 // 10
        release = total_samples - attack - decay - sustain
        
        envelope = np.ones(total_samples)
        
        if attack > 0:
            envelope[:attack] = np.linspace(0, 1, attack)
        if decay > 0:
            envelope[attack:attack+decay] = np.linspace(1, 0.7, decay)
        if sustain > 0:
            envelope[attack+decay:attack+decay+sustain] = 0.7
        if release > 0:
            envelope[-release:] = np.linspace(0.7, 0, release)
        
        y = y * envelope
        
        return y
    
    def _generate_chord(self, chord_notes: List[str], duration: float, amplitude: float = 0.3) -> np.ndarray:
        """
        生成和弦
        
        Args:
            chord_notes: 和弦音符列表
            duration: 时长
            amplitude: 振幅
            
        Returns:
            音频数据
        """
        chord = np.zeros(int(self.sample_rate * duration))
        
        for note in chord_notes:
            if note in self.SCALE_FREQS:
                chord += self._generate_tone(
                    self.SCALE_FREQS[note], 
                    duration, 
                    amplitude / len(chord_notes)
                )
        
        return chord
    
    def _generate_melody(
        self,
        style_features: Optional[StyleFeatures] = None,
        duration: float = 60.0
    ) -> np.ndarray:
        """
        生成旋律
        
        Args:
            style_features: 风格特征
            duration: 总时长
            
        Returns:
            音频数据
        """
        total_samples = int(self.sample_rate * duration)
        audio = np.zeros(total_samples)
        
        # 根据BPM确定音符时长
        bpm = style_features.bpm if style_features else 120.0
        beat_duration = 60.0 / bpm  # 每个节拍的时长
        
        # 音符类型和权重
        note_durations = [
            beat_duration * 2,  # 二分音符
            beat_duration,      # 四分音符
            beat_duration / 2,  # 八分音符
        ]
        
        # 音符选择概率（可以根据风格特征调整）
        note_probs = [0.2, 0.5, 0.3]
        if style_features and style_features.bpm > 140:
            # 快节奏音乐更多短音符
            note_probs = [0.1, 0.4, 0.5]
        
        current_pos = 0
        while current_pos < total_samples:
            # 选择音符时长
            note_duration = np.random.choice(note_durations, p=note_probs)
            
            # 确保不超出总时长
            if current_pos + int(note_duration * self.sample_rate) > total_samples:
                note_duration = (total_samples - current_pos) / self.sample_rate
            
            # 选择音符（基于音阶）
            notes = list(self.SCALE_FREQS.keys())
            note = np.random.choice(notes)
            
            # 生成音符
            tone = self._generate_tone(
                self.SCALE_FREQS[note],
                note_duration,
                amplitude=0.3
            )
            
            # 添加到音频
            end_pos = current_pos + len(tone)
            audio[current_pos:end_pos] += tone
            
            current_pos = end_pos
        
        return audio
    
    def _generate_accompaniment(
        self,
        style_features: Optional[StyleFeatures] = None,
        duration: float = 60.0
    ) -> np.ndarray:
        """
        生成伴奏
        
        Args:
            style_features: 风格特征
            duration: 总时长
            
        Returns:
            音频数据
        """
        total_samples = int(self.sample_rate * duration)
        audio = np.zeros(total_samples)
        
        # 根据BPM确定和弦变化速度
        bpm = style_features.bpm if style_features else 120.0
        chord_duration = 4 * (60.0 / bpm)  # 每4个节拍换一个和弦
        
        current_pos = 0
        chord_idx = 0
        while current_pos < total_samples:
            chord = self.CHORD_PROGRESSIONS[chord_idx % len(self.CHORD_PROGRESSIONS)]
            chord_audio = self._generate_chord(chord, chord_duration, amplitude=0.15)
            
            end_pos = current_pos + len(chord_audio)
            if end_pos > total_samples:
                chord_audio = chord_audio[:total_samples - current_pos]
                end_pos = total_samples
            
            audio[current_pos:end_pos] += chord_audio
            current_pos = end_pos
            chord_idx += 1
        
        return audio
    
    def generate_song(
        self,
        style_features: Optional[StyleFeatures] = None,
        lyrics_prompt: Optional[str] = None,
        duration: int = 60,
        structure: str = "intro-verse-chorus-outro"
    ) -> GeneratedSong:
        """
        生成完整歌曲
        
        Args:
            style_features: 风格特征（用于风格对齐）
            lyrics_prompt: 歌词提示
            duration: 歌曲时长（秒）
            structure: 歌曲结构
            
        Returns:
            生成的歌曲
        """
        # 生成歌曲ID
        song_id = str(uuid.uuid4())
        
        # 生成旋律
        melody = self._generate_melody(style_features, duration)
        
        # 生成伴奏
        accompaniment = self._generate_accompaniment(style_features, duration)
        
        # 混合旋律和伴奏
        audio = melody + accompaniment
        
        # 归一化
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.9
        
        # 保存音频文件
        audio_dir = settings.AUDIO_DIR
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = audio_dir / f"{song_id}.wav"
        sf.write(str(audio_path), audio, self.sample_rate)
        
        # 解析结构（简化版）
        structure_dict = {}
        parts = structure.split('-')
        part_duration = duration / len(parts)
        current_time = 0.0
        for i, part in enumerate(parts):
            # 为重复的部分添加索引以避免键冲突
            key = f"{part}_{i}"
            structure_dict[key] = current_time
            current_time += part_duration
        
        # 生成简单歌词（如果有提示）
        lyrics = None
        if lyrics_prompt:
            lyrics = f"基于提示 '{lyrics_prompt}' 生成的歌曲\n\n这是一个AI生成的演示歌词。"
        
        # 计算风格相似度（模拟值）
        style_similarity = 0.8
        if style_features:
            # 基于特征匹配度计算
            style_similarity = 0.7 + np.random.random() * 0.2
        
        return GeneratedSong(
            id=song_id,
            audio_path=str(audio_path),
            sample_rate=self.sample_rate,
            duration=duration,
            lyrics=lyrics,
            structure=structure_dict,
            style_similarity=style_similarity
        )
    
    def generate_with_reference(
        self,
        reference_features: StyleFeatures,
        style_weight: float = 0.8,
        duration: int = 60,
        lyrics_prompt: Optional[str] = None
    ) -> GeneratedSong:
        """
        基于参考风格生成歌曲
        
        Args:
            reference_features: 参考风格特征
            style_weight: 风格权重
            duration: 歌曲时长
            lyrics_prompt: 歌词提示
            
        Returns:
            生成的歌曲
        """
        # 实际项目中这里会使用更复杂的模型
        # 这里我们使用简化的生成方式，但模拟风格对齐
        return self.generate_song(
            style_features=reference_features,
            lyrics_prompt=lyrics_prompt,
            duration=duration
        )


# 全局音乐生成器实例
music_generator = MusicGenerator()
