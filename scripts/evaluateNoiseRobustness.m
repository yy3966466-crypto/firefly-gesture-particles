% EVALUATENOISEROBUSTNESS  Anti-interference test with controlled noise.
%
%   Loads MIT-BIH records, adds controlled noise at various SNR levels,
%   runs R-wave detection, and measures accuracy degradation.
%
%   Noise types:
%     - Gaussian white noise (muscle artifact simulation)
%     - 50 Hz sinusoidal interference (power-line simulation)
%     - Random pulse interference (motion artifact simulation)
%
%   Reports detection accuracy at each SNR level.

clear; clc;
fprintf('=== Noise Robustness Evaluation ===\n\n');

projectRoot = fileparts(fileparts(mfilename('fullpath')));
addpath(genpath(fullfile(projectRoot, 'src')));

records = {'105', '124', '221', '233'};
mitdbFolder = fullfile(projectRoot, 'data', 'public', 'mitdb');
toleranceSamples = round(0.150 * 360);  % ±150 ms at 360 Hz

% SNR levels to test (dB)
snrLevels = [30, 20, 15, 10, 5, 0];

% Noise types
noiseTypes = {'gaussian', 'powerline', 'pulse'};
noiseLabels = {'Gaussian white (muscle)', '50 Hz (power-line)', 'Pulse (motion artifact)'};

for rIdx = 1:numel(records)
    record = records{rIdx};
    fprintf('\n--- Record %s ---\n', record);

    % Load raw signal
    ecgRecord = bioio.loadMitdbRecord(mitdbFolder, record, 1);
    raw = ecgRecord.signal;
    fs = ecgRecord.fs;
    n = length(raw);
    t = (0:n-1)' / fs;

    % Get baseline performance (clean signal)
    baselineResult = bioalg.processEcg(raw, fs);
    baselineLocs = double(baselineResult.rLocs);

    % Load annotations
    annotations = bioio.loadMitdbAnnotations(mitdbFolder, record);
    trueLocs = annotations.samples;

    % Remove NaN from trueLocs for comparison
    trueLocs = trueLocs(~isnan(trueLocs));
    if isempty(trueLocs)
        fprintf('  No annotations found, skipping.\n');
        continue;
    end

    % Compute baseline accuracy
    trueDetected = false(size(trueLocs));
    detectedMatched = false(size(baselineLocs));
    for tIdx = 1:length(trueLocs)
        dist = abs(baselineLocs - trueLocs(tIdx));
        [minDist, dIdx] = min(dist);
        if minDist <= toleranceSamples && ~detectedMatched(dIdx)
            trueDetected(tIdx) = true;
            detectedMatched(dIdx) = true;
        end
    end
    TP0 = sum(trueDetected);
    FN0 = sum(~trueDetected);
    FP0 = sum(~detectedMatched);
    acc0 = TP0 / (TP0 + FP0) * 100;
    se0  = TP0 / (TP0 + FN0) * 100;

    fprintf('  Baseline SNR: %.2f dB, Acc: %.1f%%, Se: %.1f%%\n', ...
        baselineResult.snrDb, acc0, se0);

    for nType = 1:length(noiseTypes)
        noiseType = noiseTypes{nType};
        fprintf('  Noise: %s\n', noiseLabels{nType});

        for sIdx = 1:length(snrLevels)
            targetSNR = snrLevels(sIdx);

            % Generate noise with controlled power
            signalPower = var(raw, 'omitnan');

            switch noiseType
                case 'gaussian'
                    noisePower = signalPower / (10^(targetSNR/10));
                    noise = sqrt(noisePower) * randn(n, 1);
                    noise = noise - mean(noise);

                case 'powerline'
                    % 50 Hz + harmonics
                    noisePower = signalPower / (10^(targetSNR/10));
                    amp = sqrt(2 * noisePower);
                    noise = amp * sin(2*pi*50*t + 2*pi*rand());
                    % Add 3rd harmonic for realism
                    noise = noise + 0.3*amp * sin(2*pi*150*t + 2*pi*rand());

                case 'pulse'
                    % Random pulse artifacts
                    numPulses = round(n / (10*fs));  % ~1 pulse per 10 seconds
                    pulseLocations = randi([round(0.05*fs), n-round(0.05*fs)], numPulses, 1);
                    noise = zeros(n, 1);
                    for pIdx = 1:numPulses
                        pLoc = pulseLocations(pIdx);
                        pulseDur = randi([round(0.02*fs), round(0.10*fs)]);
                        pulseAmp = (rand() * 2 + 1) * sqrt(signalPower);
                        pulseStart = max(1, pLoc - round(pulseDur/2));
                        pulseEnd = min(n, pLoc + round(pulseDur/2));
                        window = hamming(pulseEnd - pulseStart + 1);
                        noise(pulseStart:pulseEnd) = noise(pulseStart:pulseEnd) + ...
                            pulseAmp * window .* (2*rand(pulseEnd-pulseStart+1, 1) - 1);
                    end
                    % Scale to target SNR
                    currentPower = var(noise, 'omitnan');
                    targetPower = signalPower / (10^(targetSNR/10));
                    if currentPower > eps
                        noise = noise * sqrt(targetPower / currentPower);
                    end
            end

            % Add noise to signal
            noisy = raw + noise;

            % Run detector
            noisyResult = bioalg.processEcg(noisy, fs);
            detectedLocs = double(noisyResult.rLocs);

            % Evaluate
            trueDetected = false(size(trueLocs));
            detectedMatched = false(size(detectedLocs));
            for tIdx = 1:length(trueLocs)
                dist = abs(detectedLocs - trueLocs(tIdx));
                [minDist, dIdx] = min(dist);
                if minDist <= toleranceSamples && ~detectedMatched(dIdx)
                    trueDetected(tIdx) = true;
                    detectedMatched(dIdx) = true;
                end
            end
            TP = sum(trueDetected);
            FN = sum(~trueDetected);
            FP = sum(~detectedMatched);
            acc = TP / (TP + FP) * 100;
            se  = TP / (TP + FN) * 100;

            % Compute actual SNR of noisy signal
            noiseEstimate = noisy - smoothdata(noisy, 'movmean', round(0.1*fs));
            actualSNR = 10 * log10(var(noisy, 'omitnan') / var(noiseEstimate, 'omitnan'));

            fprintf('    Target SNR %3d dB → Actual SNR %5.1f dB: Acc=%5.1f%%, Se=%5.1f%%\n', ...
                targetSNR, actualSNR, acc, se);
        end
    end
end

fprintf('\nDone.\n');
