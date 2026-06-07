function plan = getRandomDatasetPlan(mode, projectRoot)
%GETRANDOMDATASETPLAN Pick random public ECG/respiration records.
% mode: "abnormal", "mixed", or "normal"

if nargin < 1 || strlength(string(mode)) == 0
    mode = "abnormal";
end
if nargin < 2
    projectRoot = "";
end

mode = lower(string(mode));
rng('shuffle', 'twister');
% Small pause ensures distinct seeds for rapid consecutive calls
pause(0.002);

mitdbNormal = ["100","101","103","115","117"];
mitdbAbnormal = [ ...
    "105","106","108","109","111","112","114","116","118","119", ...
    "121","122","123","124","200","201","202","203","205","207", ...
    "208","209","210","212","213","214","215","217","219","220", ...
    "221","222","223","228","230","231","232","233","234"];

% Curated from BIDMC numerics so the respiratory rate is more likely to be
% outside the normal window or visibly irregular in the waveform.
bidmcNormal = ["01","06","07","08","09","12","16","22","24","30","47"];
bidmcAbnormal = ["05","11","14","27","32","33","38","41","50","53"];

switch mode
    case "normal"
        ecgPool = mitdbNormal;
        respPool = bidmcNormal;
    case "mixed"
        if rand < 0.70
            ecgPool = mitdbAbnormal;
        else
            ecgPool = mitdbNormal;
        end
        if rand < 0.60
            respPool = bidmcAbnormal;
        else
            respPool = bidmcNormal;
        end
    otherwise
        ecgPool = mitdbAbnormal;
        respPool = bidmcAbnormal;
        mode = "abnormal";
end

[ecgPool, ecgLocalOnly] = localPreferExisting(projectRoot, ecgPool, 'mitdb');
[respPool, respLocalOnly] = localPreferExisting(projectRoot, respPool, 'bidmc');

plan = struct();
plan.mode = char(mode);
plan.ecgRecord = char(ecgPool(randi(numel(ecgPool))));
plan.respRecord = char(respPool(randi(numel(respPool))));
plan.ecgLocalOnly = ecgLocalOnly;
plan.respLocalOnly = respLocalOnly;
end

function [pool, localOnly] = localPreferExisting(projectRoot, pool, datasetType)
localOnly = false;

if strlength(string(projectRoot)) == 0
    return;
end

existing = strings(0, 1);
for idx = 1:numel(pool)
    recordId = string(pool(idx));
    switch datasetType
        case 'mitdb'
            baseFolder = fullfile(projectRoot, 'data', 'public', 'mitdb');
            requiredFiles = { ...
                fullfile(baseFolder, recordId + ".hea"), ...
                fullfile(baseFolder, recordId + ".dat"), ...
                fullfile(baseFolder, recordId + ".atr")};
        otherwise
            baseFolder = fullfile(projectRoot, 'data', 'public', 'bidmc');
            requiredFiles = { ...
                fullfile(baseFolder, "bidmc_" + recordId + "_Signals.csv"), ...
                fullfile(baseFolder, "bidmc_" + recordId + "_Numerics.csv"), ...
                fullfile(baseFolder, "bidmc_" + recordId + "_Fix.txt")};
    end

    if all(cellfun(@isfile, requiredFiles))
        existing(end + 1) = recordId; %#ok<AGROW>
    end
end

if ~isempty(existing)
    pool = existing;
    localOnly = true;
end
end
