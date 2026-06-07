classdef TemperatureSensorReaderApp < handle
    %TEMPERATURESENSORREADERAPP Standalone UI for GooDeTek Type-C temperature modules.

    properties (Access = private)
        ProjectRoot
        UIFigure
        PortField
        BaudRateField
        ModeDropDown
        BodyCommandField
        ObjectCommandField
        ReadWindowField
        ConnectButton
        DisconnectButton
        ReadOnceButton
        StartButton
        StopButton
        RefreshButton
        ClearButton
        StatusLabel
        TempLabel
        RawArea
        LogArea
        Axes
        TempLine

        SerialObj = []
        TimerObj = []
        IsRunning = false
        SessionStart = datetime('now')
        TimeData = zeros(0, 1)
        TempData = zeros(0, 1)
        LogLines = {'等待连接传感器...'}
        LastLoggedStatus = ""
        LastLoggedTime = datetime('now')
    end

    methods
        function app = TemperatureSensorReaderApp(projectRoot)
            if nargin < 1 || isempty(projectRoot)
                projectRoot = pwd;
            end

            app.ProjectRoot = projectRoot;
            app.buildUi();
            app.TimerObj = timer( ...
                'ExecutionMode', 'fixedSpacing', ...
                'Period', 0.50, ...
                'BusyMode', 'drop', ...
                'TimerFcn', @(~, ~) app.onTimerTick());
            app.refreshPorts();
            app.logLine('协议: 9600 8N1, HEX单字节, 体温AB, 物温AA, 返回+000365=36.5°C。');
        end

        function show(app)
            if isempty(app.UIFigure) || ~isvalid(app.UIFigure)
                return;
            end

            try
                app.UIFigure.Visible = 'on';
            catch
            end
            try
                app.UIFigure.WindowState = 'normal';
            catch
            end
            try
                figure(app.UIFigure);
            catch
            end
            drawnow;
        end

        function delete(app)
            app.stopContinuous();
            if ~isempty(app.TimerObj)
                try
                    delete(app.TimerObj);
                catch
                end
                app.TimerObj = [];
            end
            app.disconnectSerial(false);

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
            app.UIFigure = uifigure( ...
                'Name', 'Type-C测温模块读取', ...
                'Position', localInitialPosition(), ...
                'Color', [0.97, 0.98, 1.00], ...
                'CloseRequestFcn', @(~, ~) app.delete());

            mainGrid = uigridlayout(app.UIFigure, [5, 1]);
            mainGrid.RowHeight = {110, 82, 74, '1x', 120};
            mainGrid.Padding = [14, 14, 14, 14];
            mainGrid.RowSpacing = 10;

            controlPanel = uipanel(mainGrid, ...
                'Title', '串口与命令', ...
                'BackgroundColor', 'white');
            controlPanel.Layout.Row = 1;

            controlGrid = uigridlayout(controlPanel, [2, 8]);
            controlGrid.RowHeight = {30, 30};
            controlGrid.ColumnWidth = {64, 90, 64, 96, 72, 88, 72, '1x'};
            controlGrid.Padding = [10, 6, 10, 6];
            controlGrid.ColumnSpacing = 8;

            label = uilabel(controlGrid, 'Text', '端口', 'HorizontalAlignment', 'right', 'BackgroundColor', 'white');
            label.Layout.Row = 1;
            label.Layout.Column = 1;
            app.PortField = uieditfield(controlGrid, 'text', 'Value', 'COM7');
            app.PortField.Layout.Row = 1;
            app.PortField.Layout.Column = 2;

            label = uilabel(controlGrid, 'Text', '波特率', 'HorizontalAlignment', 'right', 'BackgroundColor', 'white');
            label.Layout.Row = 1;
            label.Layout.Column = 3;
            app.BaudRateField = uieditfield(controlGrid, 'numeric', ...
                'Value', 9600, ...
                'Limits', [1200, 921600], ...
                'RoundFractionalValues', 'on');
            app.BaudRateField.Layout.Row = 1;
            app.BaudRateField.Layout.Column = 4;

            label = uilabel(controlGrid, 'Text', '模式', 'HorizontalAlignment', 'right', 'BackgroundColor', 'white');
            label.Layout.Row = 1;
            label.Layout.Column = 5;
            app.ModeDropDown = uidropdown(controlGrid, ...
                'Items', {'body', 'object'}, ...
                'Value', 'body');
            app.ModeDropDown.Layout.Row = 1;
            app.ModeDropDown.Layout.Column = 6;

            app.RefreshButton = uibutton(controlGrid, ...
                'Text', '刷新串口', ...
                'ButtonPushedFcn', @(~, ~) app.refreshPorts());
            app.RefreshButton.Layout.Row = 1;
            app.RefreshButton.Layout.Column = 7;

            app.StatusLabel = uilabel(controlGrid, ...
                'Text', '状态: 未连接', ...
                'BackgroundColor', 'white', ...
                'WordWrap', 'on');
            app.StatusLabel.Layout.Row = 1;
            app.StatusLabel.Layout.Column = 8;

            label = uilabel(controlGrid, 'Text', '体温HEX', 'HorizontalAlignment', 'right', 'BackgroundColor', 'white');
            label.Layout.Row = 2;
            label.Layout.Column = 1;
            app.BodyCommandField = uieditfield(controlGrid, 'text', 'Value', 'AB');
            app.BodyCommandField.Layout.Row = 2;
            app.BodyCommandField.Layout.Column = 2;

            label = uilabel(controlGrid, 'Text', '物温HEX', 'HorizontalAlignment', 'right', 'BackgroundColor', 'white');
            label.Layout.Row = 2;
            label.Layout.Column = 3;
            app.ObjectCommandField = uieditfield(controlGrid, 'text', 'Value', 'AA');
            app.ObjectCommandField.Layout.Row = 2;
            app.ObjectCommandField.Layout.Column = 4;

            label = uilabel(controlGrid, 'Text', '等待s', 'HorizontalAlignment', 'right', 'BackgroundColor', 'white');
            label.Layout.Row = 2;
            label.Layout.Column = 5;
            app.ReadWindowField = uieditfield(controlGrid, 'numeric', ...
                'Value', 0.50, ...
                'Limits', [0.05, 5.00]);
            app.ReadWindowField.Layout.Row = 2;
            app.ReadWindowField.Layout.Column = 6;

            app.ClearButton = uibutton(controlGrid, ...
                'Text', '清空', ...
                'ButtonPushedFcn', @(~, ~) app.clearData());
            app.ClearButton.Layout.Row = 2;
            app.ClearButton.Layout.Column = 7;

            protocolLabel = uilabel(controlGrid, ...
                'Text', '默认: 9600,8,N,1；体温0xAB，物温0xAA；ASCII返回如+000365。', ...
                'BackgroundColor', 'white', ...
                'FontAngle', 'italic');
            protocolLabel.Layout.Row = 2;
            protocolLabel.Layout.Column = 8;

            buttonPanel = uipanel(mainGrid, 'BackgroundColor', 'white');
            buttonPanel.Layout.Row = 2;
            buttonGrid = uigridlayout(buttonPanel, [1, 5]);
            buttonGrid.ColumnWidth = {'1x', '1x', '1x', '1x', '1x'};
            buttonGrid.Padding = [10, 12, 10, 12];
            buttonGrid.ColumnSpacing = 10;

            app.ConnectButton = uibutton(buttonGrid, ...
                'Text', '连接', ...
                'ButtonPushedFcn', @(~, ~) app.connectSerial());
            app.DisconnectButton = uibutton(buttonGrid, ...
                'Text', '断开', ...
                'ButtonPushedFcn', @(~, ~) app.disconnectSerial(true));
            app.ReadOnceButton = uibutton(buttonGrid, ...
                'Text', '读取一次', ...
                'ButtonPushedFcn', @(~, ~) app.readOnce());
            app.StartButton = uibutton(buttonGrid, ...
                'Text', '连续读取', ...
                'ButtonPushedFcn', @(~, ~) app.startContinuous());
            app.StopButton = uibutton(buttonGrid, ...
                'Text', '停止', ...
                'ButtonPushedFcn', @(~, ~) app.stopContinuous());

            readoutPanel = uipanel(mainGrid, 'BackgroundColor', [0.98, 0.99, 1.00]);
            readoutPanel.Layout.Row = 3;
            readoutGrid = uigridlayout(readoutPanel, [1, 2]);
            readoutGrid.ColumnWidth = {240, '1x'};
            readoutGrid.Padding = [12, 8, 12, 8];

            app.TempLabel = uilabel(readoutGrid, ...
                'Text', '-- °C', ...
                'FontSize', 34, ...
                'FontWeight', 'bold', ...
                'HorizontalAlignment', 'center', ...
                'BackgroundColor', [0.98, 0.99, 1.00], ...
                'FontColor', [0.20, 0.20, 0.20]);
            app.TempLabel.Layout.Column = 1;

            app.RawArea = uitextarea(readoutGrid, ...
                'Value', {'原始回包: --'}, ...
                'Editable', 'off', ...
                'FontName', 'Consolas');
            app.RawArea.Layout.Column = 2;

            app.Axes = uiaxes(mainGrid);
            app.Axes.Layout.Row = 4;
            title(app.Axes, '温度读取曲线');
            xlabel(app.Axes, '时间 / s');
            ylabel(app.Axes, '温度 / °C');
            grid(app.Axes, 'on');
            app.Axes.Box = 'on';
            app.TempLine = plot(app.Axes, nan, nan, ...
                'LineWidth', 1.6, ...
                'Color', [0.82, 0.24, 0.11], ...
                'Marker', '.');

            app.LogArea = uitextarea(mainGrid, ...
                'Value', app.LogLines, ...
                'Editable', 'off', ...
                'FontName', 'Consolas');
            app.LogArea.Layout.Row = 5;
        end

        function refreshPorts(app)
            try
                ports = string(serialportlist("available"));
            catch ME
                ports = strings(0, 1);
                app.logLine("串口列表读取失败: " + string(ME.message));
            end

            if isempty(ports)
                app.StatusLabel.Text = '状态: 未检测到可用串口';
                app.logLine('未检测到可用串口。');
                return;
            end

            app.StatusLabel.Text = "状态: 可用串口 " + strjoin(ports, ', ');
            app.logLine("可用串口: " + strjoin(ports, ', '));
            if strlength(string(app.PortField.Value)) == 0
                app.PortField.Value = char(ports(1));
            end
        end

        function connectSerial(app)
            app.disconnectSerial(false);

            portName = strtrim(string(app.PortField.Value));
            baudRate = app.BaudRateField.Value;
            if strlength(portName) == 0
                app.showStatus('未填写COM端口。', true);
                return;
            end

            try
                app.SerialObj = serialport(portName, baudRate, "Timeout", 1.0);
                app.trySetSerialProperty('DataBits', 8);
                app.trySetSerialProperty('StopBits', 1);
                app.trySetSerialProperty('Parity', 'none');
                flush(app.SerialObj);
                app.showStatus(sprintf('已连接 %s @ %d, 8N1', portName, baudRate), false);
                app.logLine(sprintf('已连接 %s @ %d。', portName, baudRate));
            catch ME
                app.SerialObj = [];
                app.showStatus("串口连接失败: " + string(ME.message), true);
                app.logLine("串口连接失败: " + string(ME.message));
            end
        end

        function trySetSerialProperty(app, propertyName, value)
            try
                app.SerialObj.(propertyName) = value;
            catch
            end
        end

        function disconnectSerial(app, shouldLog)
            if nargin < 2
                shouldLog = true;
            end

            app.stopContinuous();
            serialObj = app.SerialObj;
            app.SerialObj = [];
            if ~isempty(serialObj)
                try
                    flush(serialObj);
                catch
                end
                try
                    delete(serialObj);
                catch
                end
            end

            if shouldLog
                app.showStatus('已断开。', false);
                app.logLine('串口已断开。');
            end
        end

        function readOnce(app)
            [value, rawText, statusText, ok] = app.readSensor();
            app.updateReadout(value, rawText, statusText, ok);
        end

        function startContinuous(app)
            if ~app.hasSerialConnection()
                app.connectSerial();
            end
            if ~app.hasSerialConnection() || app.IsRunning
                return;
            end

            app.SessionStart = datetime('now');
            app.IsRunning = true;
            start(app.TimerObj);
            app.showStatus('连续读取中。', false);
            app.logLine('开始连续读取。');
        end

        function stopContinuous(app)
            if ~isempty(app.TimerObj)
                try
                    stop(app.TimerObj);
                catch
                end
            end
            app.IsRunning = false;
        end

        function onTimerTick(app)
            if ~app.IsRunning
                return;
            end

            [value, rawText, statusText, ok] = app.readSensor();
            app.updateReadout(value, rawText, statusText, ok);
            drawnow limitrate nocallbacks;
        end

        function [value, rawText, statusText, ok] = readSensor(app)
            value = NaN;
            rawText = "";
            statusText = "串口未连接。";
            ok = false;

            if ~app.hasSerialConnection()
                app.connectSerial();
                if ~app.hasSerialConnection()
                    return;
                end
            end

            serialObj = app.SerialObj;

            cmdText = app.currentCommandText();
            if strlength(cmdText) == 0
                statusText = "命令为空。";
                return;
            end

            try
                bufferedText = app.readAvailableText(serialObj);
                [bufferValue, bufferToken] = app.parseTemperature(bufferedText);
                if ~isnan(bufferValue)
                    value = bufferValue;
                    rawText = bufferedText;
                    statusText = "读取成功，来自串口缓冲: " + bufferToken;
                    ok = true;
                    return;
                end

                if ~app.hasSerialConnection()
                    statusText = "串口已断开，停止读取。";
                    return;
                end

                flush(serialObj);
                write(serialObj, uint8(hex2dec(char(cmdText))), "uint8");

                deadline = tic;
                rawBytes = zeros(0, 1, 'uint8');
                while toc(deadline) < app.ReadWindowField.Value
                    pause(0.02);
                    if ~app.hasSerialConnection()
                        statusText = "串口已断开，停止读取。";
                        return;
                    end

                    byteCount = serialObj.NumBytesAvailable;
                    if byteCount < 1
                        continue;
                    end

                    chunk = read(serialObj, byteCount, "uint8");
                    rawBytes = [rawBytes; chunk(:)]; %#ok<AGROW>
                    rawText = string(char(rawBytes(:).'));
                    [value, token] = app.parseTemperature(rawText);
                    if ~isnan(value)
                        statusText = "读取成功: " + token;
                        ok = true;
                        return;
                    end
                end

                rawText = string(char(rawBytes(:).'));
                if strlength(rawText) == 0
                    statusText = "未收到回包。若设备管理器显示CH340代码31，请先修复驱动。";
                else
                    statusText = "收到回包但未匹配 +000365 格式。";
                end
            catch ME
                statusText = "读取失败: " + string(ME.message);
            end
        end

        function cmdText = currentCommandText(app)
            if strcmpi(app.ModeDropDown.Value, 'object')
                cmdText = string(app.ObjectCommandField.Value);
            else
                cmdText = string(app.BodyCommandField.Value);
            end
            cmdText = upper(regexprep(char(cmdText), '[^0-9A-Fa-f]', ''));
            cmdText = string(cmdText);
        end

        function rawText = readAvailableText(~, serialObj)
            rawText = "";
            if isempty(serialObj)
                return;
            end
            byteCount = serialObj.NumBytesAvailable;
            if byteCount < 1
                return;
            end
            rawBytes = read(serialObj, byteCount, "uint8");
            rawText = string(char(rawBytes(:).'));
        end

        function tf = hasSerialConnection(app)
            tf = false;
            if isempty(app.SerialObj)
                return;
            end

            try
                app.SerialObj.NumBytesAvailable;
                tf = true;
            catch
                tf = false;
            end
        end

        function [value, token] = parseTemperature(~, rawText)
            value = NaN;
            token = "";
            if strlength(string(rawText)) == 0
                return;
            end

            tokenText = regexp(char(rawText), '[+-]\d{6}', 'match', 'once');
            if isempty(tokenText)
                return;
            end

            token = string(tokenText);
            value = str2double(tokenText) ./ 10.0;
        end

        function updateReadout(app, value, rawText, statusText, ok)
            elapsedSeconds = seconds(datetime('now') - app.SessionStart);
            app.TimeData(end + 1, 1) = elapsedSeconds;
            app.TempData(end + 1, 1) = value;
            % Trim to last 5 minutes to prevent unbounded memory growth
            maxHistory = 600;
            if numel(app.TimeData) > maxHistory
                app.TimeData = app.TimeData(end - maxHistory + 1:end);
                app.TempData = app.TempData(end - maxHistory + 1:end);
            end

            if ok && ~isnan(value)
                app.TempLabel.Text = sprintf('%.1f °C', value);
                app.TempLabel.FontColor = [0.08, 0.45, 0.18];
            else
                app.TempLabel.Text = '-- °C';
                app.TempLabel.FontColor = [0.65, 0.18, 0.14];
            end

            if strlength(string(rawText)) == 0
                rawDisplay = '--';
            else
                rawDisplay = char(rawText);
            end

            app.RawArea.Value = { ...
                ['原始回包: ', rawDisplay], ...
                ['解析状态: ', char(statusText)]};
            app.showStatus(statusText, ~ok);
            app.logStatus(statusText);

            set(app.TempLine, ...
                'XData', app.TimeData, ...
                'YData', app.TempData);
            if ~isempty(app.TimeData)
                xlim(app.Axes, [max(0, app.TimeData(end) - 60), max(60, app.TimeData(end) + eps)]);
            end
        end

        function clearData(app)
            app.TimeData = zeros(0, 1);
            app.TempData = zeros(0, 1);
            app.SessionStart = datetime('now');
            set(app.TempLine, 'XData', nan, 'YData', nan);
            app.TempLabel.Text = '-- °C';
            app.TempLabel.FontColor = [0.20, 0.20, 0.20];
            app.RawArea.Value = {'原始回包: --'};
            app.logLine('已清空读取曲线。');
        end

        function showStatus(app, statusText, isWarning)
            app.StatusLabel.Text = "状态: " + string(statusText);
            if isWarning
                app.StatusLabel.FontColor = [0.75, 0.18, 0.12];
            else
                app.StatusLabel.FontColor = [0.12, 0.40, 0.18];
            end
        end

        function logLine(app, messageText)
            stamp = char(datetime('now', 'Format', 'HH:mm:ss'));
            line = sprintf('[%s] %s', stamp, char(string(messageText)));
            app.LogLines = [{line}; app.LogLines(:)];
            if numel(app.LogLines) > 40
                app.LogLines = app.LogLines(1:40);
            end
            if ~isempty(app.LogArea) && isvalid(app.LogArea)
                app.LogArea.Value = app.LogLines;
            end
        end

        function logStatus(app, statusText)
            statusText = string(statusText);
            nowTime = datetime('now');
            if statusText == app.LastLoggedStatus && seconds(nowTime - app.LastLoggedTime) < 5
                return;
            end

            app.LastLoggedStatus = statusText;
            app.LastLoggedTime = nowTime;
            app.logLine(statusText);
        end
    end
end

function position = localInitialPosition()
screenSize = get(groot, 'ScreenSize');
width = min(980, max(820, screenSize(3) - 80));
height = min(680, max(560, screenSize(4) - 80));
xPos = screenSize(1) + max(20, (screenSize(3) - width) / 2);
yPos = screenSize(2) + max(40, (screenSize(4) - height) / 2);
position = round([xPos, yPos, width, height]);
end
