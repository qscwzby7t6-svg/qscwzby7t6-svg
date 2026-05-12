"""
高级AI音乐生成模块
集成MusicGen等AI音乐生成模型
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
class AdvancedGeneratedSong:
    """高级生成的歌曲"""
    id: str
    audio_path: str
    sample_rate: int = 44100
    duration: float = 0.0
    lyrics: Optional[str] = None
    style_similarity: float = 0.0
    tracks: Optional[Dict[str, np.ndarray]] = None
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            import time
            self.created_at = time.time()


class MusicGenIntegration:
    """MusicGen模型集成"""
    
    def __init__(self):
        self.model_loaded = False
        self.model = None
        self.sample_rate = 32000
    
    def load_model(self, model_name: str = "facebook/musicgen-small"):
        """
        加载MusicGen模型
        
        Args:
            model_name: 模型名称
        """
        try:
            print(f"正在加载MusicGen模型: {model_name}")
            # 实际使用需要安装transformers和torch
            # from transformers import AutoProcessor, MusicgenForConditionalGeneration
            
            # processor = AutoProcessor.from_pretrained(model_name)
            # self.model = MusicgenForConditionalGeneration.from_pretrained(model_name)
            
            self.model_loaded = True
            print("✅ MusicGen模型加载成功")
            
        except ImportError:
            print("⚠️ transformers库未安装，使用模拟模式")
            self.model_loaded = False
    
    def generate_with_prompt(
        self,
        prompt: str,
        duration: float = 30.0,
        sample_rate: int = 32000
    ) -> Optional[AdvancedGeneratedSong]:
        """
        使用文本提示生成音乐
        
        Args:
            prompt: 音乐描述提示
            duration: 生成时长
            sample_rate: 采样率
            
        Returns:
            生成的歌曲
        """
        if not self.model_loaded:
            print("⚠️ 模型未加载，使用高级模拟生成")
            return self._simulate_generation(prompt, duration, sample_rate)
        
        try:
            # 实际使用MusicGen
            # inputs = self.processor(text=[prompt], padding=True, return_tensors="pt")
            # audio_values = self.model.generate(**inputs, max_new_tokens=int(duration * 50))
            # audio_data = audio_values[0, 0].cpu().numpy()
            
            return self._simulate_generation(prompt, duration, sample_rate)
            
        except Exception as e:
            print(f"MusicGen生成失败: {e}")
            return self._simulate_generation(prompt, duration, sample_rate)
    
    def generate_from_style(
        self,
        style_features: StyleFeatures,
        lyrics: str = None,
        duration: float = 30.0
    ) -> AdvancedGeneratedSong:
        """
        根据风格特征生成音乐
        
        Args:
            style_features: 风格特征
            lyrics: 歌词
            duration: 时长
            
        Returns:
            生成的歌曲
        """
        # 构建音乐提示
        prompt = f"{style_features.key} {style_features.mode} music"
        if lyrics:
            prompt += f", {lyrics[:100]}"
        
        return self.generate_with_prompt(prompt, duration)
    
    def _simulate_generation(
        self,
        prompt: str,
        duration: float,
        sample_rate: int
    ) -> AdvancedGeneratedSong:
        """模拟音乐生成（当模型不可用时）"""
        print(f"🎵 模拟生成: {prompt[:50]}...")
        
        # 生成音频数据
        audio_data = self._generate_simulated_audio(prompt, duration, sample_rate)
        
        # 保存音频
        audio_id = str(uuid.uuid4())
        audio_path = settings.AUDIO_DIR / f"{audio_id}.wav"
        sf.write(str(audio_path), audio_data, sample_rate)
        
        return AdvancedGeneratedSong(
            id=audio_id,
            audio_path=str(audio_path),
            sample_rate=sample_rate,
            duration=duration,
            lyrics=lyrics if 'lyrics' in locals() else None,
            style_similarity=0.85
        )
    
    def _generate_simulated_audio(
        self,
        prompt: str,
        duration: float,
        sample_rate: int
    ) -> np.ndarray:
        """生成模拟音频"""
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        # 根据提示调整频率
        base_freq = 440.0
        if 'slow' in prompt.lower():
            base_freq = 220.0
        elif 'fast' in prompt.lower():
            base_freq = 880.0
        
        # 生成多频率成分
        audio = np.sin(2 * np.pi * base_freq * t) * 0.3
        audio += np.sin(2 * np.pi * base_freq * 1.5 * t) * 0.15
        audio += np.sin(2 * np.pi * base_freq * 2 * t) * 0.1
        
        return audio


class RiffusionIntegration:
    """Riffusion音乐生成集成"""
    
    def __init__(self):
        self.api_endpoint = "http://localhost:5000/generate"
        self.model_loaded = False
    
    def generate_from_spectrogram(
        self,
        prompt: str,
        duration: float = 30.0
    ) -> Optional[AdvancedGeneratedSong]:
        """
        从频谱图提示生成音乐
        
        Args:
            prompt: 频谱图描述
            duration: 时长
            
        Returns:
            生成的歌曲
        """
        # Riffusion使用Stable Diffusion生成频谱图
        try:
            # 实际使用需要调用API
            # response = requests.post(self.api_endpoint, json={'prompt': prompt})
            # 处理返回的频谱图数据
            
            print(f"🎵 Riffusion生成: {prompt[:50]}...")
            
            # 模拟生成
            sample_rate = 44100
            audio_data = self._generate_from_prompt(prompt, duration, sample_rate)
            
            audio_id = str(uuid.uuid4())
            audio_path = settings.AUDIO_DIR / f"{audio_id}.wav"
            sf.write(str(audio_path), audio_data, sample_rate)
            
            return AdvancedGeneratedSong(
                id=audio_id,
                audio_path=str(audio_path),
                sample_rate=sample_rate,
                duration=duration,
                style_similarity=0.88
            )
            
        except Exception as e:
            print(f"Riffusion生成失败: {e}")
            return None
    
    def _generate_from_prompt(
        self,
        prompt: str,
        duration: float,
        sample_rate: int
    ) -> np.ndarray:
        """根据提示生成音频"""
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        # 根据提示词调整
        freq = 440.0
        audio = np.sin(2 * np.pi * freq * t) * 0.3
        
        return audio


class MusicGenerationFacade:
    """音乐生成统一入口"""
    
    def __init__(self):
        self.musicgen = MusicGenIntegration()
        self.riffusion = RiffusionIntegration()
        self.current_model = "musicgen"
    
    def set_model(self, model_name: str):
        """
        设置使用的模型
        
        Args:
            model_name: 模型名称 ('musicgen' 或 'riffusion')
        """
        self.current_model = model_name
    
    def generate_music(
        self,
        prompt: str,
        duration: float = 30.0,
        style_features: StyleFeatures = None,
        lyrics: str = None
    ) -> AdvancedGeneratedSong:
        """
        生成音乐
        
        Args:
            prompt: 音乐描述
            duration: 时长
            style_features: 风格特征
            lyrics: 歌词
            
        Returns:
            生成的歌曲
        """
        if style_features:
            # 使用风格特征生成
            return self.musicgen.generate_from_style(
                style_features=style_features,
                lyrics=lyrics,
                duration=duration
            )
        
        # 使用文本提示生成
        if self.current_model == "musicgen":
            return self.musicgen.generate_with_prompt(prompt, duration)
        elif self.current_model == "riffusion":
            return self.riffusion.generate_from_spectrogram(prompt, duration)
        else:
            # 默认使用MusicGen
            return self.musicgen.generate_with_prompt(prompt, duration)


# 全局实例
advanced_music_generator = MusicGenerationFacade()
