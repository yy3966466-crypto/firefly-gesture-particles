function annotations = loadMitdbAnnotations(mitdbFolder, record)
%LOADMITDBANNOTATIONS Load MIT-BIH R-peak annotations.
%   annotations = LOADMITDBANNOTATIONS(mitdbFolder, record)
%   Loads pre-extracted R-peak sample positions from mitdb_annotations.mat.
%
%   Returns struct with fields: .samples (double column), .count

    matFile = fullfile(mitdbFolder, 'mitdb_annotations.mat');

    if ~isfile(matFile)
        error(['Annotation file not found: %s\n', ...
               'Run scripts/prepareAnnotations.m first to extract annotations.'], matFile);
    end

    targetName = ['r_', record];
    data = load(matFile, targetName);
    if ~isfield(data, targetName)
        error('Record %s not found in annotation file.', record);
    end

    samples = double(data.(targetName));
    samples = samples(:);
    annotations.samples = samples;
    annotations.count = length(samples);
end
