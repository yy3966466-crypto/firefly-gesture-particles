% PREPAREANNOTATIONS  Extract MIT-BIH R-peak annotations and save to MAT file.
%
%   This script reads MIT-BIH .atr annotation files (via Python wfdb),
%   extracts R-peak sample positions, and saves them to a single MAT file
%   at data/public/mitdb/mitdb_annotations.mat.
%
%   Prerequisites:
%     - Python with `wfdb` package installed (pip install wfdb)
%     - MIT-BIH .dat/.hea/.atr files in data/public/mitdb/
%
%   Output:
%     data/public/mitdb/mitdb_annotations.mat
%       Each variable is a double column vector named by record ID.
%       Example: load mitdb_annotations.mat -> 105 (2572x1 double)
%
%   Usage:
%     Run this script once before using evaluateEcgDetection.m.
%     The MIT-BIH files must be downloaded first via bioio.downloadMitdb().

clear; clc;
fprintf('=== Prepare MIT-BIH Annotations ===\n\n');

projectRoot = fileparts(fileparts(mfilename('fullpath')));
mitdbFolder = fullfile(projectRoot, 'data', 'public', 'mitdb');
records = {'100', '101', '102', '103', '104', '105', '106', '107', '108', ...
           '109', '111', '112', '113', '114', '115', '116', '117', '118', ...
           '119', '121', '122', '123', '124', '200', '201', '202', '203', ...
           '205', '207', '208', '209', '210', '212', '213', '214', '215', ...
           '217', '219', '220', '221', '222', '223', '228', '230', '231', ...
           '232', '233', '234'};

outputFile = fullfile(mitdbFolder, 'mitdb_annotations.mat');

% Use Python wfdb to extract annotations
allData = struct();

for i = 1:numel(records)
    record = records{i};
    atrFile = fullfile(mitdbFolder, [record, '.atr']);

    if ~isfile(atrFile)
        fprintf('  %s: .atr not found, skipping.\n', record);
        continue;
    end

    % Call Python wfdb via system
    pyScript = sprintf([ ...
        'import wfdb, json, sys; ', ...
        'ann = wfdb.rdann(r"%s", "atr", sampto=300000); ', ...
        'mask = [s in ("N", "L", "R", "B", "A", "a", "J", "S", "V", ' ...
        '"r", "F", "e", "j", "n", "E", "/", "f", "Q", "?") for s in ann.symbol]; ', ...
        'samples = [int(s) for s, m in zip(ann.sample, mask) if m]; ', ...
        'print(json.dumps(samples));'], ...
        strrep(atrFile, '\', '\\'));

    [status, raw] = system(['python -c "', pyScript, '"']);

    if status ~= 0
        fprintf('  %s: wfdb extraction failed, skipping.\n', record);
        continue;
    end

    samples = jsondecode(strtrim(raw));
    if isempty(samples)
        fprintf('  %s: no annotations found.\n', record);
        continue;
    end

    allData.(['r_', record]) = double(samples);
    fprintf('  %s: %d annotations extracted.\n', record, numel(samples));
end

if isempty(fieldnames(allData))
    fprintf('\nNo annotations extracted. Check MIT-BIH data files.\n');
    return;
end

save(outputFile, '-struct', 'allData');
fprintf('\nSaved %d records to %s\n', numel(fieldnames(allData)), outputFile);
fprintf('Done.\n');
