"""
端到端集成测试
测试完整的创作流程
"""
import pytest
import os
import tempfile
from pathlib import Path
import numpy as np
import soundfile as sf

from src.services import (
    song_search_service,
    style_extractor,
    copyright_detector,
    music_generator
)
from src.models.database import DatabaseManager


def create_test_audio(output_path: Path):
    """创建一个测试音频文件"""
    sr = 22050
    duration = 5
    t = np.linspace(0, duration, sr * duration, endpoint=False)
    y = np.sin(2 * np.pi * 440 * t) * 0.3  # 440Hz正弦波
    sf.write(str(output_path), y, sr)
    return output_path


def test_end_to_end_workflow():
    """测试完整的端到端流程"""
    # 1. 搜索一首歌曲
    songs = song_search_service.search_song(title="夜曲", artist="周杰伦")
    assert len(songs) >= 1
    selected_song = songs[0]
    assert selected_song.title == "夜曲"
    assert selected_song.artist == "周杰伦"
    
    # 2. 创建临时目录和数据库
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 初始化数据库
        db_manager = DatabaseManager(db_path=temp_path / "test_e2e.db")
        
        # 3. 创建测试音频文件并提取风格
        test_audio = temp_path / "test.wav"
        create_test_audio(test_audio)
        
        features = style_extractor.extract_features(test_audio)
        assert features.bpm > 0
        assert len(features.mfcc) > 0
        
        # 4. 保存风格特征到数据库
        db_manager.save_style_features(
            song_id="test_song_123",
            features=features,
            style_embedding=features.style_embedding
        )
        
        retrieved = db_manager.get_style_features("test_song_123")
        assert retrieved is not None
        
        # 5. 生成一首新歌
        generated = music_generator.generate_song(
            style_features=features,
            duration=10
        )
        
        assert generated.id is not None
        assert generated.audio_path is not None
        assert Path(generated.audio_path).exists()
        
        # 6. 保存到数据库
        db_manager.save_generated_song(
            song_id=generated.id,
            audio_path=generated.audio_path,
            style_features=features,
            lyrics="测试歌词",
            style_similarity=generated.style_similarity
        )
        
        # 7. 检测原创性
        # 先保存生成的歌曲到版权数据库
        copyright_detector.add_to_database(generated.id, Path(generated.audio_path))
        
        # 创建另一个音频用于检测
        another_audio = temp_path / "another.wav"
        t2 = np.linspace(0, 5, 22050 * 5, endpoint=False)
        y2 = np.sin(2 * np.pi * 880 * t2) * 0.3
        sf.write(str(another_audio), y2, 22050)
        
        # 测试版权检测功能能正常运行并返回报告
        report = copyright_detector.check_originality(another_audio)
        assert report is not None
        assert hasattr(report, 'is_original')
        assert hasattr(report, 'originality_score')
        assert 0 <= report.originality_score <= 1
        
        # 8. 从数据库获取最近的作品
        recent = db_manager.get_recent_generated(limit=5)
        assert len(recent) >= 1
        
        # 9. 清理生成的音频文件
        if Path(generated.audio_path).exists():
            os.unlink(generated.audio_path)
    
    print("✅ 端到端测试成功！")


if __name__ == "__main__":
    test_end_to_end_workflow()
    print("🎉 所有端到端测试通过！")
