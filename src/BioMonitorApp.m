classdef BioMonitorApp < handle
    %BIOMONITORAPP GUI for ECG, respiration, and temperature monitoring.

    properties (Access = private)
        ProjectRoot
        DataManifest = struct()
        CurrentPlan = struct()
        ECG = struct()
        Resp = struct()
        TempStream = []
        TimerObj = []
        IsRunning = false
        IsBusy = false
        ECGCursor = 1
        RespCursor = 1
        SessionStart = datetime('now')
        TempTimes = zeros(0, 1)
        TempValues = zeros(0, 1)
        LogLines = {'等待操作...'}
        LastAlarmState = ""
        LastAlarmSoundTime = -inf
        AlarmPausedUntil = -inf
        % Per-priority cooldown (seconds): crisis=1, warning=2, advisory=5
        AlarmSoundCooldown = struct('crisis', 1, 'warning', 2, 'advisory', 5)
        TtsSpeaker = []
        LastPlotRefreshTime = -inf
        LastMetricRefreshTime = -inf
        LastAnalysisRefreshTime = -inf
        LastTempReadTime = -inf
        CurrentTemp = NaN
        CurrentTempMeta = struct('mode', 'demo', 'status', '待采样', 'rawText', '')
        PlotRefreshPeriod = 0.50
        MetricRefreshPeriod = 1.00
        AnalysisRefreshPeriod = 2.00
        TempReadPeriod = 0.50
        MaxPlotPoints = 1500
    end

    properties (Access = private)
        UIFigure
        DownloadButton
        StartButton
        StopButton
        SaveButton
        ExportButton
        RefreshPortsButton
        TempModeDropDown
        MeasurementDropDown
        PortField
        BaudRateField
        ModeDropDown
        PortsHintLabel
        RunningLamp
        DataStatusLabel
        TempStatusLabel
        HRValueLabel
        RRValueLabel
        TempValueLabel
        ECGAxes
        RespAxes
        TempAxes
        ECGLine
        ECGPeakScatter
        RespLine
        RespPeakScatter
        TempLine
        AlertArea
        AnalysisArea
        LogArea
    end

    methods
        function app = BioMonitorApp(projectRoot)
            app.ProjectRoot = projectRoot;
            app.buildUi();
            app.TimerObj = timer( ...
                'ExecutionMode', 'fixedRate', ...
                'Period', 0.25, ...
                'BusyMode', 'drop', ...
                'TimerFcn', @(~, ~) app.onTimerTick());

            app.updatePortList();
            app.logLine('界面已启动，可先点击”随机抽样/准备数据”。');
        end

        function delete(app)
            app.stopMonitoring();

            if ~isempty(app.TimerObj)
                try
                    delete(app.TimerObj);
                catch
                end
                app.TimerObj = [];
            end

            if ~isempty(app.TempStream)
                try
                    delete(app.TempStream);
                catch
                end
                app.TempStream = [];
            end

            if ~isempty(app.UIFigure) && isvalid(app.UIFigure)
                fig = app.UIFigure;
                app.UIFigure = [];
                try
                    fig.CloseRequestFcn = [];
                catch
                end
                delete(fig);
            end
        end
    end

    methods (Access = private)
        function buildUi(app)
            initialPosition = localInitialFigurePosition();
            app.UIFigure = uifigure( ...
                'Name', '通用型多生理参数监护系统', ...
                'Position', initialPosition, ...
                'Color', [0.96, 0.97, 0.99], ...
                'Visible', 'off', ...
                'CloseRequestFcn', @(~, ~) app.delete());

            mainGrid = uigridlayout(app.UIFigure, [4, 2]);
            mainGrid.RowHeight = {92, '1x', '1x', '1x'};
            mainGrid.ColumnWidth = {'3.2x', '1.25x'};
            mainGrid.Padding = [14, 14, 14, 14];
            mainGrid.RowSpacing = 10;
            mainGrid.ColumnSpacing = 10;

            controlPanel = uipanel(mainGrid, ...
                'Title', '控制区', ...
                'BackgroundColor', 'white');
            controlPanel.Layout.Row = 1;
            controlPanel.Layout.Column = [1, 2];

            controlGrid = uigridlayout(controlPanel, [2, 11]);
            controlGrid.RowHeight = {30, 30};
            controlGrid.ColumnWidth = {115, 115, 90, 90, 100, 90, 110, 120, 100, '1x', 140};
            controlGrid.Padding = [10, 6, 10, 6];

            app.DownloadButton = uibutton(controlGrid, ...
                'Text', '随机抽样/准备数据', ...
                'ButtonPushedFcn', @(~, ~) app.prepareData(true));
            app.DownloadButton.Layout.Row = 1;
            app.DownloadButton.Layout.Column = 1;

            app.StartButton = uibutton(controlGrid, ...
                'Text', '开始监护', ...
                'ButtonPushedFcn', @(~, ~) app.startMonitoring());
            app.StartButton.Layout.Row = 1;
            app.StartButton.Layout.Column = 2;

            app.StopButton = uibutton(controlGrid, ...
                'Text', '停止', ...
                'ButtonPushedFcn', @(~, ~) app.stopMonitoring());
            app.StopButton.Layout.Row = 1;
            app.StopButton.Layout.Column = 3;

            app.SaveButton = uibutton(controlGrid, ...
                'Text', '保存会话', ...
                'ButtonPushedFcn', @(~, ~) app.saveSession());
            app.SaveButton.Layout.Row = 1;
            app.SaveButton.Layout.Column = 4;

            app.ExportButton = uibutton(controlGrid, ...
                'Text', '导出分析图', ...
                'ButtonPushedFcn', @(~, ~) app.exportAnalysis());
            app.ExportButton.Layout.Row = 1;
            app.ExportButton.Layout.Column = 5;

            app.RefreshPortsButton = uibutton(controlGrid, ...
                'Text', '刷新串口', ...
                'ButtonPushedFcn', @(~, ~) app.updatePortList());
            app.RefreshPortsButton.Layout.Row = 1;
            app.RefreshPortsButton.Layout.Column = 6;

            lbl = uilabel(controlGrid, ...
                'Text', '体温源', ...
                'HorizontalAlignment', 'center', ...
                'FontWeight', 'bold', ...
                'BackgroundColor', 'white');
            lbl.Layout.Row = 1;
            lbl.Layout.Column = 7;

            app.TempModeDropDown = uidropdown(controlGrid, ...
                'Items', {'demo', 'serial'}, ...
                'Value', 'demo');
            app.TempModeDropDown.Layout.Row = 1;
            app.TempModeDropDown.Layout.Column = 8;

            lbl = uilabel(controlGrid, ...
                'Text', '测温模式', ...
                'HorizontalAlignment', 'center', ...
                'FontWeight', 'bold', ...
                'BackgroundColor', 'white');
            lbl.Layout.Row = 1;
            lbl.Layout.Column = 9;

            app.MeasurementDropDown = uidropdown(controlGrid, ...
                'Items', {'body', 'object'}, ...
                'Value', 'body');
            app.MeasurementDropDown.Layout.Row = 1;
            app.MeasurementDropDown.Layout.Column = 10;

            app.RunningLamp = uilamp(controlGrid, 'Color', [0.55, 0.55, 0.55]);
            app.RunningLamp.Layout.Row = 1;
            app.RunningLamp.Layout.Column = 11;

            lbl = uilabel(controlGrid, ...
                'Text', 'COM端口', ...
                'HorizontalAlignment', 'center', ...
                'FontWeight', 'bold', ...
                'BackgroundColor', 'white');
            lbl.Layout.Row = 2;
            lbl.Layout.Column = 1;

            app.PortField = uieditfield(controlGrid, 'text', ...
                'Value', 'COM7', ...
                'HorizontalAlignment', 'right');
            app.PortField.Layout.Row = 2;
            app.PortField.Layout.Column = 2;

            lbl = uilabel(controlGrid, ...
                'Text', '波特率', ...
                'HorizontalAlignment', 'center', ...
                'FontWeight', 'bold', ...
                'BackgroundColor', 'white');
            lbl.Layout.Row = 2;
            lbl.Layout.Column = 3;

            app.BaudRateField = uieditfield(controlGrid, 'numeric', ...
                'Value', 9600, ...
                'Limits', [1200, 921600]);
            app.BaudRateField.Layout.Row = 2;
            app.BaudRateField.Layout.Column = 4;

            lbl = uilabel(controlGrid, ...
                'Text', '数据模式', ...
                'HorizontalAlignment', 'center', ...
                'FontWeight', 'bold', ...
                'BackgroundColor', 'white');
            lbl.Layout.Row = 2;
            lbl.Layout.Column = 5;

            app.ModeDropDown = uidropdown(controlGrid, ...
                'Items', {'abnormal', 'mixed', 'normal'}, ...
                'Value', 'abnormal');
            app.ModeDropDown.Layout.Row = 2;
            app.ModeDropDown.Layout.Column = 6;

            app.PortsHintLabel = uilabel(controlGrid, ...
                'Text', '可用串口: 检测中...', ...
                'BackgroundColor', 'white', ...
                'FontAngle', 'italic');
            app.PortsHintLabel.Layout.Row = 2;
            app.PortsHintLabel.Layout.Column = [7, 11];

            app.ECGAxes = uiaxes(mainGrid);
            app.ECGAxes.Layout.Row = 2;
            app.ECGAxes.Layout.Column = 1;
            title(app.ECGAxes, '心电信号（MIT-BIH 100）');
            xlabel(app.ECGAxes, '时间 / s');
            ylabel(app.ECGAxes, '幅值 / mV');
            grid(app.ECGAxes, 'on');
            app.ECGAxes.Box = 'on';
            hold(app.ECGAxes, 'on');
            app.ECGLine = plot(app.ECGAxes, nan, nan, 'LineWidth', 1.2, 'Color', [0.00, 0.37, 0.82]);
            app.ECGPeakScatter = scatter(app.ECGAxes, nan, nan, 28, [0.89, 0.19, 0.16], 'filled');
            hold(app.ECGAxes, 'off');

            app.RespAxes = uiaxes(mainGrid);
            app.RespAxes.Layout.Row = 3;
            app.RespAxes.Layout.Column = 1;
            title(app.RespAxes, '呼吸信号（BIDMC 01）');
            xlabel(app.RespAxes, '时间 / s');
            ylabel(app.RespAxes, '归一化幅值');
            grid(app.RespAxes, 'on');
            app.RespAxes.Box = 'on';
            hold(app.RespAxes, 'on');
            app.RespLine = plot(app.RespAxes, nan, nan, 'LineWidth', 1.2, 'Color', [0.08, 0.55, 0.25]);
            app.RespPeakScatter = scatter(app.RespAxes, nan, nan, 26, [0.90, 0.63, 0.07], 'filled');
            hold(app.RespAxes, 'off');

            app.TempAxes = uiaxes(mainGrid);
            app.TempAxes.Layout.Row = 4;
            app.TempAxes.Layout.Column = 1;
            title(app.TempAxes, '体温通道（demo / serial）');
            xlabel(app.TempAxes, '时间 / s');
            ylabel(app.TempAxes, '温度 / °C');
            grid(app.TempAxes, 'on');
            app.TempAxes.Box = 'on';
            hold(app.TempAxes, 'on');
            app.TempLine = plot(app.TempAxes, nan, nan, 'LineWidth', 1.6, 'Color', [0.82, 0.24, 0.11]);
            yline(app.TempAxes, 37.3, '--', '高温阈值', 'Color', [0.70, 0.10, 0.10]);
            yline(app.TempAxes, 36.0, '--', '低温阈值', 'Color', [0.10, 0.40, 0.70]);
            hold(app.TempAxes, 'off');

            sidePanel = uipanel(mainGrid, ...
                'Title', '参数与分析', ...
                'BackgroundColor', 'white');
            sidePanel.Layout.Row = [2, 4];
            sidePanel.Layout.Column = 2;

            sideGrid = uigridlayout(sidePanel, [9, 1]);
            sideGrid.RowHeight = {58, 58, 86, 86, 86, 120, 150, '1x', 140};
            sideGrid.Padding = [10, 10, 10, 10];

            app.DataStatusLabel = uilabel(sideGrid, ...
                'Text', '数据状态: 尚未抽取公开数据', ...
                'FontWeight', 'bold', ...
                'BackgroundColor', 'white', ...
                'WordWrap', 'on');
            app.DataStatusLabel.Layout.Row = 1;

            app.TempStatusLabel = uilabel(sideGrid, ...
                'Text', '体温状态: demo 模式待命', ...
                'BackgroundColor', 'white', ...
                'WordWrap', 'on');
            app.TempStatusLabel.Layout.Row = 2;

            app.HRValueLabel = localMetricLabel(sideGrid, '心率 HR', '-- bpm', 3);
            app.RRValueLabel = localMetricLabel(sideGrid, '呼吸率 RR', '-- bpm', 4);
            app.TempValueLabel = localMetricLabel(sideGrid, '体温 Temp', '-- °C', 5);

            app.AlertArea = uitextarea(sideGrid, ...
                'Value', {'当前无报警'}, ...
                'Editable', 'off', ...
                'FontName', 'Consolas');
            app.AlertArea.Layout.Row = 6;

            app.AnalysisArea = uitextarea(sideGrid, ...
                'Value', {'算法分析将在开始监护后更新'}, ...
                'Editable', 'off', ...
                'FontName', 'Consolas');
            app.AnalysisArea.Layout.Row = 7;

            app.LogArea = uitextarea(sideGrid, ...
                'Value', app.LogLines, ...
                'Editable', 'off', ...
                'FontName', 'Consolas');
            app.LogArea.Layout.Row = [8, 9];

            app.UIFigure.Visible = 'on';
            drawnow limitrate;
        end

        function prepareData(app, showReady)
            if nargin < 2
                showReady = false;
            end
            app.IsBusy = true;
            app.DownloadButton.Enable = 'off';
            app.StartButton.Enable = 'off';
            app.ModeDropDown.Enable = 'off';
            app.LogArea.Value = app.LogLines;
            drawnow;
            % Warm up TTS now so it's ready by the time data loads
            app.initTtsSpeaker();
            progress = uiprogressdlg(app.UIFigure, ...
                'Title', '准备公开数据', ...
                'Message', '正在检查本地数据与缓存...', ...
                'Indeterminate', 'off', ...
                'Value', 0.05);

            try
                app.CurrentPlan = bioio.getRandomDatasetPlan(string(app.ModeDropDown.Value), app.ProjectRoot);
                progress.Message = '正在检查本地文件...';
                progress.Value = 0.12;
                drawnow;
                bundle = bioio.loadPreparedMonitoringData(app.ProjectRoot, app.CurrentPlan);
                app.DataManifest = bundle.manifest;

                if app.DataManifest.downloadCount > 0
                    progress.Message = sprintf('已下载 %d 个缺失文件，正在载入算法结果...', app.DataManifest.downloadCount);
                elseif bundle.ecgCacheHit && bundle.respCacheHit
                    progress.Message = '已命中本地缓存，无需重新下载和重算。';
                else
                    progress.Message = '已检测到本地数据，正在首次生成缓存...';
                end
                progress.Value = 0.55;
                drawnow;
                app.ECG = bundle.ecg;
                app.Resp = bundle.resp;

                progress.Message = '更新界面预览...';
                progress.Value = 0.95;
                drawnow;
                app.renderStaticPreview();

                app.DataStatusLabel.Text = sprintf( ...
                    '数据状态: ECG=%s/%s, Resp=%s/%dHz, 模式=%s, 下载=%d', ...
                    app.ECG.recordName, app.ECG.leadName, ...
                    app.Resp.recordId, app.Resp.fs, app.CurrentPlan.mode, app.DataManifest.downloadCount);
                app.logLine("已随机抽取 ECG=" + app.CurrentPlan.ecgRecord + ...
                    ", Resp=" + app.CurrentPlan.respRecord + ...
                    ", 模式=" + app.CurrentPlan.mode + ...
                    ", 下载文件数=" + string(app.DataManifest.downloadCount) + ...
                    ", ECG缓存=" + string(bundle.ecgCacheHit) + ...
                    ", Resp缓存=" + string(bundle.respCacheHit));
                % Update axes titles to reflect the actual selected records
                title(app.ECGAxes, sprintf('心电信号（MIT-BIH %s）', app.CurrentPlan.ecgRecord));
                title(app.RespAxes, sprintf('呼吸信号（BIDMC %s）', app.CurrentPlan.respRecord));

                progress.Value = 1.0;
                close(progress);
                % Show ready indicator only on direct button click
                if showReady
                    app.DataStatusLabel.Text = sprintf( ...
                        '✅ 数据准备就绪 | ECG=%s/%s, Resp=%s/%dHz, 模式=%s', ...
                        app.ECG.recordName, app.ECG.leadName, ...
                        app.Resp.recordId, app.Resp.fs, app.CurrentPlan.mode);
                    app.DataStatusLabel.FontColor = [0.10, 0.52, 0.20];
                    app.logLine("数据准备就绪，可以开始监护。");
                    % Voice announcement — TTS already warmed up
                    if ~isempty(app.TtsSpeaker)
                        try
                            app.TtsSpeaker.SpeakAsyncCancelAll();
                        catch
                        end
                        app.TtsSpeaker.SpeakAsync('数据准备就绪，可以开始监护');
                    end
                end
            catch ME
                close(progress);
                app.logLine("准备数据失败: " + string(ME.message));
                uialert(app.UIFigure, ME.message, '准备数据失败');
            end
            app.IsBusy = false;
            app.DownloadButton.Enable = 'on';
            app.StartButton.Enable = 'on';
            app.ModeDropDown.Enable = 'on';
        end

        function startMonitoring(app)
            if app.IsRunning || app.IsBusy
                return;
            end
            app.IsBusy = true;
            app.StartButton.Enable = 'off';
            drawnow;

            if ~isfield(app.ECG, 'filtered') || ~isfield(app.Resp, 'enhanced')
                app.prepareData();
                % Re-acquire lock after prepareData released it
                app.IsBusy = true;
                app.StartButton.Enable = 'off';
                if ~isfield(app.ECG, 'filtered') || ~isfield(app.Resp, 'enhanced')
                    app.IsBusy = false;
                    app.StartButton.Enable = 'on';
                    return;
                end
            end

            app.SessionStart = datetime('now');
            app.ECGCursor = app.chooseRandomCursor(numel(app.ECG.filtered), app.ECG.fs, 12);
            app.RespCursor = app.chooseRandomCursor(numel(app.Resp.enhanced), app.Resp.fs, 25);
            app.TempTimes = zeros(0, 1);
            app.TempValues = zeros(0, 1);
            app.LastAlarmState = "";
            app.LastPlotRefreshTime = -inf;
            app.LastMetricRefreshTime = -inf;
            app.LastAnalysisRefreshTime = -inf;
            app.LastTempReadTime = -inf;
            app.CurrentTemp = NaN;
            app.CurrentTempMeta = struct('mode', 'demo', 'status', '待采样', 'rawText', '');
            app.LastAlarmSoundTime = -inf;
            app.AlarmPausedUntil = -inf;

            if ~isempty(app.TempStream)
                try
                    delete(app.TempStream);
                catch
                end
            end

            streamSettings = struct( ...
                'port', string(app.PortField.Value), ...
                'baudRate', app.BaudRateField.Value);
            app.TempStream = tempsrc.TemperatureStream(string(app.TempModeDropDown.Value), streamSettings);
            app.TempStatusLabel.Text = "体温状态: " + app.TempStream.lastStatus;

            start(app.TimerObj);
            app.IsRunning = true;
            app.RunningLamp.Color = [0.17, 0.70, 0.25];
            % Force immediate display so data appears without timer delay
            app.ECGCursor = app.advanceCursor(app.ECGCursor, ...
                max(1, round(app.ECG.fs * app.TimerObj.Period)), numel(app.ECG.filtered), 'ECG');
            app.RespCursor = app.advanceCursor(app.RespCursor, ...
                max(1, round(app.Resp.fs * app.TimerObj.Period)), numel(app.Resp.enhanced), 'Resp');
            app.refreshPlots();
            drawnow limitrate;
            app.logLine("监护开始：本次 ECG=" + app.CurrentPlan.ecgRecord + ...
                ", Resp=" + app.CurrentPlan.respRecord + "。");
            app.IsBusy = false;
            app.StartButton.Enable = 'on';
        end

        function stopMonitoring(app)
            if ~isempty(app.TimerObj)
                try
                    stop(app.TimerObj);
                catch
                end
            end
            app.IsRunning = false;
            % Cancel any ongoing voice alarm
            try
                if ~isempty(app.TtsSpeaker)
                    app.TtsSpeaker.SpeakAsyncCancelAll();
                end
            catch
            end
            app.LastAlarmSoundTime = -inf;
            if ~isempty(app.RunningLamp) && isvalid(app.RunningLamp)
                app.RunningLamp.Color = [0.55, 0.55, 0.55];
            end
        end

        function saveSession(app)
            if isempty(app.TempValues)
                app.logLine('当前没有可保存的会话数据。');
                return;
            end

            outputFolder = fullfile(app.ProjectRoot, 'output', 'sessions');
            if ~isfolder(outputFolder)
                mkdir(outputFolder);
            end

            stamp = char(datetime('now', 'Format', 'yyyyMMdd_HHmmss'));
            matFile = fullfile(outputFolder, ['session_', stamp, '.mat']);
            tempCsv = fullfile(outputFolder, ['session_', stamp, '_temperature.csv']);
            hrCsv = fullfile(outputFolder, ['session_', stamp, '_heart_rate.csv']);
            rrCsv = fullfile(outputFolder, ['session_', stamp, '_resp_rate.csv']);

            session = struct();
            session.savedAt = datetime('now');
            session.ecg = app.ECG;
            session.resp = app.Resp;
            session.tempTimes = app.TempTimes;
            session.tempValues = app.TempValues;
            session.settings = struct( ...
                'tempMode', app.TempModeDropDown.Value, ...
                'measurementMode', app.MeasurementDropDown.Value, ...
                'port', app.PortField.Value, ...
                'baudRate', app.BaudRateField.Value);
            save(matFile, '-struct', 'session');

            writetable(table(app.TempTimes, app.TempValues, ...
                'VariableNames', {'time_s', 'temperature_c'}), tempCsv);
            writetable(table(app.ECG.heartRateTimes, app.ECG.heartRate, ...
                'VariableNames', {'time_s', 'heart_rate_bpm'}), hrCsv);
            writetable(table(app.Resp.respRateTimes, app.Resp.respRate, ...
                'VariableNames', {'time_s', 'resp_rate_bpm'}), rrCsv);

            app.logLine("会话已保存到: " + string(matFile));
        end

        function exportAnalysis(app)
            if ~isfield(app.ECG, 'filtered') || ~isfield(app.Resp, 'enhanced')
                app.prepareData();
                if ~isfield(app.ECG, 'filtered') || ~isfield(app.Resp, 'enhanced')
                    return;
                end
            end

            try
                bundle = struct();
                bundle.ecg = app.ECG;
                bundle.resp = app.Resp;
                bundle.manifest = app.DataManifest;

                report = bioout.exportAnalysisReport(app.ProjectRoot, bundle, app.CurrentPlan);
                app.logLine("分析图与数据已导出到: " + string(report.outputFolder));
                uialert(app.UIFigure, ...
                    sprintf('分析图和数据已导出到:\n%s', report.outputFolder), ...
                    '导出完成');
            catch ME
                app.logLine("导出分析失败: " + string(ME.message));
                uialert(app.UIFigure, ME.message, '导出失败');
            end
        end

        function updatePortList(app)
            try
                ports = string(serialportlist("available"));
            catch
                ports = strings(0, 1);
            end

            if isempty(ports)
                app.PortsHintLabel.Text = '可用串口: 当前未检测到';
                app.logLine('当前未检测到可用串口，体温通道可先使用 demo 模式。');
            else
                app.PortsHintLabel.Text = "可用串口: " + strjoin(ports, ', ');
                if strlength(string(app.PortField.Value)) == 0
                    app.PortField.Value = char(ports(1));
                end
                app.logLine("已检测到串口: " + strjoin(ports, ', '));
            end
        end

        function onTimerTick(app)
            try
                if ~app.IsRunning
                    return;
                end

                ecgStep = max(1, round(app.ECG.fs * app.TimerObj.Period));
                respStep = max(1, round(app.Resp.fs * app.TimerObj.Period));
                app.ECGCursor = app.advanceCursor(app.ECGCursor, ecgStep, numel(app.ECG.filtered), 'ECG');
                app.RespCursor = app.advanceCursor(app.RespCursor, respStep, numel(app.Resp.enhanced), 'Resp');

                elapsedSeconds = seconds(datetime('now') - app.SessionStart);
                uiTouched = false;

                if isnan(app.CurrentTemp) || ...
                        (elapsedSeconds - app.LastTempReadTime) >= app.TempReadPeriod
                    [app.CurrentTemp, app.CurrentTempMeta] = app.TempStream.next(string(app.MeasurementDropDown.Value));
                    app.TempTimes(end + 1, 1) = elapsedSeconds;
                    app.TempValues(end + 1, 1) = app.CurrentTemp;
                    app.LastTempReadTime = elapsedSeconds;
                    % Trim history to prevent unbounded memory growth
                    maxTempHistory = round(300 / app.TempReadPeriod);
                    if numel(app.TempTimes) > maxTempHistory
                        app.TempTimes = app.TempTimes(end - maxTempHistory + 1:end);
                        app.TempValues = app.TempValues(end - maxTempHistory + 1:end);
                    end
                end

                if (elapsedSeconds - app.LastPlotRefreshTime) >= app.PlotRefreshPeriod
                    app.refreshPlots();
                    app.LastPlotRefreshTime = elapsedSeconds;
                    uiTouched = true;
                end

                if (elapsedSeconds - app.LastMetricRefreshTime) >= app.MetricRefreshPeriod
                    updateAnalysis = (elapsedSeconds - app.LastAnalysisRefreshTime) >= app.AnalysisRefreshPeriod;
                    app.refreshMetricsAndAnalysis(elapsedSeconds, app.CurrentTemp, app.CurrentTempMeta, updateAnalysis);
                    app.LastMetricRefreshTime = elapsedSeconds;
                    if updateAnalysis
                        app.LastAnalysisRefreshTime = elapsedSeconds;
                    end
                    uiTouched = true;
                end

                if uiTouched
                    drawnow limitrate;
                end
            catch ME
                % Log transient errors but keep monitoring alive.
                % Only stop on fatal internal errors.
                app.logLine("警告: 定时器瞬时错误: " + string(ME.message));
                if contains(ME.identifier, 'MATLAB:class:InvalidProperty') || ...
                   contains(ME.identifier, 'MATLAB:undefinedVarOrClass')
                    app.stopMonitoring();
                    app.logLine("运行时错误（已停止）: " + string(ME.message));
                    uialert(app.UIFigure, ME.message, '监护已停止');
                end
            end
        end

        function refreshPlots(app)
            ecgWindowSamples = round(12 * app.ECG.fs);
            ecgStart = max(1, app.ECGCursor - ecgWindowSamples + 1);
            ecgIdx = ecgStart:app.ECGCursor;
            ecgDisplayIdx = localThinIndexVector(ecgIdx, app.MaxPlotPoints);
            set(app.ECGLine, ...
                'XData', app.ECG.t(ecgDisplayIdx), ...
                'YData', app.ECG.filtered(ecgDisplayIdx));
            ecgPeakMask = app.ECG.rLocs >= ecgStart & app.ECG.rLocs <= app.ECGCursor;
            set(app.ECGPeakScatter, ...
                'XData', app.ECG.t(app.ECG.rLocs(ecgPeakMask)), ...
                'YData', app.ECG.filtered(app.ECG.rLocs(ecgPeakMask)));
            xlim(app.ECGAxes, [app.ECG.t(ecgIdx(1)), app.ECG.t(ecgIdx(end)) + eps]);

            respWindowSamples = round(25 * app.Resp.fs);
            respStart = max(1, app.RespCursor - respWindowSamples + 1);
            respIdx = respStart:app.RespCursor;
            respDisplayIdx = localThinIndexVector(respIdx, app.MaxPlotPoints);
            set(app.RespLine, ...
                'XData', app.Resp.t(respDisplayIdx), ...
                'YData', app.Resp.enhanced(respDisplayIdx));
            respPeakMask = app.Resp.peakLocs >= respStart & app.Resp.peakLocs <= app.RespCursor;
            set(app.RespPeakScatter, ...
                'XData', app.Resp.t(app.Resp.peakLocs(respPeakMask)), ...
                'YData', app.Resp.enhanced(app.Resp.peakLocs(respPeakMask)));
            xlim(app.RespAxes, [app.Resp.t(respIdx(1)), app.Resp.t(respIdx(end)) + eps]);

            if isempty(app.TempTimes)
                set(app.TempLine, 'XData', nan, 'YData', nan);
            else
                % Display recent 60 s of raw temperature values.
                % Heavy filtering/smoothing is offloaded to TemperatureStream
                % so the plot refresh stays lightweight.
                tempWindowStart = max(0, app.TempTimes(end) - 60);
                tempStartIdx = find(app.TempTimes >= tempWindowStart, 1, 'first');
                if isempty(tempStartIdx)
                    tempStartIdx = 1;
                end
                tempIdx = tempStartIdx:numel(app.TempTimes);
                % Thin to MaxPlotPoints for render speed
                if numel(tempIdx) > app.MaxPlotPoints
                    stride = ceil(numel(tempIdx) / app.MaxPlotPoints);
                    tempIdx = tempIdx(1:stride:end);
                end
                set(app.TempLine, ...
                    'XData', app.TempTimes(tempIdx), ...
                    'YData', app.TempValues(tempIdx));
                xlim(app.TempAxes, [max(0, app.TempTimes(end) - 60), max(60, app.TempTimes(end) + eps)]);
            end
        end

        function refreshMetricsAndAnalysis(app, elapsedSeconds, currentTemp, tempMeta, updateAnalysis)
            if nargin < 5
                updateAnalysis = true;
            end

            currentHr = app.lookupRate(app.ECG.heartRateTimes, app.ECG.heartRate, app.ECG.t(app.ECGCursor), 15);
            currentRr = app.lookupRate(app.Resp.respRateTimes, app.Resp.respRate, app.Resp.t(app.RespCursor), 20);
            [ecgIrregular, ecgIrregularText] = app.detectEcgIrregularity();
            [respIrregular, respIrregularText] = app.detectRespIrregularity();

            app.updateMetricLabel(app.HRValueLabel, '心率 HR', currentHr, 'bpm', [60, 100]);
            app.updateMetricLabel(app.RRValueLabel, '呼吸率 RR', currentRr, 'bpm', [12, 20]);
            app.updateMetricLabel(app.TempValueLabel, '体温 Temp', currentTemp, '°C', [36.0, 37.3]);

            app.TempStatusLabel.Text = "体温状态: " + string(tempMeta.status);

            alarmLines = app.buildAlarmLines(currentHr, currentRr, currentTemp, ...
                ecgIrregular, ecgIrregularText, respIrregular, respIrregularText);

            % Pre-build TTS message before UI update so voice fires
            % with minimal lag behind the red text.
            alarmMsg = app.buildAlarmMessage(alarmLines);
            hasAlarm = ~isempty(alarmLines) && ~strcmp(alarmLines{1}, '当前无报警');

            app.AlertArea.Value = alarmLines;
            currentAlarmStr = strjoin(string(alarmLines), '|');

            % Sound alarm: fire immediately on alarm transition,
            % then apply priority-graded cooldown for repeated alarms.
            if hasAlarm && elapsedSeconds >= app.AlarmPausedUntil
                alarmPriority = app.classifyAlarmPriority(alarmLines);
                cooldown = app.AlarmSoundCooldown.(alarmPriority);
                % Fire immediately if alarm state just changed (transition),
                % otherwise respect cooldown period.
                isNewAlarm = ~strcmp(currentAlarmStr, app.LastAlarmState);
                if isNewAlarm || (elapsedSeconds - app.LastAlarmSoundTime) >= cooldown
                    app.playAlarmSound(alarmMsg);
                    app.LastAlarmSoundTime = elapsedSeconds;
                end
            end

            % Log alarm events on transition to alarming state
            if hasAlarm && ~strcmp(currentAlarmStr, app.LastAlarmState)
                app.logAlarmEvent(alarmLines);
            end
            app.LastAlarmState = currentAlarmStr;

            if updateAnalysis
                analysisLines = app.buildAnalysisLines(elapsedSeconds, currentHr, currentRr, ...
                    ecgIrregularText, respIrregularText);
                app.AnalysisArea.Value = analysisLines;
            end
        end

        function renderStaticPreview(app)
            previewEcgCount = min(numel(app.ECG.filtered), round(8 * app.ECG.fs));
            previewRespCount = min(numel(app.Resp.enhanced), round(12 * app.Resp.fs));
            ecgEnd = app.chooseRandomCursor(numel(app.ECG.filtered), app.ECG.fs, 8);
            ecgStart = max(1, ecgEnd - previewEcgCount + 1);
            ecgIdx = ecgStart:ecgEnd;

            set(app.ECGLine, ...
                'XData', app.ECG.t(ecgIdx), ...
                'YData', app.ECG.filtered(ecgIdx));
            previewEcgPeaks = app.ECG.rLocs(app.ECG.rLocs >= ecgStart & app.ECG.rLocs <= ecgEnd);
            set(app.ECGPeakScatter, ...
                'XData', app.ECG.t(previewEcgPeaks), ...
                'YData', app.ECG.filtered(previewEcgPeaks));

            respEnd = app.chooseRandomCursor(numel(app.Resp.enhanced), app.Resp.fs, 12);
            respStart = max(1, respEnd - previewRespCount + 1);
            respIdx = respStart:respEnd;
            set(app.RespLine, ...
                'XData', app.Resp.t(respIdx), ...
                'YData', app.Resp.enhanced(respIdx));
            previewRespPeaks = app.Resp.peakLocs(app.Resp.peakLocs >= respStart & app.Resp.peakLocs <= respEnd);
            set(app.RespPeakScatter, ...
                'XData', app.Resp.t(previewRespPeaks), ...
                'YData', app.Resp.enhanced(previewRespPeaks));
        end

        function cursor = advanceCursor(app, cursor, step, totalCount, label)
            cursor = cursor + step;
            if cursor > totalCount
                cursor = 1;
                app.logLine(label + " 数据已循环回到起点。");
            end
        end

        function value = lookupRate(~, timeAxis, rateAxis, currentTime, lookbackWindow)
            if isempty(rateAxis)
                value = NaN;
                return;
            end

            mask = timeAxis <= currentTime & timeAxis >= (currentTime - lookbackWindow);
            if any(mask)
                value = median(rateAxis(mask), 'omitnan');
            else
                earlierMask = timeAxis <= currentTime;
                if any(earlierMask)
                    value = rateAxis(find(earlierMask, 1, 'last'));
                else
                    value = NaN;
                end
            end
        end

        function updateMetricLabel(~, labelHandle, titleText, value, unitText, normalRange)
            if isnan(value)
                labelHandle.Text = sprintf('%s\n-- %s', titleText, unitText);
                labelHandle.FontColor = [0.35, 0.35, 0.35];
                return;
            end

            labelHandle.Text = sprintf('%s\n%.1f %s', titleText, value, unitText);
            if value < normalRange(1) || value > normalRange(2)
                labelHandle.FontColor = [0.82, 0.18, 0.15];
            else
                labelHandle.FontColor = [0.10, 0.52, 0.20];
            end
        end

        function alarmLines = buildAlarmLines(~, hr, rr, temp, ecgIrregular, ecgText, respIrregular, respText)
            alarmLines = {};

            if ~isnan(hr) && (hr < 60 || hr > 100)
                alarmLines{end + 1} = sprintf('心率报警: %.1f bpm', hr);
            end
            if ~isnan(rr) && (rr < 12 || rr > 20)
                alarmLines{end + 1} = sprintf('呼吸报警: %.1f bpm', rr);
            end
            if ~isnan(temp) && (temp < 36.0 || temp > 37.3)
                alarmLines{end + 1} = sprintf('体温报警: %.1f °C', temp);
            end
            if ecgIrregular
                alarmLines{end + 1} = sprintf('心电异常提示: %s', ecgText);
            end
            if respIrregular
                alarmLines{end + 1} = sprintf('呼吸异常提示: %s', respText);
            end

            if isempty(alarmLines)
                alarmLines = {'当前无报警'};
            else
                alarmLines = [{'当前报警:'}, alarmLines];
            end
        end

        function priority = classifyAlarmPriority(~, alarmLines)
            % Classify the highest alarm priority in the current alarm set.
            % Returns 'crisis', 'warning', or 'advisory'.
            lines = strjoin(string(alarmLines), '|');
            priority = 'advisory';  % default: irregularity hints only
            if contains(lines, '心率报警') || contains(lines, '呼吸报警') || contains(lines, '体温报警')
                priority = 'warning';
            end
            % Crisis: extreme values (HR < 40 or > 150, Temp > 39.5, RR < 6 or > 36)
            for i = 1:numel(alarmLines)
                line = char(alarmLines{i});
                if contains(line, '心率报警')
                    val = sscanf(line, '心率报警: %f');
                    if ~isempty(val) && (val(1) < 40 || val(1) > 150)
                        priority = 'crisis';
                    end
                elseif contains(line, '体温报警')
                    val = sscanf(line, '体温报警: %f');
                    if ~isempty(val) && val(1) > 39.5
                        priority = 'crisis';
                    end
                elseif contains(line, '呼吸报警')
                    val = sscanf(line, '呼吸报警: %f');
                    if ~isempty(val) && (val(1) < 6 || val(1) > 36)
                        priority = 'crisis';
                    end
                end
            end
        end

        function pauseAlarm(app, duration)
            % Pause audible alarms for `duration` seconds (default 30).
            if nargin < 2
                duration = 30;
            end
            app.AlarmPausedUntil = max(app.AlarmPausedUntil, ...
                seconds(datetime('now') - app.SessionStart) + duration);
            app.logLine(sprintf('报警已暂停 %d 秒。', duration));
        end

        function resumeAlarm(app)
            app.AlarmPausedUntil = -inf;
            app.logLine('报警已恢复。');
        end

        function analysisLines = buildAnalysisLines(app, elapsedSeconds, hr, rr, ecgText, respText)
            analysisLines = {};
            analysisLines{end + 1} = sprintf('随机模式: %s', app.CurrentPlan.mode);
            analysisLines{end + 1} = sprintf('当前 ECG 记录: %s', app.CurrentPlan.ecgRecord);
            analysisLines{end + 1} = sprintf('当前 Resp 记录: %s', app.CurrentPlan.respRecord);
            analysisLines{end + 1} = sprintf('ECG SNR: %.2f dB', app.ECG.snrDb);
            analysisLines{end + 1} = sprintf('Resp SNR: %.2f dB', app.Resp.snrDb);
            analysisLines{end + 1} = sprintf('累计R波: %d', sum(app.ECG.rLocs <= app.ECGCursor));
            analysisLines{end + 1} = sprintf('累计呼吸峰: %d', sum(app.Resp.peakLocs <= app.RespCursor));
            analysisLines{end + 1} = sprintf('心律状态: %s', ecgText);
            analysisLines{end + 1} = sprintf('呼吸节律状态: %s', respText);

            [corrValue, corrText] = app.estimateFusionCorrelation();
            if isnan(corrValue)
                analysisLines{end + 1} = '心呼相关: 数据不足';
            else
                analysisLines{end + 1} = sprintf('心呼相关: %.2f (%s)', corrValue, corrText);
            end

            analysisLines{end + 1} = sprintf('体温趋势: %s', app.estimateTemperatureTrend());

            if ~isnan(hr) && ~isnan(rr)
                analysisLines{end + 1} = sprintf('当前 HR/RR 比值: %.2f', hr / max(rr, eps));
            end

            analysisLines{end + 1} = sprintf('会话时长: %.1f s', elapsedSeconds);
        end

        function playAlarmSound(app, alarmMsg)
            % Play alarm voice using Windows TTS (async, non-blocking).
            % alarmMsg is a pre-built Chinese string from buildAlarmMessage.
            try
                if isempty(alarmMsg)
                    return;  % Only 心电异常提示 → no sound
                end
                if app.initTtsSpeaker()
                    % SpeakAsync is non-blocking; cooldown prevents overlap
                    app.TtsSpeaker.SpeakAsync(alarmMsg);
                    return;
                end
                % Fallback to tone beeping if TTS unavailable
                app.playAlarmTone(alarmMsg);
            catch
                beep;
            end
        end

        function ok = initTtsSpeaker(app)
            ok = false;
            try
                if ~isempty(app.TtsSpeaker)
                    ok = true;
                    return;
                end
                NET.addAssembly('System.Speech');
                app.TtsSpeaker = System.Speech.Synthesis.SpeechSynthesizer();
                app.TtsSpeaker.Volume = 100;
                app.TtsSpeaker.Rate = 0;
                % Warm up the TTS engine in background to eliminate
                % first-SpeakAsync latency when a real alarm fires.
                app.TtsSpeaker.SpeakAsync('就绪');
                ok = true;
            catch
            end
        end

        function msg = buildAlarmMessage(~, alarmLines)
            lines = string(alarmLines);
            msg = "";
            for i = 1:numel(lines)
                line = char(lines(i));
                if contains(line, '心率报警')
                    msg = msg + "心率异常、";
                elseif contains(line, '呼吸报警')
                    msg = msg + "呼吸异常、";
                elseif contains(line, '体温报警')
                    msg = msg + "体温异常、";
                end
            end
            msg = char(msg);
            if ~isempty(msg)
                msg = msg(1:end-1);
            end
        end

        function playAlarmTone(~, alarmMsg)
            % Tone-based alarm differentiated by type.
            % alarmMsg is the pre-built Chinese alarm message string.
            hasHR = contains(alarmMsg, '心率异常');
            hasRR = contains(alarmMsg, '呼吸异常');
            hasTemp = contains(alarmMsg, '体温异常');

            fs = 8192;
            beepSignal = [];

            if hasHR
                t = 0:(1/fs):0.12;
                beepSignal = [beepSignal, sin(2*pi*1040*t) * 0.5, zeros(1, round(0.06*fs))];
                beepSignal = [beepSignal, sin(2*pi*1040*t) * 0.5, zeros(1, round(0.10*fs))];
            end
            if hasRR
                t = 0:(1/fs):0.18;
                beepSignal = [beepSignal, sin(2*pi*780*t) * 0.5, zeros(1, round(0.08*fs))];
                beepSignal = [beepSignal, sin(2*pi*780*t) * 0.5, zeros(1, round(0.10*fs))];
            end
            if hasTemp
                t = 0:(1/fs):0.30;
                beepSignal = [beepSignal, sin(2*pi*520*t) * 0.5, zeros(1, round(0.10*fs))];
            end
            if isempty(beepSignal)
                t = 0:(1/fs):0.25;
                beepSignal = [sin(2*pi*880*t) * 0.5, zeros(1, round(0.06*fs)), ...
                              sin(2*pi*660*t) * 0.5];
            end

            sound(beepSignal, fs);
        end

        function logAlarmEvent(app, alarmLines)
            % Log alarm events to file
            % Thesis: 报警信息记录至日志文件，内容包括报警时间、异常参数类型和异常数值
            try
                outputFolder = fullfile(app.ProjectRoot, 'output', 'alarms');
                if ~isfolder(outputFolder)
                    mkdir(outputFolder);
                end
                logFile = fullfile(outputFolder, 'alarm_log.txt');
                timestamp = char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss'));
                fid = fopen(logFile, 'a');
                if fid > 0
                    fprintf(fid, '[%s] %s\n', timestamp, strjoin(alarmLines, ' | '));
                    fclose(fid);
                end
            catch
            end
        end

        function [corrValue, textLabel] = estimateFusionCorrelation(app)
            recentWindow = 60;
            currentEcgTime = app.ECG.t(app.ECGCursor);
            currentRespTime = app.Resp.t(app.RespCursor);
            latestTime = min(currentEcgTime, currentRespTime);

            hrMask = app.ECG.heartRateTimes >= (latestTime - recentWindow) & app.ECG.heartRateTimes <= latestTime;
            rrMask = app.Resp.respRateTimes >= (latestTime - recentWindow) & app.Resp.respRateTimes <= latestTime;

            if sum(hrMask) < 3 || sum(rrMask) < 3
                corrValue = NaN;
                textLabel = '数据不足';
                return;
            end

            startTime = max(min(app.ECG.heartRateTimes(hrMask)), min(app.Resp.respRateTimes(rrMask)));
            endTime = min(max(app.ECG.heartRateTimes(hrMask)), max(app.Resp.respRateTimes(rrMask)));
            if endTime <= startTime
                corrValue = NaN;
                textLabel = '时间窗不足';
                return;
            end

            commonTime = linspace(startTime, endTime, 40).';
            hrSeries = interp1(app.ECG.heartRateTimes(hrMask), app.ECG.heartRate(hrMask), commonTime, 'linear', 'extrap');
            rrSeries = interp1(app.Resp.respRateTimes(rrMask), app.Resp.respRate(rrMask), commonTime, 'linear', 'extrap');
            corrMatrix = corrcoef(hrSeries, rrSeries);
            corrValue = corrMatrix(1, 2);

            if abs(corrValue) < 0.20
                textLabel = '弱耦合';
            elseif corrValue > 0
                textLabel = '正相关';
            else
                textLabel = '负相关';
            end
        end

        function trendText = estimateTemperatureTrend(app)
            if numel(app.TempValues) < 6
                trendText = '样本不足';
                return;
            end

            recentMask = app.TempTimes >= max(0, app.TempTimes(end) - 30) & ~isnan(app.TempValues);
            if sum(recentMask) < 6
                trendText = '样本不足';
                return;
            end

            coeffs = polyfit(app.TempTimes(recentMask), app.TempValues(recentMask), 1);
            slopePerMinute = coeffs(1) * 60;

            if slopePerMinute > 0.08
                trendText = sprintf('升温 %.3f °C/min', slopePerMinute);
            elseif slopePerMinute < -0.08
                trendText = sprintf('降温 %.3f °C/min', slopePerMinute);
            else
                trendText = '基本稳定';
            end
        end

        function logLine(app, messageText)
            timeStamp = char(datetime('now', 'Format', 'HH:mm:ss'));
            newLine = sprintf('[%s] %s', timeStamp, char(string(messageText)));
            app.LogLines = [{newLine}; app.LogLines(:)];
            if numel(app.LogLines) > 20
                app.LogLines = app.LogLines(1:20);
            end
            if ~isempty(app.LogArea) && isvalid(app.LogArea)
                app.LogArea.Value = app.LogLines;
            end
        end

        function cursor = chooseRandomCursor(~, totalCount, fs, windowSeconds)
            windowSamples = round(windowSeconds * fs);
            lowerBound = min(windowSamples, totalCount);
            upperBound = totalCount;
            if lowerBound >= upperBound
                cursor = upperBound;
            else
                cursor = randi([lowerBound, upperBound]);
            end
        end

        function [flag, textLabel] = detectEcgIrregularity(app)
            currentTime = app.ECG.t(app.ECGCursor);
            rrTimes = app.ECG.heartRateTimes;
            hr = app.ECG.heartRate;
            mask = rrTimes <= currentTime & rrTimes >= (currentTime - 25);

            if sum(mask) < 6
                flag = false;
                textLabel = '样本不足';
                return;
            end

            rrIntervals = 60 ./ hr(mask);
            cv = std(rrIntervals, 'omitnan') / max(mean(rrIntervals, 'omitnan'), eps);
            deviation = max(abs(rrIntervals - median(rrIntervals, 'omitnan')));
            flag = cv > 0.12 || deviation > 0.18;

            if flag
                textLabel = sprintf('RR变异偏大 (CV=%.2f)', cv);
            else
                textLabel = sprintf('节律较稳定 (CV=%.2f)', cv);
            end
        end

        function [flag, textLabel] = detectRespIrregularity(app)
            currentTime = app.Resp.t(app.RespCursor);
            rrTimes = app.Resp.respRateTimes;
            rr = app.Resp.respRate;
            mask = rrTimes <= currentTime & rrTimes >= (currentTime - 35);

            if sum(mask) < 4
                flag = false;
                textLabel = '样本不足';
                return;
            end

            respIntervals = 60 ./ rr(mask);
            cv = std(respIntervals, 'omitnan') / max(mean(respIntervals, 'omitnan'), eps);
            flag = cv > 0.18 || any(rr(mask) > 20) || any(rr(mask) < 12);

            if flag
                textLabel = sprintf('呼吸节律波动较大 (CV=%.2f)', cv);
            else
                textLabel = sprintf('呼吸节律较稳定 (CV=%.2f)', cv);
            end
        end
    end
