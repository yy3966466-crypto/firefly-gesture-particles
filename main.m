function app = main()
%MAIN Launch the universal multi-parameter monitoring demo app.

projectRoot = fileparts(mfilename('fullpath'));
if isempty(projectRoot)
    projectRoot = pwd;
end

srcRoot = fullfile(projectRoot, 'src');
if ~isfolder(srcRoot)
    error('BioMonitor:MissingSourceFolder', ...
        '未找到项目源码目录: %s', srcRoot);
end

% Put this project's code at the front of the MATLAB path for this session.
% This avoids interference from stale global startup paths without changing
% any MATLAB files or user path settings outside the project.
addpath(genpath(srcRoot), '-begin');

try
    app = BioMonitorApp(projectRoot);
catch ME
    fprintf(2, '\nBioMonitor 启动失败。\n');
    fprintf(2, '项目目录: %s\n', projectRoot);
    fprintf(2, 'MATLAB版本: %s (%s)\n', version, version('-release'));
    fprintf(2, '%s\n', getReport(ME, 'extended', 'hyperlinks', 'off'));
    rethrow(ME);
end

% When users call `main` without assigning the output, keep a reference in
% the base workspace so the handle object is not destroyed immediately.
if nargout == 0
    assignin('base', 'bioMonitorApp', app);
end
end
