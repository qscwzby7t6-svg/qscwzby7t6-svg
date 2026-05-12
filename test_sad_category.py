#!/usr/bin/env python3
"""
测试：以忧伤分类播放量第一的歌曲进行仿写
"""
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

print("🎵 忧伤分类歌曲仿写测试")
print("=" * 70)

# 添加忧伤分类的映射
print("📋 步骤1: 检查音乐分类")
print(f"当前分类列表: {song_search_service.MUSIC_GENRES}")

# 获取忧伤/抒情分类的热门歌曲
print("\n🎼 步骤2: 获取忧伤/抒情分类播放量第一的歌曲")
sad_songs = song_search_service.get_top_songs_by_genre("抒情", limit=5)

if sad_songs:
    top_sad_song = sad_songs[0]
    print(f"✅ 找到忧伤分类播放量第一的歌曲!")
    print(f"   排名: TOP 1")
    print(f"   歌曲名称: {top_sad_song.title}")
    print(f"   歌手: {top_sad_song.artist}")
    print(f"   专辑: {top_sad_song.album}")
    if top_sad_song.play_count:
        print(f"   播放量: {top_sad_song.play_count:,}")
    print(f"   热度指数: {top_sad_song.trend_score}/100")
    print(f"   流派: {top_sad_song.genre}")
else:
    print("❌ 未找到忧伤分类的歌曲")
    exit(1)

# 创建测试音频并提取风格
print("\n🎨 步骤3: 提取歌曲风格特征")

with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    test_audio = temp_path / "sad_song.wav"
    
    # 生成带有忧伤情感的测试音频（使用较低的音调）
    sr = 22050
    duration = 10
    t = np.linspace(0, duration, sr * duration, endpoint=False)
    
    # 忧伤风格的音频（较低频率，较慢节奏）
    y = np.sin(2 * np.pi * 220 * t) * 0.4 + np.sin(2 * np.pi * 330 * t) * 0.2
    y += np.sin(2 * np.pi * 110 * t) * 0.15  # 添加低音
    
    sf.write(str(test_audio), y, sr)
    
    features = style_extractor.extract_features(test_audio)
    
    print(f"✅ 风格特征提取完成")
    print(f"   BPM: {features.bpm:.1f}")
    print(f"   调式: {features.key} {features.mode}")
    print(f"   频谱中心: {features.spectral_centroid:.1f}")

# 根据风格生成歌曲名称
print("\n🎤 步骤4: 根据忧伤风格生成歌曲名称")

style_dict = {
    'genre': top_sad_song.genre if top_sad_song.genre else ['ballad'],
    'bpm': features.bpm
}
generated_name = song_search_service.generate_song_name(style_dict)

print(f"✅ 生成忧伤风格歌曲名称: {generated_name}")

# 生成歌曲
print("\n🎶 步骤5: AI生成忧伤风格原创歌曲")

generated = music_generator.generate_song(
    style_features=features,
    lyrics_prompt="忧伤、思念、回忆",
    duration=25
)

print(f"✅ 歌曲生成完成")
print(f"   歌曲ID: {generated.id}")
print(f"   音频路径: {generated.audio_path}")
print(f"   时长: {generated.duration}秒")
print(f"   风格相似度: {generated.style_similarity:.2%}")

# 原创性检测
print("\n🛡️ 步骤6: 原创性检测")

report = copyright_detector.check_originality(Path(generated.audio_path))

print(f"✅ 原创性检测完成")
print(f"   是否原创: {'是 ✅' if report.is_original else '否 ⚠️'}")
print(f"   原创度评分: {report.originality_score:.2%}")

print("\n" + "=" * 70)
print("🎉 忧伤分类歌曲仿写测试完成！")
print("\n📝 最终作品信息:")
print(f"   🎵 参考歌曲: {top_sad_song.title} - {top_sad_song.artist}")
print(f"   💰 播放量: {top_sad_song.play_count:,}")
print(f"   📊 排名: 忧伤/抒情分类 TOP 1")
print(f"\n   🎶 生成歌曲名称: {generated_name}")
print(f"   🎨 风格相似度: {generated.style_similarity:.2%}")
print(f"   ✅ 原创度评分: {report.originality_score:.2%}")
print(f"   ⏱️ 时长: {generated.duration}秒")
print(f"   📁 音频路径: {generated.audio_path}")
print("\n💫 忧伤风格仿写成功！")
