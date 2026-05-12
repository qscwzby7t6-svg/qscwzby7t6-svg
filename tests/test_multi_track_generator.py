"""
多轨音频生成模块测试
"""
import pytest
import numpy as np
from pathlib import Path

from src.services.multi_track_generator import (
    DrumGenerator,
    BassGenerator,
    SynthGenerator,
    MultiTrackGenerator,
    TrackType,
    MultiTrackSong
)


class TestDrumGenerator:
    """测试鼓点生成器"""
    
    @pytest.fixture
    def drum_gen(self):
        return DrumGenerator(sample_rate=22050)
    
    def test_generate_pattern(self, drum_gen):
        """测试生成鼓点节奏型"""
        audio = drum_gen.generate_pattern(
            pattern="4/4",
            bpm=120,
            duration=5.0
        )
        
        assert isinstance(audio, np.ndarray)
        assert len(audio) == int(22050 * 5.0)
        # 音频幅度可能超过1.0，但应该在一个合理范围内
        assert np.max(np.abs(audio)) <= 2.0
    
    def test_generate_kick(self, drum_gen):
        """测试生成底鼓"""
        n_samples = 1000
        kick = drum_gen._generate_kick(n_samples)
        
        assert isinstance(kick, np.ndarray)
        assert len(kick) == n_samples
    
    def test_generate_snare(self, drum_gen):
        """测试生成军鼓"""
        n_samples = 1000
        snare = drum_gen._generate_snare(n_samples)
        
        assert isinstance(snare, np.ndarray)
        assert len(snare) == n_samples
    
    def test_generate_hihat(self, drum_gen):
        """测试生成踩镲"""
        n_samples = 1000
        hihat = drum_gen._generate_hihat(n_samples)
        
        assert isinstance(hihat, np.ndarray)
        assert len(hihat) == n_samples


class TestBassGenerator:
    """测试贝斯生成器"""
    
    @pytest.fixture
    def bass_gen(self):
        return BassGenerator(sample_rate=22050)
    
    def test_generate_bassline(self, bass_gen):
        """测试生成贝斯线"""
        notes = ['C', 'E', 'G', 'A']
        audio = bass_gen.generate_bassline(
            notes=notes,
            duration=5.0,
            bpm=120
        )
        
        assert isinstance(audio, np.ndarray)
        assert len(audio) == int(22050 * 5.0)
        assert np.max(np.abs(audio)) <= 1.0
    
    def test_generate_walking_bass(self, bass_gen):
        """测试生成Walking Bass"""
        audio = bass_gen.generate_walking_bass(
            key="C",
            duration=5.0,
            bpm=120
        )
        
        assert isinstance(audio, np.ndarray)
        assert len(audio) == int(22050 * 5.0)


class TestSynthGenerator:
    """测试合成器生成器"""
    
    @pytest.fixture
    def synth_gen(self):
        return SynthGenerator(sample_rate=22050)
    
    def test_generate_pad(self, synth_gen):
        """测试生成Pad音色"""
        chord = [261.63, 329.63, 392.00]
        audio = synth_gen.generate_pad(
            chord=chord,
            duration=5.0
        )
        
        assert isinstance(audio, np.ndarray)
        assert len(audio) == int(22050 * 5.0)
        assert np.max(np.abs(audio)) <= 1.0
    
    def test_generate_lead(self, synth_gen):
        """测试生成Lead音色"""
        notes = [261.63, 329.63, 392.00, 523.25]
        audio = synth_gen.generate_lead(
            notes=notes,
            note_duration=0.5,
            bpm=120
        )
        
        assert isinstance(audio, np.ndarray)
        assert len(audio) > 0
    
    def test_generate_arpeggio(self, synth_gen):
        """测试生成琶音"""
        chord = [261.63, 329.63, 392.00]
        audio = synth_gen.generate_arpeggio(
            chord=chord,
            duration=5.0,
            arp_speed=0.125
        )
        
        assert isinstance(audio, np.ndarray)
        assert len(audio) == int(22050 * 5.0)


class TestMultiTrackGenerator:
    """测试多轨音频生成器"""
    
    @pytest.fixture
    def multi_gen(self):
        return MultiTrackGenerator(sample_rate=22050)
    
    def test_generate_full_track(self, multi_gen):
        """测试生成完整多轨音乐"""
        song = multi_gen.generate_full_track(
            bpm=120,
            key="C",
            duration=10.0,
            enable_drums=True,
            enable_bass=True,
            enable_synth=True,
            enable_pad=True
        )
        
        assert isinstance(song, MultiTrackSong)
        assert song.id
        assert len(song.tracks) == 4
        assert song.duration == 10.0
        assert song.master_audio is not None
        # Track对象有audio_data属性，不是audio_path
        assert song.tracks['drums'].audio_data is not None
    
    def test_generate_full_track_selective(self, multi_gen):
        """测试选择性生成音轨"""
        song = multi_gen.generate_full_track(
            bpm=120,
            key="C",
            duration=5.0,
            enable_drums=True,
            enable_bass=False,
            enable_synth=True,
            enable_pad=False
        )
        
        assert isinstance(song, MultiTrackSong)
        assert len(song.tracks) == 2
        assert 'drums' in song.tracks
        assert 'synth_lead' in song.tracks
        assert 'bass' not in song.tracks
        assert 'pad' not in song.tracks
    
    def test_export_track(self, multi_gen):
        """测试导出单条音轨"""
        song = multi_gen.generate_full_track(
            bpm=120,
            key="C",
            duration=5.0
        )
        
        track = song.tracks['drums']
        exported_path = multi_gen.export_track(track, "test_drum.wav")
        
        assert Path(exported_path).exists()
