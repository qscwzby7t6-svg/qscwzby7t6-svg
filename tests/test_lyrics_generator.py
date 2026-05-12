"""
歌词生成模块测试
"""
import pytest
from src.services.lyrics_generator import (
    LLMIntegration,
    LyricsGenerator,
    GeneratedLyrics,
    LyricsTheme,
    LyricsStyle
)


class TestLLMIntegration:
    """测试LLM集成"""
    
    @pytest.fixture
    def llm(self):
        return LLMIntegration(api_key="test_key")
    
    def test_initialization(self, llm):
        """测试初始化"""
        assert llm.api_key == "test_key"
        assert llm.model == "gpt-3.5-turbo"
    
    def test_generate_title(self, llm):
        """测试生成歌曲标题"""
        title = llm._generate_title(
            theme=LyricsTheme.LOVE.value,
            style=LyricsStyle.POP.value,
            keywords=["爱情", "甜蜜"]
        )
        
        assert isinstance(title, str)
        assert len(title) > 0
        assert "《" in title and "》" in title
    
    def test_generate_lyrics_structure(self, llm):
        """测试生成歌词结构"""
        result = llm._generate_lyrics_structure(
            theme=LyricsTheme.LOVE.value,
            style=LyricsStyle.POP.value,
            keywords=["爱情", "甜蜜"],
            duration=180
        )
        
        assert "lines" in result
        assert "full_text" in result
        assert "structure" in result
        assert len(result["lines"]) > 0
    
    def test_generate_verse(self, llm):
        """测试生成主歌"""
        verse = llm._generate_verse(
            theme=LyricsTheme.LOVE.value,
            keywords=["爱情"],
            num_lines=4
        )
        
        assert isinstance(verse, list)
        assert len(verse) == 4
        assert all(isinstance(line, str) for line in verse)
    
    def test_generate_chorus(self, llm):
        """测试生成副歌"""
        chorus = llm._generate_chorus(
            theme=LyricsTheme.LOVE.value,
            keywords=["爱情"],
            num_lines=4
        )
        
        assert isinstance(chorus, list)
        assert len(chorus) == 4
        assert all(isinstance(line, str) for line in chorus)


class TestLyricsGenerator:
    """测试歌词生成器"""
    
    @pytest.fixture
    def generator(self):
        return LyricsGenerator()
    
    def test_generate_lyrics(self, generator):
        """测试生成歌词"""
        result = generator.generate_lyrics(
            theme=LyricsTheme.LOVE.value,
            style=LyricsStyle.POP.value,
            keywords=["爱情", "甜蜜", "心动"],
            duration=180
        )
        
        assert isinstance(result, GeneratedLyrics)
        assert result.title
        assert result.theme == LyricsTheme.LOVE.value
        assert result.style == LyricsStyle.POP.value
        assert len(result.lines) > 0
        assert result.full_text
        # 检查structure字典中是否包含预期的section
        assert "verse1" in result.structure
        assert "chorus1" in result.structure
    
    def test_generate_from_reference(self, generator):
        """测试根据参考歌曲生成歌词"""
        result = generator.generate_from_reference(
            reference_song="告白气球",
            style=LyricsStyle.POP.value,
            keywords=["爱情"],
            duration=180
        )
        
        assert isinstance(result, GeneratedLyrics)
        assert len(result.lines) > 0
    
    def test_infer_theme_from_song(self, generator):
        """测试从歌曲名推断主题"""
        # 爱情主题
        theme1 = generator._infer_theme_from_song("爱情的故事")
        assert theme1 == LyricsTheme.LOVE.value
        
        # 忧伤主题
        theme2 = generator._infer_theme_from_song("孤独的夜")
        assert theme2 == LyricsTheme.SADNESS.value
        
        # 梦想主题
        theme3 = generator._infer_theme_from_song("追梦人")
        assert theme3 == LyricsTheme.DREAM.value
        
        # 默认主题
        theme4 = generator._infer_theme_from_song("未知歌曲")
        assert theme4 == LyricsTheme.LOVE.value