end

function labelHandle = localMetricLabel(parent, titleText, valueText, rowIndex)
panel = uipanel(parent, 'BackgroundColor', [0.98, 0.99, 1.00]);
panel.Layout.Row = rowIndex;

grid = uigridlayout(panel, [2, 1]);
grid.RowHeight = {22, 46};
grid.Padding = [10, 8, 10, 8];

titleLabel = uilabel(grid, ...
    'Text', titleText, ...
    'FontWeight', 'bold', ...
    'FontSize', 13, ...
    'BackgroundColor', [0.98, 0.99, 1.00], ...
    'FontColor', [0.20, 0.20, 0.20]);
titleLabel.Layout.Row = 1;

labelHandle = uilabel(grid, ...
    'Text', valueText, ...
    'FontSize', 19, ...
    'FontWeight', 'bold', ...
    'HorizontalAlignment', 'center', ...
    'VerticalAlignment', 'center', ...
    'BackgroundColor', [0.98, 0.99, 1.00]);
labelHandle.Layout.Row = 2;
end

function position = localInitialFigurePosition()
screenSize = get(groot, 'ScreenSize');
margin = 40;
targetWidth = 1500;
targetHeight = 920;

usableWidth = max(900, screenSize(3) - 2 * margin);
usableHeight = max(640, screenSize(4) - 2 * margin);
width = min(targetWidth, usableWidth);
height = min(targetHeight, usableHeight);

xPos = screenSize(1) + max(20, (screenSize(3) - width) / 2);
yPos = screenSize(2) + max(40, (screenSize(4) - height) / 2);
position = round([xPos, yPos, width, height]);
end

function indices = localThinIndexVector(indices, maxPoints)
if numel(indices) <= maxPoints
    return;
end

pick = unique(round(linspace(1, numel(indices), maxPoints)));
indices = indices(pick);
end
