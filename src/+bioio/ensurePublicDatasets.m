function manifest = ensurePublicDatasets(projectRoot, plan)
%ENSUREPUBLICDATASETS Download required public datasets when missing.

if nargin < 2 || isempty(plan)
    plan = bioio.getRandomDatasetPlan("abnormal");
end

dataRoot = fullfile(projectRoot, 'data', 'public');
mitdbFolder = fullfile(dataRoot, 'mitdb');
bidmcFolder = fullfile(dataRoot, 'bidmc');

if ~isfolder(mitdbFolder)
    mkdir(mitdbFolder);
end
if ~isfolder(bidmcFolder)
    mkdir(bidmcFolder);
end

mitdbBase = 'https://physionet.org/files/mitdb/1.0.0/';
bidmcBase = 'https://physionet.org/files/bidmc/1.0.0/bidmc_csv/';

mitdbFiles = { ...
    [plan.ecgRecord, '.hea'], ...
    [plan.ecgRecord, '.dat'], ...
    [plan.ecgRecord, '.atr']};
bidmcFiles = { ...
    ['bidmc_', plan.respRecord, '_Signals.csv'], ...
    ['bidmc_', plan.respRecord, '_Numerics.csv'], ...
    ['bidmc_', plan.respRecord, '_Fix.txt']};

manifest = struct();
manifest.dataRoot = dataRoot;
manifest.mitdbFolder = mitdbFolder;
manifest.bidmcFolder = bidmcFolder;
manifest.plan = plan;
manifest.downloadedFiles = strings(0, 1);
manifest.existingFiles = strings(0, 1);

for k = 1:numel(mitdbFiles)
    localPath = fullfile(mitdbFolder, mitdbFiles{k});
    if isfile(localPath)
        manifest.existingFiles(end + 1) = string(localPath); %#ok<AGROW>
    else
        bioio.downloadPhysioNetFile([mitdbBase, mitdbFiles{k}], localPath);
        manifest.downloadedFiles(end + 1) = string(localPath); %#ok<AGROW>
    end
end

for k = 1:numel(bidmcFiles)
    localPath = fullfile(bidmcFolder, bidmcFiles{k});
    if isfile(localPath)
        manifest.existingFiles(end + 1) = string(localPath); %#ok<AGROW>
    else
        bioio.downloadPhysioNetFile([bidmcBase, bidmcFiles{k}], localPath);
        manifest.downloadedFiles(end + 1) = string(localPath); %#ok<AGROW>
    end
end

manifest.downloadCount = numel(manifest.downloadedFiles);
manifest.localHitCount = numel(manifest.existingFiles);
end
