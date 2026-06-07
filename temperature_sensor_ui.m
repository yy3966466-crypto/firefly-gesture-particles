function varargout = temperature_sensor_ui()
%TEMPERATURE_SENSOR_UI Launch a standalone Type-C temperature sensor reader.

projectRoot = fileparts(mfilename('fullpath'));
if isempty(projectRoot)
    projectRoot = pwd;
end

srcRoot = fullfile(projectRoot, 'src');
if ~isfolder(srcRoot)
    error('TemperatureSensorUI:MissingSourceFolder', ...
        '未找到项目源码目录: %s', srcRoot);
end

addpath(genpath(srcRoot), '-begin');
app = TemperatureSensorReaderApp(projectRoot);
app.show();
assignin('base', 'temperatureSensorApp', app);

if nargout > 0
    varargout{1} = app;
end
end
