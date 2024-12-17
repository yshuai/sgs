import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from src.sgs.disconnect_strategy import ProcessKillStrategy, BrowserTabStrategy
from src.sgs.config_manager import ConfigManager

class DisconnectWorker(QThread):
    """拔电工作线程"""
    finished = pyqtSignal(bool)
    
    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        
    def run(self):
        success = self.strategy.execute()
        self.finished.emit(success)

class DisconnectButton(QLabel):
    """拔电按钮基类"""
    def __init__(self, text, strategy, parent=None):
        super().__init__(text, parent)
        self.strategy = strategy
        self.worker = None
        self.original_text = text
        self.config = ConfigManager().config
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(60, 64, 67, 200);
                border-radius: 6px;
                padding: 8px;
                font-size: 16px;
            }
            QLabel:hover {
                background-color: rgba(70, 74, 77, 200);
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setText('执行中...')
            self.setStyleSheet("""
                QLabel {
                    color: #FFC107;
                    background-color: rgba(60, 64, 67, 200);
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 16px;
                }
            """)
            
            self.worker = DisconnectWorker(self.strategy)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
    
    def on_finished(self, success):
        if not success:
            self.setText('执行失败')
            color = '#F44336'  # 错误红色
        else:
            self.setText('执行成功')
            color = '#4CAF50'  # 成功绿色
            
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: rgba(60, 64, 67, 200);
                border-radius: 6px;
                padding: 8px;
                font-size: 16px;
            }}
        """)
        QTimer.singleShot(2000, self.reset_ui)
    
    def reset_ui(self):
        self.setText(self.original_text)
        self.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(60, 60, 60, 200);
                border-radius: 6px;
                padding: 8px;
                font-size: 16px;
            }
        """)

class DisconnectManagerUI(QMainWindow):
    """拔电管理器主窗口"""
    def __init__(self):
        super().__init__()
        
        # 处理打包后的资源路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 exe
            application_path = os.path.dirname(sys.executable)
            config_path = os.path.join(application_path, 'src', 'sgs', 'config.json')
        else:
            # 如果是开发环境
            config_path = None  # ConfigManager 会使用默认路径
            
        self.config = ConfigManager(config_path).config
        self.setWindowTitle('三国杀拔电工具')
        self.setGeometry(100, 100, 180, 120)  # 减小窗口大小
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 主窗口设置
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(32, 33, 36, 240);
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # 减小边距
        layout.setSpacing(8)  # 减小按钮间距
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        # 添加客户端拔电按钮
        self.client_btn = DisconnectButton('客户端拔电', ProcessKillStrategy())
        layout.addWidget(self.client_btn)
        
        # 添加浏览器拔电按钮
        self.browser_btn = DisconnectButton('浏览器拔电', BrowserTabStrategy())
        layout.addWidget(self.browser_btn)
        
        # 窗口拖动相关
        self.dragging = False
        self.offset = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not (self.client_btn.underMouse() or self.browser_btn.underMouse()):
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

def main():
    app = QApplication(sys.argv)
    window = DisconnectManagerUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()