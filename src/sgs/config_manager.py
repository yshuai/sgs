import json
import sys
from pathlib import Path

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _get_config_path(self):
        """获取配置文件路径，支持开发环境和打包环境"""
        if getattr(sys, 'frozen', False):
            # 打包环境
            base_path = Path(sys._MEIPASS)
        else:
            # 开发环境
            base_path = Path(__file__).parent
        return base_path / "config.json"
    
    def _load_config(self):
        config_path = self._get_config_path()
        try:
            with open(config_path, "r", encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 使用默认配置
            self.config = {
                "client": {
                    "game_path": r"C:\Program Files (x86)\Steam\steamapps\common\Sgsc10th\Sgsc10th.exe",
                    "process_name": "Sgsc10th.exe"
                },
                "browser": {
                    "window_title": "三国杀十周年"
                }
            }