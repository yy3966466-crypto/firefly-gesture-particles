classdef TemperatureStream < handle
    %TEMPERATURESTREAM Demo/serial temperature source for MATLAB monitoring.

    properties (SetAccess = private)
        requestedMode string = "demo"
        activeMode string = "demo"
        settings struct
        lastValue double = NaN
        lastStatus string = "demo 模式：使用占位温度序列"
    end

    properties (Access = private)
        serialObj = []
        demoCounter double = 0
    end

    methods
        function obj = TemperatureStream(mode, settings)
            if nargin < 1 || isempty(mode)
                mode = "demo";
            end
            if nargin < 2
                settings = struct();
            end

            obj.requestedMode = string(mode);
            obj.settings = obj.localApplyDefaults(settings);
            obj.localConnect();
        end

        function [value, meta] = next(obj, measurementMode)
            if nargin < 2 || isempty(measurementMode)
                measurementMode = "body";
            end
            measurementMode = string(measurementMode);

            switch lower(char(obj.activeMode))
                case 'serial'
                    [value, rawText] = obj.localReadSerial(measurementMode);
                case 'demo'
                    [value, rawText] = obj.localReadDemo(measurementMode);
                otherwise
                    value = NaN;
                    rawText = "";
            end

            obj.lastValue = value;
            meta = struct( ...
                'mode', char(obj.activeMode), ...
                'status', char(obj.lastStatus), ...
                'rawText', rawText);
        end

        function delete(obj)
            obj.localDisconnect();
        end
    end

    methods (Access = private)
        function settings = localApplyDefaults(~, settings)
            defaults = struct( ...
                'port', "", ...
                'baudRate', 9600, ...
                'requestPause', 0.20, ...
                'bodyCmd', "AB", ...
                'objectCmd', "AA", ...
                'demoBaseBody', 36.6, ...
                'demoBaseObject', 25.0);

            settings = localMergeStructs(defaults, settings);
        end

        function localConnect(obj)
            obj.localDisconnect();

            if ~strcmpi(char(obj.requestedMode), 'serial')
                obj.activeMode = "demo";
                obj.lastStatus = "demo 模式：使用占位温度序列";
                return;
            end

            try
                availablePorts = string(serialportlist("available"));
                if strlength(obj.settings.port) == 0
                    error('未填写 COM 端口。');
                end
                if ~any(strcmpi(obj.settings.port, availablePorts))
                    error('未检测到串口 %s。', obj.settings.port);
                end

                obj.serialObj = serialport(obj.settings.port, obj.settings.baudRate, "Timeout", 1.0);
                flush(obj.serialObj);
                obj.activeMode = "serial";
                obj.lastStatus = sprintf('已连接 %s @ %d', obj.settings.port, obj.settings.baudRate);
            catch ME
                obj.serialObj = [];
                obj.activeMode = "serial-error";
                obj.lastStatus = "串口不可用，未采集真实体温: " + string(ME.message);
            end
        end

        function localDisconnect(obj)
            if ~isempty(obj.serialObj)
                try
                    flush(obj.serialObj);
                catch
                end
                try
                    delete(obj.serialObj);
                catch
                end
            end
            obj.serialObj = [];
        end

        function [value, rawText] = localReadSerial(obj, measurementMode)
            if isempty(obj.serialObj)
                value = NaN;
                rawText = "";
                obj.activeMode = "serial-error";
                obj.lastStatus = "串口对象为空，当前体温无有效数据。";
                return;
            end

            if strcmpi(measurementMode, "object")
                cmdText = obj.settings.objectCmd;
            else
                cmdText = obj.settings.bodyCmd;
            end

            [bufferValue, bufferRawText, hasBufferedFrame] = obj.localReadAvailableFrame();
            if hasBufferedFrame
                value = bufferValue;
                rawText = bufferRawText;
                obj.lastStatus = sprintf('串口在线: %s, 缓冲回包 %s', obj.settings.port, char(rawText));
                return;
            end

            flush(obj.serialObj);
            write(obj.serialObj, uint8(hex2dec(char(cmdText))), "uint8");

            rawBytes = zeros(0, 1, 'uint8');
            pollTimer = tic;
            while toc(pollTimer) < obj.settings.requestPause
                pause(0.02);
                byteCount = obj.serialObj.NumBytesAvailable;
                if byteCount > 0
                    chunk = read(obj.serialObj, byteCount, "uint8");
                    rawBytes = [rawBytes; chunk(:)]; %#ok<AGROW>
                    rawText = string(char(rawBytes(:).'));
                    token = regexp(char(rawText), '[+-]\d{6}', 'match', 'once');
                    if ~isempty(token)
                        value = str2double(token) ./ 10.0;
                        obj.lastStatus = sprintf('串口在线: %s, 原始回包 %s', obj.settings.port, token);
                        return;
                    end
                end
            end

            if isempty(rawBytes)
                rawText = "";
                value = NaN;
                obj.lastStatus = "串口已连接，但当前轮询未收到数据，体温无有效数据。";
                return;
            end

            rawText = string(char(rawBytes(:).'));
            token = regexp(char(rawText), '[+-]\d{6}', 'match', 'once');

            if isempty(token)
                value = NaN;
                obj.lastStatus = "串口已连接，但返回帧未匹配 +000365 这类 ASCII 温度格式，体温无有效数据。";
                return;
            end

            value = str2double(token) ./ 10.0;
            obj.lastStatus = sprintf('串口在线: %s, 原始回包 %s', obj.settings.port, token);
        end

        function [value, rawText, hasFrame] = localReadAvailableFrame(obj)
            hasFrame = false;
            value = NaN;
            rawText = "";

            byteCount = obj.serialObj.NumBytesAvailable;
            if byteCount < 1
                return;
            end

            rawBytes = read(obj.serialObj, byteCount, "uint8");
            rawText = string(char(rawBytes(:).'));
            token = regexp(char(rawText), '[+-]\d{6}', 'match', 'once');
            if isempty(token)
                return;
            end

            value = str2double(token) ./ 10.0;
            hasFrame = true;
        end

        function [value, rawText] = localReadDemo(obj, measurementMode)
            obj.demoCounter = obj.demoCounter + 1;

            if strcmpi(measurementMode, "object")
                baseValue = obj.settings.demoBaseObject;
            else
                baseValue = obj.settings.demoBaseBody;
            end

            value = baseValue + ...
                0.08 * sin(2 * pi * obj.demoCounter / 90) + ...
                0.04 * cos(2 * pi * obj.demoCounter / 37) + ...
                0.02 * randn();

            rawText = sprintf('%+07.0f', value * 10);
            obj.lastStatus = "demo 模式：当前为占位温度序列，后续可切换真实串口";
        end
    end
end

function merged = localMergeStructs(defaults, overrides)
merged = defaults;
if isempty(overrides)
    return;
end

fields = fieldnames(overrides);
for idx = 1:numel(fields)
    merged.(fields{idx}) = overrides.(fields{idx});
end
end
