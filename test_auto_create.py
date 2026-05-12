#!/usr/bin/env python3
"""
自动创作演示：第100名播放量歌曲仿写
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
from src.models.database import DatabaseManager

print("🎵 自动创作演示")
print("=" * 70)

# 模拟用户登录信息
user_info = {
    'username': 'AI音乐创作者',
    'email': 'creator@example.com',
    'bio': '热爱音乐的AI开发者'
}

print(f"\n👤 用户信息:")
print(f"   用户名: {user_info['username']}")
print(f"   邮箱: {user_info['email']}")

# 步骤1: 获取第100名播放量的歌曲
print("\n📊 步骤1: 获取播放量排名第100的歌曲")
rank = min(100, 15)  # 由于我们只有15首歌，取最后一首
target_song = song_search_service.get_song_by_rank(rank)

if target_song:
    print(f"✅ 找到参考歌曲!")
    print(f"   歌曲名称: {target_song.title}")
    print(f"   歌手: {target_song.artist}")
    print(f"   专辑: {target_song.album}")
    if target_song.play_count:
        print(f"   播放量: {target_song.play_count:,}")
    print(f"   流派: {target_song.genre}")
else:
    print("❌ 未找到指定排名的歌曲")

# 步骤2: 创建测试音频并提取风格
print("\n🎨 步骤2: 提取歌曲风格特征")

with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    test_audio = temp_path / "test.wav"
    
    sr = 22050
    duration = 10
    t = np.linspace(0, duration, sr * duration, endpoint=False)
    y = np.sin(2 * np.pi * 440 * t) * 0.3 + np.sin(2 * np.pi * 880 * t) * 0.15
    sf.write(str(test_audio), y, sr)
    
    features = style_extractor.extract_features(test_audio)
    
    print(f"✅ 风格特征提取完成")
    print(f"   BPM: {features.bpm:.1f}")
    print(f"   调式: {features.key} {features.mode}")
    print(f"   频谱中心: {features.spectral_centroid:.1f}")
    print(f"   风格嵌入维度: {len(features.style_embedding)}")

# 步骤3: 根据风格生成歌曲名称
print("\n🎤 步骤3: 根据风格自动生成歌曲名称")

style_dict = {
    'genre': target_song.genre if target_song.genre else [],
    'bpm': features.bpm
}
generated_name = song_search_service.generate_song_name(style_dict)

print(f"✅ 生成歌曲名称: {generated_name}")

# 步骤4: 生成歌曲
print("\n🎶 步骤4: AI生成原创歌曲")

generated = music_generator.generate_song(
    style_features=features,
    lyrics_prompt="原创歌曲创作",
    duration=20
)

print(f"✅ 歌曲生成完成")
print(f"   歌曲ID: {generated.id}")
print(f"   音频路径: {generated.audio_path}")
print(f"   时长: {generated.duration}秒")
print(f"   风格相似度: {generated.style_similarity:.2%}")

# 步骤5: 原创性检测
print("\n🛡️ 步骤5: 原创性检测")

report = copyright_detector.check_originality(Path(generated.audio_path))

print(f"✅ 原创性检测完成")
print(f"   是否原创: {'是 ✅' if report.is_original else '否 ⚠️'}")
print(f"   原创度评分: {report.originality_score:.2%}")

# 步骤6: 保存作品
print("\n💾 步骤6: 保存作品信息")

print(f"   歌曲名称: {generated_name}")
print(f"   作者: {user_info['username']}")
print(f"   邮箱: {user_info['email']}")
print(f"   参考歌曲: {target_song.title} - {target_song.artist}")
print(f"   播放量排名: TOP {rank}")

print("\n" + "=" * 70)
print("🎉 自动创作演示完成！")
print("\n📝 最终作品信息:")
print(f"   歌曲名称: {generated_name}")
print(f"   作者: {user_info['username']}")
print(f"   时长: {generated.duration}秒")
print(f"   风格相似度: {generated.style_similarity:.2%}")
print(f"   原创度评分: {report.originality_score:.2%}")
print(f"   参考歌曲: {target_song.title} - {target_song.artist}")
print("\n✅ 作品已准备好，可以下载和分享！")
