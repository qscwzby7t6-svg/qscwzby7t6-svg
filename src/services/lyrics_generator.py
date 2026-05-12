"""
歌词生成模块
集成LLM进行歌词创作
"""
import random
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class LyricsTheme(Enum):
    """歌词主题"""
    LOVE = "爱情"
    SADNESS = "忧伤"
    DREAM = "梦想"
    FREEDOM = "自由"
    NOSTALGIA = "怀旧"
    HOPE = "希望"
    COURAGE = "勇气"
    YOUTH = "青春"


class LyricsStyle(Enum):
    """歌词风格"""
    POP = "流行"
    ROCK = "摇滚"
    FOLK = "民谣"
    BALLAD = "抒情"
    RAP = "说唱"
    CHINESE_CLASSICAL = "古风"


@dataclass
class LyricsLine:
    """歌词行"""
    text: str
    start_time: float
    end_time: float
    translation: Optional[str] = None


@dataclass
class GeneratedLyrics:
    """生成的歌词"""
    title: str
    theme: str
    style: str
    lines: List[LyricsLine]
    full_text: str
    structure: Dict[str, Any]


class LLMIntegration:
    """LLM歌词生成集成"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_endpoint = "https://api.openai.com/v1/chat/completions"
    
    def generate_with_llm(
        self,
        theme: str,
        style: str,
        keywords: List[str],
        song_title: str = None,
        duration: int = 180
    ) -> Optional[GeneratedLyrics]:
        """
        使用LLM生成歌词
        
        Args:
            theme: 主题
            style: 风格
            keywords: 关键词
            song_title: 歌曲标题
            duration: 时长（秒）
            
        Returns:
            生成的歌词
        """
        # 构建提示词
        prompt = self._build_prompt(theme, style, keywords, song_title, duration)
        
        try:
            # 实际调用LLM API
            # response = self._call_llm_api(prompt)
            # return self._parse_llm_response(response)
            
            # 模拟生成
            return self._simulate_generation(theme, style, keywords, song_title, duration)
            
        except Exception as e:
            print(f"LLM歌词生成失败: {e}")
            return self._simulate_generation(theme, style, keywords, song_title, duration)
    
    def _build_prompt(
        self,
        theme: str,
        style: str,
        keywords: List[str],
        song_title: str,
        duration: int
    ) -> str:
        """构建LLM提示词"""
        prompt = f"""请为歌曲创作歌词，要求如下：
主题：{theme}
风格：{style}
时长：约{duration}秒
关键词：{', '.join(keywords)}

请创作一首完整歌词，包括：
1. 歌名
2. 主歌（Verse）2段
3. 副歌（Chorus）2段
4. 过渡段（Bridge）1段

