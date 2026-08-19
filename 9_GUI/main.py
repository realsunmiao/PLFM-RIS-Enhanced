"""
RIS 雷达控制系统 - 主程序
提供图形化界面用于配置和控制 RIS 相控阵雷达系统

功能:
  1. 波束指向配置 (方位角/俯仰角)
  2. LFM 波形参数配置
  3. 实时数据显示 (A显/B显/距离-多普勒图)
  4. 目标跟踪与轨迹显示
  5. 数据录制与回放

作者: Wukong AI Assistant
日期: 2026-08-19
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QSpinBox, QPushButton, QGroupBox, QTabWidget,
    QComboBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ris_control import RISController


class RISControlPanel(QGroupBox):
    """RIS 控制面板"""
    
    def __init__(self, parent=None):
        super().__init__("RIS 参数配置", parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 波束指向配置
        beam_group = QGroupBox("波束指向")
        beam_layout = QVBoxLayout()
        
        # 方位角
        az_layout = QHBoxLayout()
        az_layout.addWidget(QLabel("方位角 (°):"))
        self.azimuth_slider = QSlider(Qt.Horizontal)
        self.azimuth_slider.setRange(-60, 60)
        self.azimuth_slider.setValue(0)
        self.azimuth_label = QLabel("0°")
        az_layout.addWidget(self.azimuth_slider)
        az_layout.addWidget(self.azimuth_label)
        beam_layout.addLayout(az_layout)
        
        # 俯仰角
        el_layout = QHBoxLayout()
        el_layout.addWidget(QLabel("俯仰角 (°):"))
        self.elevation_slider = QSlider(Qt.Horizontal)
        self.elevation_slider.setRange(-60, 60)
        self.elevation_slider.setValue(0)
        self.elevation_label = QLabel("0°")
        el_layout.addWidget(self.elevation_slider)
        el_layout.addWidget(self.elevation_label)
        beam_layout.addLayout(el_layout)
        
        beam_group.setLayout(beam_layout)
        layout.addWidget(beam_group)
        
        # LFM 波形配置
        waveform_group = QGroupBox("LFM 波形参数")
        waveform_layout = QVBoxLayout()
        
        # 起始频率
        f0_layout = QHBoxLayout()
        f0_layout.addWidget(QLabel("起始频率 (GHz):"))
        self.f0_spinbox = QSpinBox()
        self.f0_spinbox.setRange(1, 20)
        self.f0_spinbox.setValue(10)
        self.f0_spinbox.setSingleStep(0.1)
        f0_layout.addWidget(self.f0_spinbox)
        waveform_layout.addLayout(f0_layout)
        
        # 带宽
        bw_layout = QHBoxLayout()
        bw_layout.addWidget(QLabel("带宽 (MHz):"))
        self.bw_spinbox = QSpinBox()
        self.bw_spinbox.setRange(1, 1000)
        self.bw_spinbox.setValue(100)
        bw_layout.addWidget(self.bw_spinbox)
        waveform_layout.addLayout(bw_layout)
        
        # 脉冲宽度
        pw_layout = QHBoxLayout()
        pw_layout.addWidget(QLabel("脉冲宽度 (μs):"))
        self.pw_spinbox = QSpinBox()
        self.pw_spinbox.setRange(1, 1000)
        self.pw_spinbox.setValue(10)
        pw_layout.addWidget(self.pw_spinbox)
        waveform_layout.addLayout(pw_layout)
        
        waveform_group.setLayout(waveform_layout)
        layout.addWidget(waveform_group)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("启动雷达")
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.azimuth_slider.valueChanged.connect(self.update_azimuth_label)
        self.elevation_slider.valueChanged.connect(self.update_elevation_label)
    
    def update_azimuth_label(self, value):
        self.azimuth_label.setText(f"{value}°")
    
    def update_elevation_label(self, value):
        self.elevation_label.setText(f"{value}°")
    
    def get_parameters(self):
        """获取当前配置参数"""
        return {
            'azimuth': self.azimuth_slider.value(),
            'elevation': self.elevation_slider.value(),
            'f0': self.f0_spinbox.value() * 1e9,  # GHz to Hz
            'bandwidth': self.bw_spinbox.value() * 1e6,  # MHz to Hz
            'pulse_width': self.pw_spinbox.value() * 1e-6  # μs to s
        }


class RadarDisplay(QWidget):
    """雷达数据显示面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建 Matplotlib 图形
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        
        # 创建子图
        self.ax_range = self.figure.add_subplot(2, 1, 1)  # 距离剖面
        self.ax_doppler = self.figure.add_subplot(2, 1, 2)  # 距离-多普勒图
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # 初始化显示
        self.initialize_plots()
    
    def initialize_plots(self):
        """初始化图表"""
        # 距离剖面
        self.ax_range.set_title('距离剖面 (Range Profile)')
        self.ax_range.set_xlabel('距离 (m)')
        self.ax_range.set_ylabel('幅度 (dB)')
        self.range_line, = self.ax_range.plot([], [], 'b-', linewidth=1.5)
        self.ax_range.grid(True)
        self.ax_range.set_xlim(0, 3000)
        self.ax_range.set_ylim(-60, 0)
        
        # 距离-多普勒图
        self.ax_doppler.set_title('距离-多普勒图 (Range-Doppler Map)')
        self.ax_doppler.set_xlabel('距离 (m)')
        self.ax_doppler.set_ylabel('速度 (m/s)')
        self.doppler_img = self.ax_doppler.imshow(
            np.zeros((100, 100)), 
            aspect='auto', 
            cmap='jet',
            extent=[0, 3000, -50, 50]
        )
        self.ax_doppler.grid(True)
        
        self.canvas.draw()
    
    def update_display(self, range_data, doppler_map):
        """更新显示数据"""
        # 更新距离剖面
        distances = np.linspace(0, 3000, len(range_data))
        self.range_line.set_data(distances, range_data)
        
        # 更新距离-多普勒图
        self.doppler_img.set_array(doppler_map)
        
        self.canvas.draw()


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.controller = RISController()
        self.timer = QTimer()
        self.is_running = False
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        self.setWindowTitle('PLFM-RIS 雷达控制系统 v1.0')
        self.setGeometry(100, 100, 1400, 900)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧控制面板
        control_panel = RISControlPanel()
        main_layout.addWidget(control_panel, stretch=1)
        
        # 右侧显示面板
        display_tabs = QTabWidget()
        
        # 距离剖面标签页
        range_tab = RadarDisplay()
        display_tabs.addTab(range_tab, "距离剖面")
        
        # TODO: 添加其他标签页 (B显, PPI等)
        
        main_layout.addWidget(display_tabs, stretch=3)
        
        # 保存引用
        self.control_panel = control_panel
        self.radar_display = range_tab
    
    def setup_connections(self):
        """设置信号连接"""
        self.control_panel.start_btn.clicked.connect(self.start_radar)
        self.control_panel.stop_btn.clicked.connect(self.stop_radar)
        self.timer.timeout.connect(self.update_display)
    
    def start_radar(self):
        """启动雷达"""
        params = self.control_panel.get_parameters()
        
        try:
            self.controller.connect()
            self.controller.configure(params)
            self.controller.start()
            
            self.is_running = True
            self.control_panel.start_btn.setEnabled(False)
            self.control_panel.stop_btn.setEnabled(True)
            
            # 启动定时更新
            self.timer.start(100)  # 10 Hz 更新率
            
            QMessageBox.information(self, "成功", "雷达已启动")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败: {str(e)}")
    
    def stop_radar(self):
        """停止雷达"""
        try:
            self.controller.stop()
            self.controller.disconnect()
            
            self.is_running = False
            self.control_panel.start_btn.setEnabled(True)
            self.control_panel.stop_btn.setEnabled(False)
            
            self.timer.stop()
            
            QMessageBox.information(self, "成功", "雷达已停止")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"停止失败: {str(e)}")
    
    def update_display(self):
        """更新显示"""
        if not self.is_running:
            return
        
        try:
            # 从控制器获取数据
            range_data, doppler_map = self.controller.get_data()
            
            # 更新显示
            self.radar_display.update_display(range_data, doppler_map)
            
        except Exception as e:
            print(f"更新显示失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.is_running:
            self.stop_radar()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
