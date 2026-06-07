# 通用型多生理参数监护系统（MATLAB）

本项目根据题目要求实现了一个可直接运行的 MATLAB 上位机监护平台，支持三路生理参数展示，并且会在每次准备数据时随机抽取公开记录：

- 心电：自动下载并解析 PhysioNet `MIT-BIH Arrhythmia Database` 的随机记录，默认优先抽取异常心律记录
- 呼吸：自动下载并读取 PhysioNet `BIDMC PPG and Respiration Dataset` 的随机记录，默认优先抽取呼吸频率更异常或波动更明显的记录
- 体温：默认使用 `demo` 占位数据运行；后续可切换到 GooDeTek Type-C 红外测温模块串口接入

## 目录结构

- `main.m`：启动 GUI
- `smoke_test.m`：下载数据并验证算法链路
- `export_analysis_report.m`：导出 ECG/呼吸处理前后对比图和统计数据
- `src/BioMonitorApp.m`：主界面与监护逻辑
- `src/+bioio/`：公开数据下载与解析
- `src/+bioalg/`：心电/呼吸算法
- `src/+tempsrc/`：体温 demo 与串口采集

## 运行方式

```matlab
main
```

或先做一次链路验证：

```matlab
smoke_test
```

如需导出论文/答辩可用的图片和数据：

```matlab
export_analysis_report
```

## 已实现功能

- 自动下载 MIT-BIH ECG 与 BIDMC 呼吸数据
- 每次点击“随机抽样/准备数据”都会重新抽取 ECG 与呼吸公开记录
- MIT-BIH `212` 原始格式 ECG 解析，不依赖第三方 WFDB 工具箱
- ECG 数字滤波 + 差分阈值 R 波检测
- 呼吸信号自适应滤波增强 + 波峰检测 + 呼吸率计算
- 三路信号 GUI 展示
- 关键参数实时显示：心率、呼吸率、体温
- 异常报警提示
- 本地保存会话数据
- 一键导出 ECG/呼吸处理前后对比图、检测结果图、数据摘要表与局部数据 CSV

## 体温模块接入说明

根据你提供的 GooDeTek `TypeC测温模块使用指南`，当前代码已经预留真实串口接口，默认参数如下：

- 串口参数：`9600, 8, N, 1`
- 接收格式：ASCII
- 发送命令：HEX 单字节
- 物温命令：`0xAA`
- 体温命令：`0xAB`
- 返回示例：`+000365`，换算为 `36.5 °C`

如果你后面买到实物，只需要：

1. 在 GUI 里把体温源切到 `serial`
2. 填入实际 `COM` 口
3. 保持默认 `9600` 波特率（若你的模块是 FS 20ms 型号，可改成 `115200`）
4. 点击“开始监护”

## 数据来源

- MIT-BIH Arrhythmia Database  
  <https://physionet.org/content/mitdb/1.0.0/>
- BIDMC PPG and Respiration Dataset  
  <https://physionet.org/content/bidmc/1.0.0/>

## 说明

- 当前没有硬件时，平台仍可完整运行 ECG、呼吸与体温占位展示，不影响算法、界面和整体联调。
- 真实体温串口接入后，我后续可以继续帮你把采样频率、稳定性、异常帧处理和保存格式再针对实物调优。
