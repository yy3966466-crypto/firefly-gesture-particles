' Visio VBScript for System Architecture Diagram
' Usage: Open Visio -> View -> Macros -> Run this script
' Or: CScript this_file.vbs

Dim visApp, doc, page, stencil
Dim cx, boxW, boxH, layerY(3), colors(3)
Dim i

cx = 4.0
boxW = 2.8
boxH = 0.6

colors(0) = "&H4472C4"  ' Blue  - 采集层
colors(1) = "&H548235"  ' Green - 信号层
colors(2) = "&HBF8F00"  ' Gold  - 应用层
colors(3) = "&HC55A11"  ' Orange- 交互层

layerY(0) = 1.5  ' 数据采集层
layerY(1) = 2.7  ' 信号处理层
layerY(2) = 3.9  ' 应用功能层
layerY(3) = 5.1  ' 人机交互层

Set visApp = CreateObject("Visio.Application")
visApp.Visible = True
Set doc = visApp.Documents.Add("")
Set page = visApp.ActivePage

' Set page size to A4 landscape
page.PageSheet.Cells("PageWidth").ResultIU = 11.69
page.PageSheet.Cells("PageHeight").ResultIU = 8.27

' Add title
Set titleShape = page.DrawRectangle(1, 7.5, 7, 7.0)
titleShape.Cells("Width").ResultIU = 4.5
titleShape.Cells("Height").ResultIU = 0.4
titleShape.Text = "系统四层模块化架构图"
titleShape.Cells("Char.Size").ResultIU = 14
titleShape.Cells("Char.Font").ResultIU = "SimHei"
titleShape.Cells("Para.HorzAlign").ResultIU = 1  ' Center
titleShape.Cells("FillForegn").ResultIU = &HFFFFFF
titleShape.Cells("LineColor").ResultIU = &HFFFFFF

' Layer names and details
Dim names(3), details(3)
names(0) = "数据采集层"
names(1) = "信号处理层"
names(2) = "应用功能层"
names(3) = "人机交互层"

details(0) = "MIT-BIH 心电数据库" & vbCrLf & _
             "BIDMC 呼吸数据库" & vbCrLf & _
             "NTC 热敏电阻（串口9600）" & vbCrLf & _
             "USB 串口通信驱动"

details(1) = "FIR 带通滤波（5~18 Hz）" & vbCrLf & _
             "差分阈值 R 波检测" & vbCrLf & _
             "LMS 自适应呼吸增强" & vbCrLf & _
             "体温低通滤波与线性校准"

details(2) = "数据存储（.mat 格式导出）" & vbCrLf & _
             "历史数据回放分析" & vbCrLf & _
             "异常报警（声光 + 日志）" & vbCrLf & _
             "语音播报（TTS）"

details(3) = "App Designer GUI 界面" & vbCrLf & _
             "实时波形显示（ECG / Resp）" & vbCrLf & _
             "数字体温显示" & vbCrLf & _
             "用户控制面板（按钮 / 下拉菜单）"

' Draw each layer
Dim boxShapes(3)
For i = 0 To 3
    Dim left, top, right, bottom
    left = cx - boxW / 2
    top = layerY(i) + boxH / 2
    right = cx + boxW / 2
    bottom = layerY(i) - boxH / 2

    Set boxShapes(i) = page.DrawRectangle(left, top, right, bottom)
    boxShapes(i).Text = names(i) & vbCrLf & "────────────────" & vbCrLf & details(i)
    boxShapes(i).Cells("FillForegn").ResultIU = colors(i)
    boxShapes(i).Cells("FillBkgnd").ResultIU = &HFFFFFF
    boxShapes(i).Cells("LineWeight").ResultIU = 0.02

    ' Set formatting
    boxShapes(i).Cells("Char.Size").Formula = "9pt"
    boxShapes(i).Cells("Para.HorzAlign").ResultIU = 1  ' Center
Next

' Draw arrows between layers
For i = 0 To 2
    Dim arrowY
    arrowY = (layerY(i) - boxH / 2 + layerY(i+1) + boxH / 2) / 2

    ' Simple line with arrow
    Set arrowShape = page.DrawLine(cx, layerY(i) - boxH / 2 - 0.05, cx, layerY(i+1) + boxH / 2 + 0.05)
    arrowShape.Cells("LineColor").ResultIU = &H888888
    arrowShape.Cells("LineWeight").ResultIU = 0.015
    arrowShape.Cells("BegArrow").ResultIU = 0
    arrowShape.Cells("EndArrow").ResultIU = 1

    ' Add data flow label beside arrow
    Set labelShape = page.DrawRectangle(cx + 0.3, arrowY - 0.1, cx + 0.8, arrowY + 0.1)
    labelShape.Text = "数据流"
    labelShape.Cells("Char.Size").ResultIU = 7
    labelShape.Cells("FillForegn").ResultIU = &HFFFFFF
    labelShape.Cells("LineColor").ResultIU = &HFFFFFF
Next

MsgBox "架构图已生成！"

Set visApp = Nothing
