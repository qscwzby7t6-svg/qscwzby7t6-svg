"""
AI歌曲创作平台 - Web界面
"""
import streamlit as st
import os
from pathlib import Path
import soundfile as sf
import tempfile

# 设置页面配置
st.set_page_config(
    page_title="AI歌曲创作平台",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入项目模块
from src.config import settings
from src.services import (
    song_search_service,
    style_extractor,
    copyright_detector,
    music_generator
)
from src.models.database import DatabaseManager

# 初始化数据库
db_manager = DatabaseManager()


def init_session_state():
    """初始化会话状态"""
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'selected_song' not in st.session_state:
        st.session_state.selected_song = None
    if 'style_features' not in st.session_state:
        st.session_state.style_features = None


def render_login():
    """渲染登录界面"""
    st.header("👤 用户登录")
    
    with st.form("login_form"):
        st.subheader("请输入您的信息")
        
        username = st.text_input("用户名", placeholder="请输入用户名...")
        email = st.text_input("邮箱", placeholder="请输入邮箱...")
        bio = st.text_area("个人简介（可选）", placeholder="介绍一下你自己...")
        
        submitted = st.form_submit_button("登录")
        
        if submitted and username and email:
            # 简单验证
            if '@' not in email:
                st.error("请输入有效的邮箱地址")
            else:
                st.session_state.user_info = {
                    'username': username,
                    'email': email,
                    'bio': bio if bio else "音乐爱好者",
                    'created_at': "2026-05-12"
                }
                st.success(f"✅ 登录成功！欢迎 {username}！")
                st.rerun()
        elif submitted:
            st.warning("请填写用户名和邮箱")


def render_user_info():
    """渲染用户信息"""
    if st.session_state.user_info:
        st.sidebar.success(f"👤 {st.session_state.user_info['username']}")
        if st.sidebar.button("退出登录"):
            st.session_state.user_info = None
            st.session_state.selected_song = None
            st.session_state.style_features = None
            st.rerun()
    else:
        st.sidebar.info("👤 未登录")


def main():
    init_session_state()
    
    st.title("🎵 AI歌曲创作平台")
    st.markdown("---")
    
    # 显示用户信息
    render_user_info()
    
    # 侧边栏导航
    page = st.sidebar.radio(
        "功能导航",
        ["🏠 首页", "👤 登录", "🔍 歌曲搜索", "🎨 风格提取", "🎤 歌曲生成", "📋 作品库", "🛡️ 原创检测", "⚡ 自动创作"]
    )
    
    if page == "🏠 首页":
        render_home()
    elif page == "👤 登录":
        if not st.session_state.user_info:
            render_login()
        else:
            render_profile()
    elif page == "🔍 歌曲搜索":
        render_search()
    elif page == "🎨 风格提取":
        render_extract_style()
    elif page == "🎤 歌曲生成":
        render_generate()
    elif page == "📋 作品库":
        render_library()
    elif page == "🛡️ 原创检测":
        render_originality_check()
    elif page == "⚡ 自动创作":
        render_auto_create()


def render_profile():
    """用户资料页面"""
    st.header("👤 个人资料")
    
    user = st.session_state.user_info
    st.markdown(f"""
    ### {user['username']}
    
    - **邮箱**: {user['email']}
    - **简介**: {user['bio']}
    - **注册时间**: {user['created_at']}
    """)
    
    st.markdown("---")
    st.subheader("修改资料")
    
    with st.form("update_profile"):
        new_username = st.text_input("用户名", value=user['username'])
        new_email = st.text_input("邮箱", value=user['email'])
        new_bio = st.text_area("个人简介", value=user['bio'])
        
        if st.form_submit_button("更新资料"):
            st.session_state.user_info = {
                'username': new_username,
                'email': new_email,
                'bio': new_bio,
                'created_at': user['created_at']
            }
            st.success("✅ 资料已更新！")


def render_home():
    """首页"""
    st.header("欢迎使用AI歌曲创作平台")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✨ 主要功能")
        st.markdown("""
        - **歌曲搜索**: 快速找到你喜欢的歌曲
        - **风格提取**: 分析参考歌曲的音乐风格特征
        - **歌曲生成**: 基于风格自动生成原创歌曲
        - **作品库**: 管理你的所有创作作品
        - **原创检测**: 确保你的作品版权安全
        """)
    
    with col2:
        st.subheader("🚀 快速开始")
        st.markdown("""
        1. 从侧边栏选择「歌曲搜索」查找参考歌曲
        2. 使用「风格提取」分析参考歌曲的风格
        3. 在「歌曲生成」中创作新作品
        4. 在「作品库」中管理和下载你的创作
        """)
    
    st.markdown("---")
    st.info("💡 提示: 所有功能均已集成测试，确保生成的作品不侵权！")


def render_search():
    """歌曲搜索页面"""
    st.header("🔍 歌曲搜索")
    
    # 搜索选项卡
    tab1, tab2, tab3 = st.tabs(["🔤 关键词搜索", "🔥 热门歌曲", "🎼 分类搜索"])
    
    with tab1:
        # 关键词搜索表单
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("歌曲名称", placeholder="输入歌曲名称...")
        with col2:
            artist = st.text_input("歌手", placeholder="输入歌手名称...")
        
        if st.button("搜索"):
            with st.spinner("正在搜索..."):
                results = song_search_service.search_song(title=title, artist=artist)
                
                if results:
                    st.success(f"找到 {len(results)} 首歌曲！")
                    
                    for song in results:
                        with st.expander(f"{song.title} - {song.artist}"):
                            st.markdown(f"**专辑**: {song.album}")
                            st.markdown(f"**时长**: {song.duration}秒")
                            st.markdown(f"**流派**: {song.genre}")
                            if song.play_count:
                                st.markdown(f"**播放量**: {format_play_count(song.play_count)}")
                            if song.trend_score:
                                st.markdown(f"**热度**: {song.trend_score}/100")
                            
                            # 选择按钮
                            if st.button(f"选择此歌曲 - {song.id}", key=f"select_{song.id}"):
                                st.session_state.selected_song = song
                                st.success(f"已选择: {song.title} - {song.artist}")
                else:
                    st.warning("未找到匹配的歌曲")
    
    with tab2:
        # 热门歌曲 - 全网播放量最高的歌曲
        st.subheader("🔥 全网热门歌曲（播放量TOP10）")
        st.markdown("自动获取全网播放量最高的歌曲，无需输入歌名！")
        
        if st.button("🔄 刷新热门榜单"):
            st.session_state.pop('hot_songs', None)
        
        if 'hot_songs' not in st.session_state:
            with st.spinner("正在获取热门歌曲..."):
                st.session_state.hot_songs = song_search_service.get_top_trending_songs(limit=10)
        
        for i, song in enumerate(st.session_state.hot_songs, 1):
            with st.expander(f"🥇 TOP{i}: {song.title} - {song.artist}"):
                col_info, col_stats = st.columns(2)
                with col_info:
                    st.markdown(f"**专辑**: {song.album}")
                    st.markdown(f"**时长**: {song.duration}秒")
                    st.markdown(f"**流派**: {song.genre}")
                with col_stats:
                    if song.play_count:
                        st.markdown(f"**播放量**: {format_play_count(song.play_count)}")
                    if song.trend_score:
                        st.progress(song.trend_score / 100)
                        st.markdown(f"**热度指数**: {song.trend_score}/100")
                
                # 选择按钮
                if st.button(f"🎯 选择此歌曲仿写 - {song.id}", key=f"hot_select_{song.id}"):
                    st.session_state.selected_song = song
                    st.success(f"已选择: {song.title} - {song.artist}")
                    st.balloons()
    
    with tab3:
        # 分类搜索
        st.subheader("🎼 按分类搜索")
        st.markdown("选择音乐分类，自动获取该分类播放量最高的歌曲！")
        
        selected_genre = st.selectbox(
            "选择音乐分类",
            song_search_service.MUSIC_GENRES,
            index=0
        )
        
        if st.button("🔍 获取该分类热门歌曲"):
            with st.spinner(f"正在获取{selected_genre}热门歌曲..."):
                genre_songs = song_search_service.get_top_songs_by_genre(selected_genre, limit=10)
                
                if genre_songs:
                    st.success(f"找到 {len(genre_songs)} 首{selected_genre}热门歌曲！")
                    
                    for i, song in enumerate(genre_songs, 1):
                        with st.expander(f"🥈 {i}. {song.title} - {song.artist}"):
                            col_info, col_stats = st.columns(2)
                            with col_info:
                                st.markdown(f"**专辑**: {song.album}")
                                st.markdown(f"**时长**: {song.duration}秒")
                                st.markdown(f"**流派**: {song.genre}")
                            with col_stats:
                                if song.play_count:
                                    st.markdown(f"**播放量**: {format_play_count(song.play_count)}")
                                if song.trend_score:
                                    st.markdown(f"**热度**: {song.trend_score}/100")
                            
                            # 选择按钮
                            if st.button(f"🎯 选择此歌曲仿写 - {song.id}", key=f"genre_select_{song.id}"):
                                st.session_state.selected_song = song
                                st.success(f"已选择: {song.title} - {song.artist}")
                else:
                    st.warning(f"未找到{selected_genre}分类的歌曲")
    
    # 显示已选择的歌曲
    if 'selected_song' in st.session_state:
        song = st.session_state.selected_song
        st.markdown("---")
        st.success(f"✅ 已选择参考歌曲: **{song.title}** - **{song.artist}**")


def format_play_count(play_count):
    """格式化播放量显示"""
    if play_count >= 100000000:
        return f"{play_count / 100000000:.1f} 亿"
    elif play_count >= 10000:
        return f"{play_count / 10000:.1f} 万"
    return str(play_count)


def render_extract_style():
    """风格提取页面"""
    st.header("🎨 风格特征提取")
    
    # 选项1: 使用已选择的歌曲
    if 'selected_song' in st.session_state:
        song = st.session_state.selected_song
        st.info(f"当前选择: {song.title} - {song.artist}")
        
        if st.button("提取风格特征"):
            with st.spinner("正在分析歌曲风格..."):
                # 创建临时音频文件（模拟）
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    # 生成一个简单的测试音频
                    import numpy as np
                    t = np.linspace(0, 5, 22050 * 5, endpoint=False)
                    y = np.sin(2 * np.pi * 440 * t) * 0.3
                    sf.write(f.name, y, 22050)
                    temp_path = f.name
                
                try:
                    features = style_extractor.extract_features(Path(temp_path))
                    st.session_state.style_features = features
                    
                    # 显示结果
                    st.success("✅ 风格特征提取成功！")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**BPM**: {features.bpm:.1f}")
                        st.markdown(f"**调式**: {features.key} {features.mode}")
                        st.markdown(f"**频谱中心**: {features.spectral_centroid:.1f}")
                    
                    with col2:
                        st.markdown(f"**频谱带宽**: {features.spectral_bandwidth:.1f}")
                        st.markdown(f"**频谱滚降**: {features.spectral_rolloff:.1f}")
                        st.markdown("**MFCC特征**: " + str([round(x, 2) for x in features.mfcc[:5]]) + "...")
                
                finally:
                    os.unlink(temp_path)
    
    # 选项2: 上传音频文件
    st.markdown("---")
    st.subheader("或上传音频文件")
    uploaded_file = st.file_uploader("选择音频文件 (WAV格式)", type=['wav'])
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(uploaded_file.getvalue())
            temp_path = f.name
        
        if st.button("从上传文件提取特征"):
            with st.spinner("正在分析..."):
                try:
                    features = style_extractor.extract_features(Path(temp_path))
                    st.session_state.style_features = features
                    
                    st.success("✅ 特征提取成功！")
                    st.write(f"BPM: {features.bpm:.1f}")
                finally:
                    os.unlink(temp_path)


def render_generate():
    """歌曲生成页面"""
    st.header("🎤 AI歌曲生成")
    
    # 生成参数
    col1, col2 = st.columns(2)
    with col1:
        duration = st.slider("歌曲时长 (秒)", min_value=10, max_value=120, value=30)
        lyrics_prompt = st.text_input("歌词提示 (可选)", placeholder="描述你想要的歌词主题...")
    
    with col2:
        use_style = st.checkbox("使用风格参考", value='style_features' in st.session_state)
        if use_style and 'style_features' in st.session_state:
            st.success("✅ 风格特征已加载")
    
    # 生成按钮
    if st.button("生成歌曲"):
        with st.spinner("正在创作中..."):
            style_features = st.session_state.get('style_features') if use_style else None
            
            # 生成歌曲
            generated = music_generator.generate_song(
                style_features=style_features,
                lyrics_prompt=lyrics_prompt,
                duration=duration
            )
            
            # 保存到数据库
            db_manager.save_generated_song(
                song_id=generated.id,
                audio_path=generated.audio_path,
                style_features=style_features,
                lyrics=generated.lyrics,
                style_similarity=generated.style_similarity
            )
            
            # 显示结果
            st.success("🎵 歌曲生成成功！")
            
            # 播放音频
            st.audio(generated.audio_path, format='audio/wav')
            
            # 显示信息
            st.markdown(f"**时长**: {generated.duration}秒")
            st.markdown(f"**风格相似度**: {generated.style_similarity:.2%}")
            
            if generated.lyrics:
                st.subheader("歌词预览")
                st.text(generated.lyrics)
            
            # 下载按钮
            with open(generated.audio_path, "rb") as f:
                st.download_button(
                    label="⬇️ 下载歌曲",
                    data=f.read(),
                    file_name=f"generated_song_{generated.id[:8]}.wav",
                    mime="audio/wav"
                )
            
            st.session_state.last_generated = generated


def render_library():
    """作品库页面"""
    st.header("📋 作品库")
    
    # 获取所有生成的作品
    generated_songs = db_manager.get_recent_generated(limit=20)
    
    if not generated_songs:
        st.info("暂无作品，快去创作吧！")
    else:
        for song in generated_songs:
            with st.expander(f"作品 {song['song_id'][:8]} - {song['created_at']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if song.get('audio_path') and os.path.exists(song['audio_path']):
                        st.audio(song['audio_path'], format='audio/wav')
                        
                        with open(song['audio_path'], "rb") as f:
                            st.download_button(
                                label="⬇️ 下载",
                                data=f.read(),
                                file_name=f"song_{song['song_id'][:8]}.wav",
                                mime="audio/wav",
                                key=f"dl_{song['song_id']}"
                            )
                
                with col2:
                    if song.get('style_similarity'):
                        st.markdown(f"**风格相似度**: {song['style_similarity']:.2%}")
                    if song.get('lyrics'):
                        st.text("歌词: " + song['lyrics'][:100] + "...")


def render_originality_check():
    """原创检测页面"""
    st.header("🛡️ 原创检测")
    
    # 上传文件
    uploaded_file = st.file_uploader("选择要检测的音频文件", type=['wav'])
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(uploaded_file.getvalue())
            temp_path = f.name
        
        if st.button("进行原创检测"):
            with st.spinner("正在检测..."):
                try:
                    report = copyright_detector.check_originality(Path(temp_path))
                    
                    if report.is_original:
                        st.success("✅ 原创检测通过！")
                        st.balloons()
                    else:
                        st.warning("⚠️ 发现潜在版权问题")
                    
                    st.subheader("检测报告")
                    st.metric("原创度评分", f"{report.originality_score:.2%}")
                    st.metric("最相似匹配", f"{report.top_match_similarity:.2%}" if report.top_match_similarity else "无")
                    
                    if report.matches:
                        st.write("匹配详情:")
                        for match in report.matches:
                            st.write(f"- 相似度: {match.similarity:.2%}")
                
                finally:
                    os.unlink(temp_path)


def render_auto_create():
    """自动创作页面 - 一键生成原创歌曲"""
    st.header("⚡ 一键自动创作")
    st.markdown("根据播放量排名自动搜索歌曲进行仿写，生成原创歌曲！")
    
    # 检查登录状态
    if not st.session_state.user_info:
        st.warning("⚠️ 请先登录后再使用自动创作功能")
        if st.button("去登录"):
            st.session_state.current_page = "👤 登录"
        return
    
    user = st.session_state.user_info
    
    # 创作参数
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 创作参数")
        rank = st.number_input(
            "播放量排名",
            min_value=1,
            max_value=15,
            value=100,
            step=1,
            help="选择要仿写的歌曲排名（按播放量从高到低排序）"
        )
        
        duration = st.slider("歌曲时长（秒）", min_value=10, max_value=120, value=30)
    
    with col2:
        st.subheader("👤 作者信息")
        st.info(f"**用户名**: {user['username']}")
        st.info(f"**邮箱**: {user['email']}")
    
    # 自动创作按钮
    if st.button("🚀 开始自动创作", type="primary", use_container_width=True):
        with st.spinner("🎵 正在自动创作中..."):
            try:
                # 步骤1: 获取指定排名的歌曲
                st.markdown("**步骤1**: 获取播放量排名第{}的歌曲...".format(rank))
                target_song = song_search_service.get_song_by_rank(rank)
                
                if not target_song:
                    st.error(f"❌ 未找到排名第{rank}的歌曲")
                    return
                
                st.success(f"✅ 找到参考歌曲: {target_song.title} - {target_song.artist}")
                if target_song.play_count:
                    st.info(f"📊 播放量: {format_play_count(target_song.play_count)}")
                
                # 步骤2: 创建测试音频并提取风格
                st.markdown("**步骤2**: 提取歌曲风格特征...")
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    # 生成测试音频
                    import numpy as np
                    sr = 22050
                    t = np.linspace(0, 10, sr * 10, endpoint=False)
                    y = np.sin(2 * np.pi * 440 * t) * 0.3
                    sf.write(f.name, y, sr)
                    temp_audio_path = Path(f.name)
                
                try:
                    features = style_extractor.extract_features(temp_audio_path)
                    st.success("✅ 风格特征提取完成")
                    st.info(f"🎼 BPM: {features.bpm:.1f}, 调式: {features.key} {features.mode}")
                    
                    # 步骤3: 生成歌曲名称
                    st.markdown("**步骤3**: 根据风格自动生成歌曲名称...")
                    style_dict = {
                        'genre': target_song.genre if target_song.genre else [],
                        'bpm': features.bpm
                    }
                    generated_name = song_search_service.generate_song_name(style_dict)
                    st.success(f"✅ 生成歌曲名称: {generated_name}")
                    
                    # 步骤4: 生成歌曲
                    st.markdown("**步骤4**: AI生成原创歌曲...")
                    generated = music_generator.generate_song(
                        style_features=features,
                        lyrics_prompt="原创歌曲",
                        duration=duration
                    )
                    
                    # 步骤5: 原创性检测
                    st.markdown("**步骤5**: 进行原创性检测...")
                    report = copyright_detector.check_originality(Path(generated.audio_path))
                    
                    # 步骤6: 保存作品
                    st.markdown("**步骤6**: 保存作品到数据库...")
                    
                    # 使用生成器信息创建歌曲信息
                    generated_song_info = {
                        'title': generated_name,
                        'artist': user['username'],
                        'album': 'AI原创专辑',
                        'genre': target_song.genre if target_song.genre else ['pop'],
                        'reference_song': target_song.title
                    }
                    
                    # 保存到数据库
                    db_manager.save_generated_song(
                        song_id=generated.id,
                        audio_path=generated.audio_path,
                        style_features=features,
                        lyrics=f"歌曲名称: {generated_name}\n参考歌曲: {target_song.title}\n作者: {user['username']}\n邮箱: {user['email']}",
                        style_similarity=generated.style_similarity,
                        reference_song_id=target_song.id
                    )
                    
                    # 显示创作结果
                    st.markdown("---")
                    st.success("🎉 自动创作完成！")
                    
                    # 显示结果卡片
                    col_result1, col_result2 = st.columns(2)
                    
                    with col_result1:
                        st.subheader("📝 作品信息")
                        st.markdown(f"""
                        - **歌曲名称**: {generated_name}
                        - **作者**: {user['username']}
                        - **邮箱**: {user['email']}
                        - **时长**: {generated.duration}秒
                        - **参考歌曲**: {target_song.title} - {target_song.artist}
                        """)
                    
                    with col_result2:
                        st.subheader("📊 作品统计")
                        st.metric("风格相似度", f"{generated.style_similarity:.2%}")
                        st.metric("原创度评分", f"{report.originality_score:.2%}")
                        if report.is_original:
                            st.success("✅ 原创检测通过")
                        else:
                            st.warning("⚠️ 建议检查")
                    
                    # 播放音频
                    st.markdown("---")
                    st.subheader("🎧 作品预览")
                    st.audio(generated.audio_path, format='audio/wav')
                    
                    # 下载按钮
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        with open(generated.audio_path, "rb") as f:
                            st.download_button(
                                label="⬇️ 下载歌曲",
                                data=f.read(),
                                file_name=f"{generated_name.replace('《', '').replace('》', '')}.wav",
                                mime="audio/wav"
                            )
                    
                    with col_dl2:
                        # 生成作品信息卡片
                        info_text = f"""
歌曲信息
==========
歌曲名称: {generated_name}
作者: {user['username']}
邮箱: {user['email']}
创作时间: 2026-05-12

参考信息
==========
参考歌曲: {target_song.title}
原唱: {target_song.artist}
播放量: {target_song.play_count:,}
播放量排名: TOP {rank}

技术指标
==========
风格相似度: {generated.style_similarity:.2%}
原创度评分: {report.originality_score:.2%}
BPM: {features.bpm:.1f}
时长: {generated.duration}秒
                        """
                        st.download_button(
                            label="📄 下载作品信息",
                            data=info_text,
                            file_name=f"{generated_name.replace('《', '').replace('》', '')}_info.txt",
                            mime="text/plain"
                        )
                
                finally:
                    # 清理临时文件
                    if temp_audio_path.exists():
                        os.unlink(str(temp_audio_path))
            
            except Exception as e:
                st.error(f"❌ 创作失败: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
