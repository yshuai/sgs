from abc import ABC, abstractmethod
import psutil
import subprocess
import time
import random
import pygetwindow as gw
import pyautogui
from .config_manager import ConfigManager

class DisconnectStrategy(ABC):
    """拔电策略基类"""
    def __init__(self):
        self.config = ConfigManager().config
        
    @abstractmethod
    def execute(self) -> bool:
        """执行拔电操作"""
        pass

class ProcessKillStrategy(DisconnectStrategy):
    """进程终止拔电策略"""
    def execute(self) -> bool:
        try:
            process_name = self.config["client"]["process_name"]
            game_path = self.config["client"]["game_path"]
            
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'].lower() == process_name.lower():
                    process = psutil.Process(proc.info['pid'])
                    process.terminate()
                    time.sleep(random.uniform(0.8, 1.5))
                    
                    try:
                        subprocess.Popen(game_path)
                        return True
                    except Exception as e:
                        print(f"重启游戏失败: {e}")
                        return False
                        
            print(f"未找到目标游戏进程: {process_name}")
            return False
            
        except Exception as e:
            print(f"进程操作失败: {e}")
            return False

class BrowserTabStrategy(DisconnectStrategy):
    """浏览器标签页拔电策略"""
    def execute(self) -> bool:
        try:
            window_title = self.config["browser"]["window_title"]
            sgs_window = None
            
            for window in gw.getAllWindows():
                if window_title in window.title:
                    sgs_window = window
                    break
                    
            if not sgs_window:
                print(f"未找到{window_title}的窗口")
                return False
                
            # 保存当前窗口
            try:
                current_window = gw.getActiveWindow()
            except:
                current_window = None
            
            # 激活三国杀窗口并执行操作
            try:
                sgs_window.activate()
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'w')
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'shift', 't')
                
                # 恢复原窗口焦点
                if current_window:
                    current_window.activate()
                return True
                
            except Exception as e:
                print(f"操作失败: {e}")
                return False
                
        except Exception as e:
            print(f"执行失败: {e}")
            return False 