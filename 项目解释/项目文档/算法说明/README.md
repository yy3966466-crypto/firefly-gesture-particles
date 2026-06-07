# 算法说明索引

本文件夹集中说明项目中按照题目要求实现或对应实现的各类算法。每份文档都包含算法目标、处理流程、关键参数、输入输出、可视化方式和对应源码。

## 文档列表

| 文档 | 内容 |
| --- | --- |
| `01_算法总体流程.md` | 多生理参数算法链路、数据流和模块关系 |
| `02_ECG心电算法.md` | ECG 预处理、带通滤波、差分阈值、R 波检测、心率计算 |
| `03_呼吸信号算法.md` | 呼吸去基线、带通滤波、ALE/LMS 自适应增强、呼吸峰检测 |
| `04_体温读取算法.md` | Type-C 体温模块串口读取、回包解析、demo 序列 |
| `05_融合分析与报警算法.md` | 心率/呼吸率/体温阈值报警、心律/呼吸节律判断、心呼相关、趋势分析 |
| `06_可视化与验证指标.md` | GUI 实时可视化、导出图、CSV、SNR 与统计指标 |

## 源码对应关系

| 算法方向 | 源码 |
| --- | --- |
| 通用带通滤波 | `src/+bioalg/bandpassSignal.m` |
| ECG 处理 | `src/+bioalg/processEcg.m` |
| 呼吸处理 | `src/+bioalg/processRespiration.m` |
| 峰值筛选 | `src/+bioalg/selectPeaks.m` |
| SNR 估计 | `src/+bioalg/estimateSnr.m` |
| 数据读取与缓存 | `src/+bioio/` |
| 体温串口 | `src/+tempsrc/TemperatureStream.m` |
| 主界面融合分析 | `src/BioMonitorApp.m` |
| 图表导出 | `src/+bioout/exportAnalysisReport.m` |

## 总体说明

当前实现采用 base MATLAB 可运行的方案，尽量减少对外部工具箱的依赖。部分题目中提到的“FIR”在当前代码中以 FFT 频域带通方式实现等效的带通滤波功能；呼吸自适应滤波采用 ALE 结构和 LMS 权值更新形式。文档中会明确写出当前实现与题目描述的对应关系。
