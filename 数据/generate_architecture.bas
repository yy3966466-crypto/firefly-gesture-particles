Sub GenerateArchitectureDiagram()
    Dim cx As Double, boxW As Double, boxH As Double
    Dim layerY(3) As Double
    Dim i As Integer
    Dim boxShapes(3) As Visio.Shape

    cx = 4.0
    boxW = 2.8
    boxH = 0.6

    layerY(0) = 1.5  ' 数据采集层
    layerY(1) = 2.7  ' 信号处理层
    layerY(2) = 3.9  ' 应用功能层
    layerY(3) = 5.1  ' 人机交互层

    ' Set page size to A4 landscape
    ActivePage.PageSheet.Cells("PageWidth").ResultIU = 11.69
    ActivePage.PageSheet.Cells("PageHeight").ResultIU = 8.27

    ' Title
    Set titleShape = ActivePage.DrawRectangle(1, 7.5, 7, 7.0)
    titleShape.Text = "系统四层模块化架构图"
    titleShape.Cells("Char.Size").ResultIU = 14
    titleShape.Cells("Para.HorzAlign").ResultIU = 1
    titleShape.Cells("FillForegn").ResultIU = &HFFFFFF
    titleShape.Cells("LineColor").ResultIU = &HFFFFFF

    ' Layer data
    Dim names(3) As String
    Dim details(3) As String
    Dim colors(3) As Long

    names(0) = "数据采集层"
    names(1) = "信号处理层"
    names(2) = "应用功能层"
    names(3) = "人机交互层"

    colors(0) = &H4472C4  ' Blue
    colors(1) = &H548235  ' Green
    colors(2) = &HBF8F00  ' Gold
    colors(3) = &HC55A11  ' Orange

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
    For i = 0 To 3
        Dim left As Double, top As Double, right As Double, bottom As Double
        left = cx - boxW / 2
        top = layerY(i) + boxH / 2
        right = cx + boxW / 2
        bottom = layerY(i) - boxH / 2

        Set boxShapes(i) = ActivePage.DrawRectangle(left, top, right, bottom)
        boxShapes(i).Text = names(i) & vbCrLf & "────────────────" & vbCrLf & details(i)
        boxShapes(i).Cells("FillForegn").ResultIU = &HFFFFFF
        boxShapes(i).Cells("FillBkgnd").ResultIU = colors(i)
        boxShapes(i).Cells("LineWeight").ResultIU = 0.02
        boxShapes(i).Cells("Char.Size").Formula = "9pt"
        boxShapes(i).Cells("Para.HorzAlign").ResultIU = 1
    Next i

    ' Draw arrows
    For i = 0 To 2
        Set arrowShape = ActivePage.DrawLine(cx, layerY(i) - boxH / 2 - 0.05, cx, layerY(i + 1) + boxH / 2 + 0.05)
        arrowShape.Cells("LineColor").ResultIU = &H888888
        arrowShape.Cells("LineWeight").ResultIU = 0.015
        arrowShape.Cells("EndArrow").ResultIU = 1

        ' Data flow label
        Dim arrowY As Double
        arrowY = (layerY(i) - boxH / 2 + layerY(i + 1) + boxH / 2) / 2
        Set labelShape = ActivePage.DrawRectangle(cx + 0.3, arrowY - 0.08, cx + 0.7, arrowY + 0.08)
        labelShape.Text = "数据流"
        labelShape.Cells("Char.Size").ResultIU = 7
        labelShape.Cells("FillForegn").ResultIU = &HFFFFFF
        labelShape.Cells("LineColor").ResultIU = &HFFFFFF
        labelShape.Cells("Para.HorzAlign").ResultIU = 1
    Next i

    MsgBox "架构图已生成！"
End Sub
