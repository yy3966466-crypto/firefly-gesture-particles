% FIXANNOTATIONS  Re-save mitdb_annotations.mat with MATLAB-compatible names.
%
%   The original file used numeric record IDs (e.g. '105', '124') as
%   variable names. MATLAB's load() cannot create struct fields starting
%   with digits, causing "字段名称无效" errors.
%
%   This script calls fix_annotations.py to read and re-save the MAT file
%   with 'r_' prefix (e.g. 'r_105', 'r_124').

clear; clc;
fprintf('=== Fix MIT-BIH Annotations MAT File ===\n\n');

projectRoot = fileparts(fileparts(mfilename('fullpath')));
mitdbFolder = fullfile(projectRoot, 'data', 'public', 'mitdb');
matFile = fullfile(mitdbFolder, 'mitdb_annotations.mat');
pyScript = fullfile(projectRoot, 'scripts', 'fix_annotations.py');

if ~isfile(matFile)
    error('Annotation file not found: %s', matFile);
end

cmd = sprintf('python "%s" "%s"', pyScript, matFile);
fprintf('Running: %s\n', cmd);
[status, result] = system(cmd);

if status ~= 0
    error('Python fix failed:\n%s', result);
end

fprintf('%s\n', strtrim(result));

% Verify
info = whos('-file', matFile);
fprintf('New file contains %d variable(s):\n', numel(info));
for i = 1:min(numel(info), 10)
    fprintf('  %s (%s, %d elements)\n', info(i).name, info(i).class, info(i).size(1));
end
if numel(info) > 10
    fprintf('  ... and %d more\n', numel(info) - 10);
end

fprintf('\nDone.\n');
