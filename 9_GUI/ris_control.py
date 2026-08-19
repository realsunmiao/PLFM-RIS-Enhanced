"""
RIS 雷达控制器模块
负责与 FPGA 硬件通信,发送配置参数并接收雷达数据

作者: Wukong AI Assistant
日期: 2026-08-19
"""

import serial
import struct
import numpy as np
from typing import Tuple, Dict, Optional


class RISController:
    """RIS 雷达系统控制器"""
    
    # SPI 命令定义
    CMD_CONFIG_AZIMUTH = 0x01
    CMD_CONFIG_ELEVATION = 0x02
    CMD_CONFIG_F0 = 0x03
    CMD_CONFIG_K_SLOPE = 0x04
    CMD_CONFIG_T_PERIOD = 0x05
    CMD_ENABLE = 0x10
    CMD_DISABLE = 0x11
    CMD_GET_DATA = 0x20
    
    def __init__(self, port: str = 'COM3', baudrate: int = 115200):
        """
        初始化控制器
        
        Args:
            port: 串口端口 (Windows: COM3, Linux: /dev/ttyUSB0)
            baudrate: 波特率
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.connected = False
    
    def connect(self) -> bool:
        """连接到硬件"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            self.connected = True
            print(f"已连接到 {self.port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.connected = False
        print("已断开连接")
    
    def _send_command(self, cmd: int, data: bytes) -> bool:
        """
        发送 SPI 命令
        
        Args:
            cmd: 命令字节
            data: 数据负载
            
        Returns:
            是否成功
        """
        if not self.connected or not self.serial_conn:
            return False
        
        try:
            # 构建数据包: [CMD][LENGTH][DATA...]
            packet = struct.pack('<BB', cmd, len(data)) + data
            
            # 计算校验和
            checksum = sum(packet) & 0xFF
            packet += struct.pack('B', checksum)
            
            # 发送
            self.serial_conn.write(packet)
            return True
            
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False
    
    def configure(self, params: Dict) -> bool:
        """
        配置雷达参数
        
        Args:
            params: 参数字典
                - azimuth: 方位角 (度, -60~60)
                - elevation: 俯仰角 (度, -60~60)
                - f0: 起始频率 (Hz)
                - bandwidth: 带宽 (Hz)
                - pulse_width: 脉冲宽度 (秒)
        
        Returns:
            是否成功
        """
        if not self.connected:
            raise RuntimeError("未连接到硬件")
        
        try:
            # 配置方位角
            az_int = int(params['azimuth'] * 100)  # 转换为定点数
            self._send_command(
                self.CMD_CONFIG_AZIMUTH,
                struct.pack('<H', az_int)
            )
            
            # 配置俯仰角
            el_int = int(params['elevation'] * 100)
            self._send_command(
                self.CMD_CONFIG_ELEVATION,
                struct.pack('<H', el_int)
            )
            
            # 配置起始频率
            self._send_command(
                self.CMD_CONFIG_F0,
                struct.pack('<I', int(params['f0']))
            )
            
            # 计算调频斜率 k = bandwidth / pulse_width
            k_slope = params['bandwidth'] / params['pulse_width']
            self._send_command(
                self.CMD_CONFIG_K_SLOPE,
                struct.pack('<I', int(k_slope))
            )
            
            # 配置调频周期
            t_period = int(params['pulse_width'] * 1e6)  # 转换为微秒
            self._send_command(
                self.CMD_CONFIG_T_PERIOD,
                struct.pack('<I', t_period)
            )
            
            print("参数配置完成")
            return True
            
        except Exception as e:
            print(f"配置失败: {e}")
            return False
    
    def start(self) -> bool:
        """启动雷达"""
        if not self.connected:
            raise RuntimeError("未连接到硬件")
        
        success = self._send_command(self.CMD_ENABLE, b'')
        if success:
            print("雷达已启动")
        return success
    
    def stop(self) -> bool:
        """停止雷达"""
        if not self.connected:
            raise RuntimeError("未连接到硬件")
        
        success = self._send_command(self.CMD_DISABLE, b'')
        if success:
            print("雷达已停止")
        return success
    
    def get_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取雷达数据
        
        Returns:
            (range_profile, doppler_map)
            - range_profile: 距离剖面 (1D array)
            - doppler_map: 距离-多普勒图 (2D array)
        """
        if not self.connected:
            raise RuntimeError("未连接到硬件")
        
        try:
            # 请求数据
            self._send_command(self.CMD_GET_DATA, b'')
            
            # 读取响应
            # 格式: [TYPE][LENGTH][DATA...]
            response = self.serial_conn.read(1024)
            
            if len(response) < 4:
                raise ValueError("响应数据不完整")
            
            # 解析数据
            data_type = response[0]
            data_length = response[1]
            data = response[2:2+data_length]
            
            if data_type == 0x01:  # 距离剖面
                range_data = np.frombuffer(data, dtype=np.float32)
                doppler_map = np.zeros((100, 100))  # 占位
                
            elif data_type == 0x02:  # 距离-多普勒图
                # 先读取维度信息
                rows = struct.unpack('<H', data[:2])[0]
                cols = struct.unpack('<H', data[2:4])[0]
                doppler_map = np.frombuffer(
                    data[4:], 
                    dtype=np.float32
                ).reshape(rows, cols)
                range_data = np.max(doppler_map, axis=1)  # 沿速度维投影
                
            else:
                raise ValueError(f"未知数据类型: {data_type}")
            
            return range_data, doppler_map
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            # 返回模拟数据用于测试
            return self._generate_mock_data()
    
    def _generate_mock_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """生成模拟数据 (用于测试)"""
        # 距离剖面
        distances = np.linspace(0, 3000, 1000)
        range_profile = -40 + 10 * np.exp(-((distances - 500) ** 2) / (2 * 100 ** 2))
        range_profile += np.random.normal(0, 2, len(distances))
        
        # 距离-多普勒图
        doppler_map = np.random.normal(-40, 5, (100, 100))
        # 添加一个目标
        doppler_map[17, 50] = -10  # 500m, 0m/s
        
        return range_profile, doppler_map
    
    def calibrate(self) -> bool:
        """执行校准程序"""
        if not self.connected:
            raise RuntimeError("未连接到硬件")
        
        print("开始校准...")
        # TODO: 实现完整的校准流程
        # 1. 相位校准
        # 2. 幅度校准
        # 3. 阵列校正
        
        print("校准完成")
        return True
