"""
多轨音频生成模块
支持鼓点、贝斯、合成器等多轨音频生成
"""
import numpy as np
import soundfile as sf
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from src.config import settings


class TrackType(Enum):
    """音轨类型"""
    DRUMS = "drums"
    BASS = "bass"
    SYNTH = "synth"
    MELODY = "melody"
    PAD = "pad"
    VOCAL = "vocal"


@dataclass
class Track:
    """单条音轨"""
    name: str
    track_type: TrackType
    audio_data: np.ndarray
    sample_rate: int
    volume: float = 1.0
    pan: float = 0.0  # -1 (左) to 1 (右)
    muted: bool = False
    solo: bool = False


@dataclass
class MultiTrackSong:
    """多轨歌曲"""
    id: str
    tracks: Dict[str, Track]
    master_audio: Optional[np.ndarray] = None
    sample_rate: int = 44100
    duration: float = 0.0
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            import time
            self.created_at = time.time()


class DrumGenerator:
    """鼓点生成器"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.kick_freq = 60.0
        self.snare_freq = 200.0
        self.hihat_freq = 8000.0
    
    def generate_pattern(
        self,
        pattern: str = "4/4",
        bpm: int = 120,
        duration: float = 10.0
    ) -> np.ndarray:
        """
        生成鼓点节奏型
        
        Args:
            pattern: 节拍模式
            bpm: 每分钟节拍数
            duration: 时长
            
        Returns:
            鼓点音频数据
        """
        n_samples = int(self.sample_rate * duration)
        audio = np.zeros(n_samples)
        
        beat_samples = int(self.sample_rate * 60.0 / bpm)
        
        pattern_map = {
            "4/4": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # 4/4拍
            "3/4": [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],  # 3/4拍
            "2/4": [1, 0, 0, 0, 1, 0, 0, 0],  # 2/4拍
        }
        
        hits = pattern_map.get(pattern, pattern_map["4/4"])
        
        for i, hit in enumerate(hits):
            if hit:
                start = i * beat_samples // len(hits)
                if start >= n_samples:
                    break
                end = min(start + beat_samples // 2, n_samples)
                segment_length = end - start
                
                # Kick
                kick = self._generate_kick(segment_length)
                audio[start:end] += kick
                
                # Snare on 2, 4
                if i in [4, 12]:
                    snare = self._generate_snare(segment_length)
                    audio[start:end] += snare
                
                # Hi-hat
                hihat = self._generate_hihat(segment_length)
                audio[start:end] += hihat * 0.3
        
        return audio * 0.8
    
    def _generate_kick(self, n_samples: int) -> np.ndarray:
        """生成底鼓声音"""
        t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
        freq_env = np.exp(-t * 20)
        return freq_env * np.sin(2 * np.pi * self.kick_freq * t)
    
    def _generate_snare(self, n_samples: int) -> np.ndarray:
        """生成军鼓声音"""
        t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
        noise = np.random.randn(n_samples) * 0.5
        tone = np.sin(2 * np.pi * self.snare_freq * t) * 0.5
        return (noise + tone) * np.exp(-t * 15)
    
    def _generate_hihat(self, n_samples: int) -> np.ndarray:
        """生成踩镲声音"""
        t = np.linspace(0, n_samples / self.sample_rate, n_samples, endpoint=False)
        noise = np.random.randn(n_samples)
        return noise * np.exp(-t * 30) * 0.3


class BassGenerator:
    """贝斯生成器"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bass_notes = {
            'C': 65.41, 'D': 73.42, 'E': 82.41, 'F': 87.31,
            'G': 98.00, 'A': 110.00, 'B': 123.47
        }
    
    def generate_bassline(
        self,
        notes: List[str],
        duration: float = 10.0,
        bpm: int = 120
    ) -> np.ndarray:
        """
        生成贝斯线
        
        Args:
            notes: 音符列表
            duration: 时长
            bpm: 节拍速度
            
        Returns:
            贝斯音频数据
        """
        n_samples = int(self.sample_rate * duration)
        audio = np.zeros(n_samples)
        
        beat_duration = 60.0 / bpm
        note_duration = beat_duration * 2
        note_samples = int(self.sample_rate * note_duration)
        
        for i, note in enumerate(notes):
            freq = self.bass_notes.get(note, 110.0)
            start = int(i * note_samples)
            if start >= n_samples:
                break
            end = min(start + note_samples, n_samples)
            segment_length = end - start
            
            t = np.linspace(0, segment_length / self.sample_rate, segment_length, endpoint=False)
            
            # 生成贝斯音色
            bass_tone = np.sin(2 * np.pi * freq * t) * 0.6
            bass_tone += np.sin(2 * np.pi * freq * 2 * t) * 0.2
            
            # ADSR包络
            attack = int(0.02 * len(t))
            decay = int(0.05 * len(t))
            sustain = int(0.7 * len(t))
            release = len(t) - attack - decay - sustain
            
            envelope = np.ones(len(t))
            if attack > 0:
                envelope[:attack] = np.linspace(0, 1, attack)
            if decay > 0:
                envelope[attack:attack+decay] = np.linspace(1, 0.7, decay)
            if sustain > 0:
                envelope[attack+decay:attack+decay+sustain] = 0.7
            if release > 0:
                envelope[-release:] = np.linspace(0.7, 0, release)
            
            audio[start:end] = bass_tone * envelope
        
        return audio * 0.7
    
    def generate_walking_bass(
        self,
        key: str = "C",
        duration: float = 10.0,
        bpm: int = 120
    ) -> np.ndarray:
        """生成Walking Bass"""
        notes = ['C', 'E', 'G', 'A', 'C', 'D', 'E', 'G'] * 4
        num_notes = max(1, int(duration / (60/bpm) * 2))
        return self.generate_bassline(notes[:num_notes], duration, bpm)


