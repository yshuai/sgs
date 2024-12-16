import sys
import psutil
import random
import time
import threading
import ctypes
from ctypes import windll
import pyautogui
import keyboard
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import subprocess

def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False

game_path = r"C:\Program Files (x86)\Steam\steamapps\common\Sgsc10th\Sgsc10th.exe"
target_game = 'Sgsc10th.exe'

class AdvancedAntiCheatDisconnect:
    def __init__(self, target_game='sgsc10th.exe', game_path=game_path):
        self.target_game = target_game
        self.game_path = game_path
        self.process_found = False
    
    def strategy_network_block(self, pid):
        """通过中断并重启进程来断网"""
        try:
            process = psutil.Process(pid)
            process.terminate()
            time.sleep(random.uniform(0.8, 1.5))
            
            try:
                subprocess.Popen(self.game_path)
                return True
            except Exception as e:
                print(f"重启游戏失败: {e}")
                return False
            
        except Exception as e:
            print(f"进程操作失败: {e}")
            return False
    
    def execute_disconnect(self):
        """执行断线"""
        self.process_found = False
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'].lower() == self.target_game.lower():
                    pid = proc.info['pid']
                    self.process_found = True
                    return self.strategy_network_block(pid)
            
            if not self.process_found:
                print(f"未找到目标游戏进程: {self.target_game}")
                return False
                
        except Exception as e:
            print(f"执行断线失败: {e}")
            return False

class GameDisconnectUI(QMainWindow):
    # 定义自定义信号
    success_signal = pyqtSignal()
    error_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        if not is_admin():
            windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
            
        self.setWindowTitle('高级一键拔线')
        self.setGeometry(100, 100, 250, 120)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 180);
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        self.click_label = QLabel('一键断线')
        self.click_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(60, 60, 60, 200);
                border-radius: 8px;
                padding: 10px;
                font-size: 20px;
            }
        """)
        self.click_label.mousePressEvent = self.trigger_disconnect
        layout.addWidget(self.click_label)
        
        # 连接信号到对应的槽
        self.success_signal.connect(self.reset_ui)
        self.error_signal.connect(self.show_error)
        
        self.anti_cheat = AdvancedAntiCheatDisconnect(target_game=target_game,game_path=game_path)
        
        self.dragging = False
        self.offset = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.click_label.underMouse():  # 如果不是点击在标签上，才允许拖动
                self.dragging = True
                self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.dragging and self.offset:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None
    
    def trigger_disconnect(self, event):
        """触发断线"""
        if event.button() == Qt.LeftButton:
            self.click_label.setText('执行断线中...')
            self.click_label.setStyleSheet("""
                QLabel {
                    color: yellow;
                    background-color: rgba(60, 60, 60, 200);
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 20px;
                }
            """)
            
            threading.Thread(target=self.async_disconnect, daemon=True).start()
    
    def async_disconnect(self):
        """异步执行断线"""
        success = self.anti_cheat.execute_disconnect()
        
        if success:
            self.reset_ui()
        else:
            self.error_signal.emit()
    
    def reset_ui(self):
        """重置UI状态"""
        self.click_label.setText('一键断线')
        self.click_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(60, 60, 60, 200);
                border-radius: 8px;
                padding: 10px;
                font-size: 20px;
            }
        """)
    
    def show_error(self):
        """显示错误信息"""
        self.click_label.setText('断线失败')
        self.click_label.setStyleSheet("""
            QLabel {
                color: red;
                background-color: rgba(60, 60, 60, 200);
                border-radius: 8px;
                padding: 10px;
                font-size: 20px;
            }
        """)
        
        QTimer.singleShot(2000, self.reset_ui)

def main():
    app = QApplication(sys.argv)
    disconnect_tool = GameDisconnectUI()
    disconnect_tool.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
