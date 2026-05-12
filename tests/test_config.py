"""
配置模块单元测试
"""
import pytest
from pathlib import Path
from src.config import Settings, settings


class TestSettings:
    """测试Settings类"""
    
    def test_default_settings(self):
        """测试默认配置"""
        test_settings = Settings()
        
        # 检查路径是否正确
        assert test_settings.BASE_DIR.name == "workspace"
        assert test_settings.DATA_DIR.exists()
        assert test_settings.AUDIO_DIR.exists()
        assert test_settings.MODELS_DIR.exists()
        assert test_settings.DB_DIR.exists()
        assert test_settings.STATIC_DIR.exists()
        
        # 检查默认值
        assert test_settings.SAMPLE_RATE == 22050
        assert test_settings.API_PORT == 8000
        assert test_settings.DEBUG is True
        assert test_settings.ORIGINALITY_THRESHOLD == 0.7
    
    def test_custom_settings(self, tmp_path):
        """测试自定义配置（使用临时目录）"""
        # 这里可以测试环境变量覆盖的情况
        pass


class TestGlobalSettings:
    """测试全局配置实例"""
    
    def test_global_instance(self):
        """测试全局配置实例"""
        assert settings is not None
        assert isinstance(settings, Settings)
    
    def test_directories_created(self):
        """测试目录是否已创建"""
        assert settings.DATA_DIR.is_dir()
        assert settings.AUDIO_DIR.is_dir()
        assert settings.MODELS_DIR.is_dir()
        assert settings.DB_DIR.is_dir()
        assert settings.STATIC_DIR.is_dir()