class SynthGenerator:
    """合成器生成器"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def generate_pad(
        self,
        chord: List[float],
        duration: float = 10.0
    ) -> np.ndarray:
        """
        生成Pad音色
        
        Args:
            chord: 和弦频率列表
            duration: 时长
            
        Returns:
            Pad音频数据
        """
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        audio = np.zeros(n_samples)
        
        for freq in chord:
            # 添加谐波
            synth = np.sin(2 * np.pi * freq * t) * 0.4
            synth += np.sin(2 * np.pi * freq * 2 * t) * 0.2
            synth += np.sin(2 * np.pi * freq * 3 * t) * 0.1
            
            audio += synth
        
        # 缓慢的包络
        attack = int(0.5 * self.sample_rate)
        release = int(1.0 * self.sample_rate)
        
        envelope = np.ones(n_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        return audio * envelope * 0.3
    
    def generate_lead(
        self,
        notes: List[float],
        note_duration: float = 0.5,
        bpm: int = 120
    ) -> np.ndarray:
        """生成主旋律合成器音色"""
        total_duration = len(notes) * note_duration
        n_samples = int(self.sample_rate * total_duration)
        audio = np.zeros(n_samples)
        
        note_samples = int(self.sample_rate * note_duration)
        
        for i, freq in enumerate(notes):
            start = int(i * note_samples)
            end = min(start + note_samples, n_samples)
            
            t = np.linspace(0, (end - start) / self.sample_rate, end - start, endpoint=False)
            
            # 主旋律音色
            lead = np.sin(2 * np.pi * freq * t) * 0.5
            lead += np.sin(2 * np.pi * freq * 2 * t) * 0.2
            
            audio[start:end] = lead
        
        return audio * 0.6
    
    def generate_arpeggio(
        self,
        chord: List[float],
        duration: float = 10.0,
        arp_speed: float = 0.125
    ) -> np.ndarray:
        """生成琶音"""
        n_samples = int(self.sample_rate * duration)
        audio = np.zeros(n_samples)
        
        arp_samples = int(self.sample_rate * arp_speed)
        num_notes = int(duration / arp_speed)
        
        for i in range(num_notes):
            freq = chord[i % len(chord)]
            start = int(i * arp_samples)
            end = min(start + arp_samples, n_samples)
            
            t = np.linspace(0, (end - start) / self.sample_rate, end - start, endpoint=False)
            
            arp_note = np.sin(2 * np.pi * freq * t) * 0.4
            arp_note += np.sin(2 * np.pi * freq * 3 * t) * 0.1
            
            # 包络
            envelope = np.exp(-t * 5)
            
            audio[start:end] = arp_note * envelope
        
        return audio * 0.5


class MultiTrackGenerator:
    """多轨音频生成器"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.drum_gen = DrumGenerator(sample_rate)
        self.bass_gen = BassGenerator(sample_rate)
        self.synth_gen = SynthGenerator(sample_rate)
    
    def generate_full_track(
        self,
        bpm: int = 120,
        key: str = "C",
        duration: float = 30.0,
        enable_drums: bool = True,
        enable_bass: bool = True,
        enable_synth: bool = True,
        enable_pad: bool = True
    ) -> MultiTrackSong:
        """
        生成完整多轨音乐
        
        Args:
            bpm: 节拍速度
            key: 调性
            duration: 时长
            enable_*: 是否启用各音轨
            
        Returns:
            多轨歌曲对象
        """
        song_id = str(uuid.uuid4())
        tracks = {}
        
        # 鼓点轨
        if enable_drums:
            drum_audio = self.drum_gen.generate_pattern(
                pattern="4/4",
                bpm=bpm,
                duration=duration
            )
            tracks['drums'] = Track(
                name="Drums",
                track_type=TrackType.DRUMS,
                audio_data=drum_audio,
                sample_rate=self.sample_rate,
                volume=0.8
            )
        
        # 贝斯轨
        if enable_bass:
            bass_notes = ['C', 'E', 'G', 'A', 'C', 'G', 'E', 'G']
            bass_audio = self.bass_gen.generate_bassline(
                notes=bass_notes,
                duration=duration,
                bpm=bpm
            )
            tracks['bass'] = Track(
                name="Bass",
                track_type=TrackType.BASS,
                audio_data=bass_audio,
                sample_rate=self.sample_rate,
                volume=0.75
            )
        
        # 合成器Lead轨
        if enable_synth:
            lead_notes = [261.63, 329.63, 392.00, 523.25] * int(duration / 2)
            synth_audio = self.synth_gen.generate_lead(
                notes=lead_notes,
                note_duration=0.5,
                bpm=bpm
            )
            tracks['synth_lead'] = Track(
                name="Synth Lead",
                track_type=TrackType.SYNTH,
                audio_data=synth_audio,
                sample_rate=self.sample_rate,
                volume=0.6
            )
        
        # Pad轨
        if enable_pad:
            chord_freqs = [261.63, 329.63, 392.00]  # C大调和弦
            pad_audio = self.synth_gen.generate_pad(
                chord=chord_freqs,
                duration=duration
            )
            tracks['pad'] = Track(
                name="Pad",
                track_type=TrackType.PAD,
                audio_data=pad_audio,
                sample_rate=self.sample_rate,
                volume=0.4
            )
        
        # 混合所有音轨
        master_audio = self._mix_tracks(tracks)
        
        # 保存主音频
        audio_path = settings.AUDIO_DIR / f"{song_id}_master.wav"
        sf.write(str(audio_path), master_audio, self.sample_rate)
        
        return MultiTrackSong(
            id=song_id,
            tracks=tracks,
            master_audio=master_audio,
            sample_rate=self.sample_rate,
            duration=duration
        )
    
    def _mix_tracks(self, tracks: Dict[str, Track]) -> np.ndarray:
        """混合所有音轨"""
        if not tracks:
            return np.array([])
        
        max_length = max(len(t.audio_data) for t in tracks.values())
        master = np.zeros(max_length)
        
        for track in tracks.values():
            if track.muted:
                continue
            
            # 调整音量
            audio = track.audio_data * track.volume
            
            # 调整声像
            if track.pan > 0:
                # 右声道增强
                audio_r = audio * (1 + track.pan * 0.3)
                audio_l = audio * (1 - track.pan * 0.3)
                # 这里简化为单声道，实际应返回立体声
                master[:len(audio)] += (audio_l + audio_r) / 2
            else:
                master[:len(audio)] += audio
        
        # 限制幅度防止削波
        master = np.clip(master, -1.0, 1.0)
        
        return master
    
    def export_track(self, track: Track, filename: str) -> str:
        """导出单条音轨"""
        audio_path = settings.AUDIO_DIR / filename
        sf.write(str(audio_path), track.audio_data, track.sample_rate)
        return str(audio_path)


# 全局实例
multi_track_generator = MultiTrackGenerator()