请用中文创作，语言优美、情感真挚。"""
        
        if song_title:
            prompt += f"\n\n歌曲标题：{song_title}"
        
        return prompt
    
    def _call_llm_api(self, prompt: str) -> str:
        """调用LLM API"""
        import requests
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.8,
            'max_tokens': 1000
        }
        
        response = requests.post(
            self.api_endpoint,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        
        raise Exception(f"API调用失败: {response.status_code}")
    
    def _parse_llm_response(self, response: str) -> GeneratedLyrics:
        """解析LLM响应"""
        # 解析歌词结构
        lines = []
        current_section = "verse"
        line_start = 0.0
        line_duration = 5.0
        
        for line_text in response.split('\n'):
            if line_text.strip():
                lines.append(LyricsLine(
                    text=line_text.strip(),
                    start_time=line_start,
                    end_time=line_start + line_duration
                ))
                line_start += line_duration
        
        return GeneratedLyrics(
            title="生成的歌曲",
            theme="未分类",
            style="流行",
            lines=lines,
            full_text=response,
            structure={'sections': []}
        )
    
    def _simulate_generation(
        self,
        theme: str,
        style: str,
        keywords: List[str],
        song_title: str,
        duration: int
    ) -> GeneratedLyrics:
        """模拟歌词生成"""
        print(f"🎤 正在生成{style}风格{theme}主题歌词...")
        
        # 生成歌名
        title = song_title or self._generate_title(theme, style, keywords)
        
        # 生成歌词结构
        lyrics_data = self._generate_lyrics_structure(theme, style, keywords, duration)
        
        return GeneratedLyrics(
            title=title,
            theme=theme,
            style=style,
            lines=lyrics_data['lines'],
            full_text=lyrics_data['full_text'],
            structure=lyrics_data['structure']
        )
    
    def _generate_title(self, theme: str, style: str, keywords: List[str]) -> str:
        """生成歌曲标题"""
        templates = {
            LyricsTheme.LOVE.value: [
                "《{}的约定》", "《遇见{}》", "《{}时光》", "《{}之约》",
                "《{}在心中》", "《因你{}》", "《{}绽放》", "《爱如{}》"
            ],
            LyricsTheme.SADNESS.value: [
                "《{}夜》", "《{}回忆》", "《{}独白》", "《{}的眼泪》",
                "《{}不再来》", "《致{}》", "《{}如烟》", "《{}的痕迹》"
            ],
            LyricsTheme.DREAM.value: [
                "《追{}》", "《{}飞翔》", "《{}在路上》", "《向着{}》",
                "《{}的力量》", "《勇敢{}》", "《{}无限》", "《拥抱{}》"
            ],
            LyricsTheme.FREEDOM.value: [
                "《{}如风》", "《放飞{}》", "《{}天空》", "《追逐{}》",
                "《{}无界》", "《{}狂奔》", "《{}漂泊》", "《生命{}》"
            ],
            LyricsTheme.NOSTALGIA.value: [
                "《{}时光》", "《那年{}》", "《{}记忆》", "《{}-2000》",
                "《{}老歌》", "《回到{}》", "《{}岁月》", "《如烟{}》"
            ],
            LyricsTheme.HOPE.value: [
                "《{}光芒》", "《{}-明天》", "《迎接{}》", "《{}在前方》",
                "《黎明{}》", "《{}-晨曦》", "《拥抱{}》", "《{}-重生》"
            ],
            LyricsTheme.COURAGE.value: [
                "《逆风{}》", "《{}-勇者》", "《无所{}》", "《{}-无敌》",
                "《{}-挑战》", "《{}-向前》", "《{}-奋斗》", "《{}-前行》"
            ],
            LyricsTheme.YOUTH.value: [
                "《{}-青春》", "《那年{}》", "《{}不再》", "《{}-时光》",
                "《{}-呐喊》", "《燃烧{}》", "《{}-狂想》", "《{}-记忆》"
            ]
        }
        
        theme_key = theme
        keyword = random.choice(keywords) if keywords else "旋律"
        
        available_templates = templates.get(theme_key, templates[LyricsTheme.LOVE.value])
        template = random.choice(available_templates)
        
        return template.format(keyword)
    
    def _generate_lyrics_structure(
        self,
        theme: str,
        style: str,
        keywords: List[str],
        duration: int
    ) -> Dict[str, Any]:
        """生成歌词结构"""
        lines = []
        line_start = 0.0
        line_duration = 4.0  # 每行约4秒
        
        # 主歌1
        verse1_lines = self._generate_verse(theme, keywords, 4)
        lines.append(LyricsLine("[主歌1]", line_start, line_start + 1.0))
        line_start += 1.0
        for line_text in verse1_lines:
            lines.append(LyricsLine(line_text, line_start, line_start + line_duration))
            line_start += line_duration
        
        # 副歌1
        chorus_lines = self._generate_chorus(theme, keywords, 4)
        lines.append(LyricsLine("[副歌]", line_start, line_start + 1.0))
        line_start += 1.0
        for line_text in chorus_lines:
            lines.append(LyricsLine(line_text, line_start, line_start + line_duration))
            line_start += line_duration
        
        # 主歌2
        verse2_lines = self._generate_verse(theme, keywords, 4)
        lines.append(LyricsLine("[主歌2]", line_start, line_start + 1.0))
        line_start += 1.0
        for line_text in verse2_lines:
            lines.append(LyricsLine(line_text, line_start, line_start + line_duration))
            line_start += line_duration
        
        # 副歌2
        lines.append(LyricsLine("[副歌]", line_start, line_start + 1.0))
        line_start += 1.0
        for line_text in chorus_lines:
            lines.append(LyricsLine(line_text, line_start, line_start + line_duration))
            line_start += line_duration
        
        # 过渡段
        bridge_lines = self._generate_bridge(theme, keywords, 2)
        lines.append(LyricsLine("[过渡]", line_start, line_start + 1.0))
        line_start += 1.0
        for line_text in bridge_lines:
            lines.append(LyricsLine(line_text, line_start, line_start + line_duration))
            line_start += line_duration
        
        # 尾声
        outro_lines = self._generate_outro(theme, 2)
        lines.append(LyricsLine("[尾声]", line_start, line_start + 1.0))
        line_start += 1.0
        for line_text in outro_lines:
            lines.append(LyricsLine(line_text, line_start, line_start + line_duration))
            line_start += line_duration
        
        # 构建完整文本
        full_text = '\n'.join([line.text for line in lines if not line.text.startswith('[')])
        
        # 构建结构
        structure = {
            'verse1': {'start': 0, 'duration': 18, 'lines': 4},
            'chorus1': {'start': 19, 'duration': 18, 'lines': 4},
            'verse2': {'start': 38, 'duration': 18, 'lines': 4},
            'chorus2': {'start': 57, 'duration': 18, 'lines': 4},
            'bridge': {'start': 76, 'duration': 9, 'lines': 2},
            'outro': {'start': 86, 'duration': 10, 'lines': 2}
        }
        
        return {
            'lines': lines,
            'full_text': full_text,
            'structure': structure
        }
    
    def _generate_verse(self, theme: str, keywords: List[str], num_lines: int) -> List[str]:
        """生成主歌"""
        keyword = random.choice(keywords) if keywords else "时光"
        
        verse_templates = {
            LyricsTheme.LOVE.value: [
                "在人群中发现你的身影",
                f"那一眼仿佛穿越了{keyword}",
                "心跳的声音如此清晰",
                "世界因你而改变",
                "每一次呼吸都关于你",
                "星光洒落在这个夜晚",
                "你的笑容温暖如春",
                "愿时光停留在这一刻"
            ],
            LyricsTheme.SADNESS.value: [
                f"独自走在{keyword}的街头",
                "风吹过带走了回忆",
                "那些曾经的美好时光",
                "如今只剩下孤独",
                "夜色中弥漫着思念",
                f"{keyword}如潮水般涌来",
                "眼泪在眼眶中打转",
                "却无法挽回逝去的"
            ],
            LyricsTheme.DREAM.value: [
                f"怀揣着{keyword}出发",
                "穿越风雨不畏艰难",
                "前方道路虽然漫长",
                "信念是我前进的力量",
                "即使跌倒也要站起",
                f"追逐{keyword}的光芒",
                "让青春不留遗憾",
                "让生命绽放光彩"
            ],
            LyricsTheme.FREEDOM.value: [
                f"让{keyword}在风中飘扬",
                "挣脱束缚勇敢飞翔",
                "天空无限宽广",
                "大地充满希望",
                "不再被规则限制",
                "勇敢做真实的自己",
                "让灵魂自由翱翔",
                "奔向心中的远方"
            ]
        }
        
        templates = verse_templates.get(theme, verse_templates[LyricsTheme.LOVE.value])
        return random.sample(templates, min(num_lines, len(templates)))
    
    def _generate_chorus(self, theme: str, keywords: List[str], num_lines: int) -> List[str]:
        """生成副歌"""
        keyword = random.choice(keywords) if keywords else "旋律"
        
        chorus_templates = {
            LyricsTheme.LOVE.value: [
                f"因为爱，让我们{keyword}",
                "心跳同频永远不变",
                "你是我的唯一",
                "相伴到永远",
                f"让{keyword}回荡天际",
                "爱是最美的语言"
            ],
            LyricsTheme.SADNESS.value: [
                f"也许{keyword}不再回来",
                "只能独自承受这一切",
                "回忆是心中的伤痕",
                "永远无法抹去",
                "时间会治愈一切",
                "但伤疤依然存在"
            ],
            LyricsTheme.DREAM.value: [
                f"追逐{keyword}的脚步不停歇",
                "勇敢向前不放弃",
                "终有一天会到达",
                "梦想的彼岸",
                "让生命绽放光芒",
                "创造属于我的奇迹"
            ],
            LyricsTheme.FREEDOM.value: [
                f"我要{keyword}如风",
                "无拘无束飞翔",
                "不受任何限制",
                "做真正的自己",
                "让灵魂自由呼吸",
                "拥抱整个世界"
            ]
        }
        
        templates = chorus_templates.get(theme, chorus_templates[LyricsTheme.LOVE.value])
        return random.sample(templates, min(num_lines, len(templates)))
    
    def _generate_bridge(self, theme: str, keywords: List[str], num_lines: int) -> List[str]:
        """生成过渡段"""
        return [
            f"然而在这{''.join(keywords[:1]) if keywords else '时刻'}",
            "我终于明白",
            "生命的意义在于",
            "勇敢追求心中所爱"
        ][:num_lines]
    
    def _generate_outro(self, theme: str, num_lines: int) -> List[str]:
        """生成尾声"""
        return [
            "感谢生命中的一切",
            "感谢有你的陪伴",
            "这首歌献给你",
            "永远爱你"
        ][:num_lines]


class LyricsGenerator:
    """歌词生成器主类"""
    
    def __init__(self):
        self.llm = LLMIntegration()
    
    def generate_lyrics(
        self,
        theme: str,
        style: str,
        keywords: List[str],
        song_title: str = None,
        duration: int = 180
    ) -> GeneratedLyrics:
        """
        生成歌词
        
        Args:
            theme: 主题
            style: 风格
            keywords: 关键词
            song_title: 歌曲标题
            duration: 时长
            
        Returns:
            生成的歌词
        """
        return self.llm.generate_with_llm(
            theme=theme,
            style=style,
            keywords=keywords,
            song_title=song_title,
            duration=duration
        )
    
    def generate_from_reference(
        self,
        reference_song: str,
        style: str,
        keywords: List[str],
        duration: int = 180
    ) -> GeneratedLyrics:
        """
        根据参考歌曲生成歌词
        
        Args:
            reference_song: 参考歌曲名
            style: 风格
            keywords: 关键词
            duration: 时长
            
        Returns:
            生成的歌词
        """
        # 根据参考歌曲确定主题
        theme = self._infer_theme_from_song(reference_song)
        
        return self.generate_lyrics(
            theme=theme,
            style=style,
            keywords=keywords,
            duration=duration
        )
    
    def _infer_theme_from_song(self, song_name: str) -> str:
        """从歌曲名推断主题"""
        song_lower = song_name.lower()
        
        if any(word in song_lower for word in ['爱', 'love', '心', ' kiss', '拥抱']):
            return LyricsTheme.LOVE.value
        elif any(word in song_lower for word in ['孤独', '寂寞', 'sad', '伤', '痛']):
            return LyricsTheme.SADNESS.value
        elif any(word in song_lower for word in ['梦', 'dream', '理想', '飞翔']):
            return LyricsTheme.DREAM.value
        elif any(word in song_lower for word in ['自由', 'free', '飞', '奔跑']):
            return LyricsTheme.FREEDOM.value
        elif any(word in song_lower for word in ['青春', 'young', '时光', '那年']):
            return LyricsTheme.YOUTH.value
        else:
            return LyricsTheme.LOVE.value


# 全局实例
lyrics_generator = LyricsGenerator()
