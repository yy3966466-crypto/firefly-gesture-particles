% EVALUATEECGDETECTION  Evaluate R-wave detection against MIT-BIH annotations.
%
%   Loads MIT-BIH records (105,124,208,221,233,234), runs processEcg,
%   compares detected R-waves against gold-standard annotations, and
%   reports accuracy, sensitivity, F1, and heart-rate MAE.
%
%   Accuracy  = TP / (TP + FP)
%   Sensitivity = TP / (TP + FN)
%   F1 = 2 * (Acc * Se) / (Acc + Se)
%
%   A detected R-wave is considered a true positive (TP) if it falls
%   within ±150 ms of a reference annotation.

clear; clc;
fprintf('=== ECG R-wave Detection Evaluation ===\n\n');

projectRoot = fileparts(fileparts(mfilename('fullpath')));
addpath(genpath(fullfile(projectRoot, 'src')));

records = {'105', '124', '208', '221', '233', '234'};
mitdbFolder = fullfile(projectRoot, 'data', 'public', 'mitdb');

results = struct();

for rIdx = 1:numel(records)
    record = records{rIdx};
    fprintf('Processing record %s ...\n', record);

    % 1. Load raw signal
    ecgRecord = bioio.loadMitdbRecord(mitdbFolder, record, 1);
    raw = ecgRecord.signal;
    fs = ecgRecord.fs;
    toleranceSamples = round(0.150 * fs);  % ±150 ms at record's actual sampling rate

    % 2. Run detector
    result = bioalg.processEcg(raw, fs);
    detectedLocs = double(result.rLocs);

    % 3. Load ground truth annotations
    annotations = bioio.loadMitdbAnnotations(mitdbFolder, record);
    trueLocs = annotations.samples;

    % 4. Compare: for each true beat, check if a detection falls within
    %    tolerance window. This avoids double-counting.
    trueDetected = false(size(trueLocs));
    detectedMatched = false(size(detectedLocs));

    for tIdx = 1:length(trueLocs)
        tLoc = trueLocs(tIdx);
        dist = abs(detectedLocs - tLoc);
        [minDist, dIdx] = min(dist);
        if minDist <= toleranceSamples && ~detectedMatched(dIdx)
            trueDetected(tIdx) = true;
            detectedMatched(dIdx) = true;
        end
    end

    TP = sum(trueDetected);
    FN = sum(~trueDetected);           % missed beats
    FP = sum(~detectedMatched);        % false alarms

    accuracy = TP / (TP + FP) * 100;
    sensitivity = TP / (TP + FN) * 100;
    f1 = 2 * (accuracy/100 * sensitivity/100) / ...
        (accuracy/100 + sensitivity/100 + eps) * 100;

    % 5. Heart Rate MAE
    % Compute HR from detected beats and compare with true beats
    % Use running 5-beat average windows
    if length(trueLocs) > 5 && length(detectedLocs) > 5
        trueRR = diff(trueLocs) / fs;
        trueHR = 60 ./ trueRR;
        detectedRR = diff(detectedLocs) / fs;
        detectedHR = 60 ./ detectedRR;

        % Align: find matching beats within tolerance and compare HR
        matchedTrue = [];
        matchedDetected = [];
        usedDetected = false(size(detectedLocs));

        for tIdx = 1:length(trueLocs)
            dists = abs(detectedLocs - trueLocs(tIdx));
            valid = dists <= toleranceSamples & ~usedDetected;
            if any(valid)
                [~, dIdx] = min(dists);
                usedDetected(dIdx) = true;
                matchedTrue(end+1) = tIdx;       %#ok<AGROW>
                matchedDetected(end+1) = dIdx;   %#ok<AGROW>
            end
        end

        if length(matchedTrue) > 5
            % Compare instantaneous HR (from RR intervals)
            trueHRVals = trueHR(matchedTrue(1:end-1));  % RR(i) → HR at beat i+1
            trueHRVals = trueHRVals(~isinf(trueHRVals) & ~isnan(trueHRVals));

            detHRVals = detectedHR(matchedDetected(1:end-1));
            detHRVals = detHRVals(~isinf(detHRVals) & ~isnan(detHRVals));

            minLen = min(length(trueHRVals), length(detHRVals));
            hrMAE = mean(abs(trueHRVals(1:minLen) - detHRVals(1:minLen)));
        else
            hrMAE = NaN;
        end
    else
        hrMAE = NaN;
    end

    % 6. Store results
    results(1).(['r_', record]) = struct( ...
        'totalBeats', length(trueLocs), ...
        'detectedBeats', length(detectedLocs), ...
        'TP', TP, 'FP', FP, 'FN', FN, ...
        'accuracyPct', accuracy, ...
        'sensitivityPct', sensitivity, ...
        'f1Pct', f1, ...
        'hrMAE', hrMAE);

    fprintf('  Total: %d, Detected: %d, TP: %d, FP: %d, FN: %d\n', ...
        length(trueLocs), length(detectedLocs), TP, FP, FN);
    fprintf('  Acc: %.2f%%, Se: %.2f%%, F1: %.2f%%, HR MAE: %.2f bpm\n\n', ...
        accuracy, sensitivity, f1, hrMAE);
end

% 7. Summary table
fprintf('=== Summary ===\n');
fprintf('%-8s %-6s %-6s %-6s %-6s %-8s %-8s %-8s %-8s\n', ...
    'Record', 'Total', 'Detect', 'TP', 'FP', 'Acc(%)', 'Se(%)', 'F1(%)', 'HR_MAE');
fprintf(repmat('-', 72, 1)); fprintf('\n');

totalTP = 0; totalFP = 0; totalFN = 0; totalBeats = 0;
for rIdx = 1:numel(records)
    r = results.(['r_', records{rIdx}]);
    fprintf('%-8s %-6d %-6d %-6d %-6d %-8.2f %-8.2f %-8.2f %-8.2f\n', ...
        records{rIdx}, r.totalBeats, r.detectedBeats, r.TP, r.FP, ...
        r.accuracyPct, r.sensitivityPct, r.f1Pct, r.hrMAE);
    totalTP = totalTP + r.TP;
    totalFP = totalFP + r.FP;
    totalFN = totalFN + r.FN;
    totalBeats = totalBeats + r.totalBeats;
end
fprintf(repmat('-', 72, 1)); fprintf('\n');

avgAcc = totalTP / (totalTP + totalFP) * 100;
avgSe = totalTP / (totalTP + totalFN) * 100;
avgF1 = 2 * (avgAcc/100 * avgSe/100) / (avgAcc/100 + avgSe/100) * 100;
fprintf('%-8s %-6d %-6d %-6d %-6d %-8.2f %-8.2f %-8.2f\n', ...
    'AVG', totalBeats, totalTP+totalFP, totalTP, totalFP, avgAcc, avgSe, avgF1);

fprintf('\nDone.\n');
