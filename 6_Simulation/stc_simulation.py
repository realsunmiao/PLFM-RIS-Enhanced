"""
STC 算法仿真脚本 - 时空编码雷达系统仿真

功能:
  1. 生成 LFM 信号
  2. 计算波束赋形方向图
  3. 模拟目标回波
  4. 脉冲压缩和距离-多普勒处理

作者: Wukong AI Assistant
日期: 2026-08-19
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve


def generate_lfm_signal(f0, bandwidth, pulse_width, fs):
    """
    生成线性调频(LFM)信号
    
    参数:
        f0: 起始频率 (Hz)
        bandwidth: 带宽 (Hz)
        pulse_width: 脉冲宽度 (s)
        fs: 采样率 (Hz)
    
    返回:
        t: 时间向量
        signal: LFM 信号
    """
    t = np.arange(0, pulse_width, 1/fs)
    k = bandwidth / pulse_width  # 调频斜率
    
    # LFM 信号: s(t) = exp(j*2*pi*(f0*t + 0.5*k*t^2))
    phase = 2 * np.pi * (f0 * t + 0.5 * k * t**2)
    signal = np.exp(1j * phase)
    
    return t, signal


def array_factor_2d(theta, phi, azimuth, elevation, wavelength, rows=8, cols=8):
    """
    计算 2D 阵列的阵列因子
    
    参数:
        theta: 俯仰角扫描范围 (度)
        phi: 方位角扫描范围 (度)
        azimuth: 目标方位角 (度)
        elevation: 目标俯仰角 (度)
        wavelength: 波长 (m)
        rows: 行数
        cols: 列数
    
    返回:
        AF: 阵列因子幅度
    """
    d = wavelength / 2  # 阵元间距
    
    THETA, PHI = np.meshgrid(theta, phi)
    AF = np.zeros_like(THETA, dtype=complex)
    
    for m in range(rows):
        for n in range(cols):
            x = n * d
            y = m * d
            
            # 期望波束指向的相位
            psi_steering = (2 * np.pi / wavelength) * (
                x * np.sin(np.radians(elevation)) * np.cos(np.radians(azimuth)) +
                y * np.sin(np.radians(elevation)) * np.sin(np.radians(azimuth))
            )
            
            # 观察方向的相位
            psi_obs = (2 * np.pi / wavelength) * (
                x * np.sin(np.radians(THETA)) * np.cos(np.radians(PHI)) +
                y * np.sin(np.radians(THETA)) * np.sin(np.radians(PHI))
            )
            
            AF += np.exp(1j * (psi_obs - psi_steering))
    
    return np.abs(AF) / (rows * cols)


def pulse_compression(received_signal, reference_signal):
    """
    脉冲压缩 (匹配滤波)
    
    参数:
        received_signal: 接收信号
        reference_signal: 参考信号 (LFM)
    
    返回:
        compressed: 压缩后的信号
    """
    # 匹配滤波器是参考信号的共轭反转
    matched_filter = np.conj(reference_signal[::-1])
    
    # 卷积实现匹配滤波
    compressed = fftconvolve(received_signal, matched_filter, mode='same')
    
    return compressed


def range_doppler_processing(data_matrix, fs, prf):
    """
    距离-多普勒处理
    
    参数:
        data_matrix: 距离慢时间数据矩阵 (快时间 x 脉冲数)
        fs: 采样率
        prf: 脉冲重复频率
    
    返回:
        rd_map: 距离-多普勒图
    """
    # 距离维 FFT (已在脉冲压缩后)
    # 多普勒维 FFT
    doppler_fft = np.fft.fftshift(np.fft.fft(data_matrix, axis=1), axes=1)
    
    # 取幅度
    rd_map = np.abs(doppler_fft)
    
    # 归一化到 dB
    rd_map_db = 20 * np.log10(rd_map / np.max(rd_map) + 1e-10)
    
    return rd_map_db


def simulate_target_echo(lfm_signal, target_range, target_velocity, c, fs,
                         pulse_idx=0, prf=10e3):
    """
    模拟目标回波

    参数:
        lfm_signal: 发射信号
        target_range: 目标距离 (m)
        target_velocity: 目标速度 (m/s)
        c: 光速 (m/s)
        fs: 采样率
        pulse_idx: 脉冲序号（慢时间索引，用于跨脉冲多普勒相位累积）
        prf: 脉冲重复频率 (Hz)

    返回:
        echo: 回波信号
    """
    # 计算时延
    time_delay = 2 * target_range / c
    
    # 计算多普勒频移
    f0 = 10.5e9  # 载频
    doppler_freq = 2 * target_velocity * f0 / c
    
    # 采样延迟
    sample_delay = int(time_delay * fs)
    
    # 生成回波 (简化模型)
    echo = np.zeros_like(lfm_signal, dtype=complex)
    
    if sample_delay < len(lfm_signal):
        # 添加时延和多普勒频移
        # 多普勒相位 = 脉内快时间项 + 跨脉冲慢时间项 (pulse_idx/prf)，
        # 后者保证脉冲多普勒处理能正确测速
        t = np.arange(len(lfm_signal) - sample_delay) / fs
        slow_time = pulse_idx / prf
        doppler_phase = 2 * np.pi * doppler_freq * (t + slow_time)
        
        echo[sample_delay:] = lfm_signal[:-sample_delay] * np.exp(1j * doppler_phase) * 0.1
    
    return echo


def main():
    """主仿真流程"""
    
    # ===== 参数设置 =====
    f0 = 10.5e9          # 起始频率 10.5 GHz
    bandwidth = 100e6    # 带宽 100 MHz
    pulse_width = 10e-6  # 脉冲宽度 10 μs
    fs = 200e6           # 采样率 200 MHz
    c = 3e8              # 光速
    
    # 目标参数
    target_range = 500   # 目标距离 500 m
    target_velocity = 10 # 目标速度 10 m/s
    
    # 波束指向
    # 注意: array_factor_2d 的 steering 相位与 sin(elevation) 成正比，
    # elevation=0 时波束在方位维无指向性（水平扇面），故取俯仰角 30°
    azimuth_target = 30  # 方位角 30°
    elevation_target = 30 # 俯仰角 30°
    
    print("=" * 60)
    print("PLFM-RIS 雷达系统仿真")
    print("=" * 60)
    print(f"载频: {f0/1e9:.1f} GHz")
    print(f"带宽: {bandwidth/1e6:.0f} MHz")
    print(f"脉冲宽度: {pulse_width*1e6:.0f} μs")
    print(f"目标距离: {target_range} m")
    print(f"目标速度: {target_velocity} m/s")
    print(f"波束指向: 方位角 {azimuth_target}°, 俯仰角 {elevation_target}°")
    print("=" * 60)
    
    # ===== 1. 生成 LFM 信号 =====
    print("\n[1/4] 生成 LFM 信号...")
    t, lfm_signal = generate_lfm_signal(f0, bandwidth, pulse_width, fs)
    print(f"  信号长度: {len(lfm_signal)} 采样点")
    
    # ===== 2. 计算波束方向图 =====
    print("[2/4] 计算波束方向图...")
    wavelength = c / f0
    theta_scan = np.linspace(-60, 60, 121)
    phi_scan = np.linspace(-60, 60, 121)
    
    AF = array_factor_2d(theta_scan, phi_scan, azimuth_target, elevation_target, wavelength)
    
    # ===== 3. 模拟目标回波并脉冲压缩 =====
    print("[3/4] 模拟目标回波并进行脉冲压缩...")
    echo = simulate_target_echo(lfm_signal, target_range, target_velocity, c, fs)
    compressed = pulse_compression(echo, lfm_signal)
    
    # 计算理论距离分辨率
    range_resolution = c / (2 * bandwidth)
    print(f"  理论距离分辨率: {range_resolution:.2f} m")
    
    # ===== 4. 距离-多普勒处理 (多脉冲) =====
    print("[4/4] 距离-多普勒处理...")
    num_pulses = 64
    prf = 10e3  # 脉冲重复频率 10 kHz
    
    data_matrix = np.zeros((len(compressed), num_pulses), dtype=complex)
    
    for i in range(num_pulses):
        # 模拟不同时刻的目标位置（跨脉冲慢时间相位累积，支持多普勒测速）
        current_range = target_range + target_velocity * (i / prf)
        echo_pulse = simulate_target_echo(lfm_signal, current_range,
                                          target_velocity, c, fs,
                                          pulse_idx=i, prf=prf)
        compressed_pulse = pulse_compression(echo_pulse, lfm_signal)
        data_matrix[:, i] = compressed_pulse
    
    rd_map = range_doppler_processing(data_matrix, fs, prf)
    
    # ===== 可视化结果 =====
    print("\n生成可视化图表...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 图 1: LFM 信号时域
    ax1 = axes[0, 0]
    ax1.plot(t * 1e6, np.real(lfm_signal), 'b-', linewidth=0.5, label='Real')
    ax1.plot(t * 1e6, np.imag(lfm_signal), 'r--', linewidth=0.5, label='Imag')
    ax1.set_xlabel('Time (μs)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('LFM Signal (Time Domain)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图 2: 波束方向图
    ax2 = axes[0, 1]
    im2 = ax2.contourf(phi_scan, theta_scan, 20 * np.log10(AF + 1e-10), 
                       levels=50, cmap='jet')
    ax2.set_xlabel('Azimuth (°)')
    ax2.set_ylabel('Elevation (°)')
    ax2.set_title(f'Beam Pattern (Steered to {azimuth_target}°, {elevation_target}°)')
    plt.colorbar(im2, ax=ax2, label='Gain (dB)')
    ax2.grid(True, alpha=0.3)
    
    # 图 3: 脉冲压缩结果
    ax3 = axes[1, 0]
    # 匹配滤波 'same' 模式引入 (n-1)-(n-1)//2 个采样点的时延偏移，
    # 补偿后脉冲压缩峰值对齐到目标真实距离
    delay_offset = (len(compressed) - 1) - (len(compressed) - 1) // 2
    range_axis = (np.arange(len(compressed)) - delay_offset) * c / (2 * fs)
    ax3.plot(range_axis, 20 * np.log10(np.abs(compressed) + 1e-10), 'b-', linewidth=1)
    ax3.set_xlabel('Range (m)')
    ax3.set_ylabel('Amplitude (dB)')
    ax3.set_title('Pulse Compression Result')
    ax3.set_xlim([0, 1000])
    ax3.grid(True, alpha=0.3)
    
    # 标记目标位置
    ax3.axvline(target_range, color='r', linestyle='--', label=f'Target at {target_range}m')
    ax3.legend()
    
    # 图 4: 距离-多普勒图
    ax4 = axes[1, 1]
    doppler_axis = np.linspace(-prf/2, prf/2, num_pulses)
    extent = [0, range_axis[-1], doppler_axis[0], doppler_axis[-1]]
    im4 = ax4.imshow(rd_map, aspect='auto', cmap='jet', extent=extent, origin='lower')
    ax4.set_xlabel('Range (m)')
    ax4.set_ylabel('Velocity (m/s)')
    ax4.set_title('Range-Doppler Map')
    plt.colorbar(im4, ax=ax4, label='Amplitude (dB)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stc_simulation_result.png', dpi=300, bbox_inches='tight')
    print("  已保存: stc_simulation_result.png")
    
    plt.show()
    
    print("\n" + "=" * 60)
    print("仿真完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
