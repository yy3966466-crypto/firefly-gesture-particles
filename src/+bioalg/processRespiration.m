function result = processRespiration(signal, fs)
%PROCESSRESPIRATION Adaptive enhancement and breathing-rate extraction.

signal = signal(:);
t = (0:(numel(signal) - 1)).' ./ fs;

baselineWindow = max(5, round(1.20 * fs));
baseline = movmean(signal, baselineWindow, 'omitnan');
detrended = signal - baseline;
bandpassed = bioalg.bandpassSignal(detrended, fs, [0.08, 0.80]);
bandpassed = movmean(bandpassed, max(3, round(0.12 * fs)));

order = max(8, min(40, round(0.40 * fs)));
delay = max(order + 2, round(0.25 * fs));
stepSize = 0.015 / (order * max(var(bandpassed, 'omitnan'), eps));
[enhanced, errorSignal] = localRunAle(bandpassed, order, delay, stepSize);
enhanced = movmean(enhanced, max(3, round(0.95 * fs)));

trend = movmean(enhanced, max(5, round(4.00 * fs)));
spread = movmean(abs(enhanced - trend), max(5, round(4.00 * fs)));
threshold = trend + 0.20 .* spread;

candidateLocs = find(enhanced(2:end-1) >= enhanced(1:end-2) & ...
                     enhanced(2:end-1) > enhanced(3:end)) + 1;
candidateLocs = candidateLocs(enhanced(candidateLocs) >= threshold(candidateLocs));

if numel(candidateLocs) < 3
    fallbackThreshold = mean(enhanced, 'omitnan') + 0.10 * std(enhanced, 'omitnan');
    candidateLocs = find(enhanced(2:end-1) >= enhanced(1:end-2) & ...
                         enhanced(2:end-1) > enhanced(3:end) & ...
                         enhanced(2:end-1) >= fallbackThreshold) + 1;
end

peakLocs = bioalg.selectPeaks(candidateLocs, enhanced, round(1.40 * fs));
respIntervals = diff(peakLocs) ./ fs;
respRate = 60 ./ respIntervals;
respRateTimes = t(peakLocs(2:end));

result = struct();
result.fs = fs;
result.t = t;
result.raw = signal;
result.bandpassed = bandpassed;
result.enhanced = enhanced;
result.errorSignal = errorSignal;
result.threshold = threshold;
result.peakLocs = peakLocs(:);
result.respRate = respRate(:);
result.respRateTimes = respRateTimes(:);
result.snrDb = bioalg.estimateSnr(signal, enhanced);
end

function [enhanced, errorSignal] = localRunAle(signal, order, delay, stepSize)
sampleCount = numel(signal);
weights = zeros(order, 1);
enhanced = zeros(sampleCount, 1);
errorSignal = zeros(sampleCount, 1);
twoMu = 2 * stepSize;

% Delay-line buffer avoids per-iteration vector construction overhead
buffer = zeros(order, 1);
startIdx = delay + order;

for idx = startIdx:sampleCount
    buffer(2:end) = buffer(1:end-1);
    buffer(1) = signal(idx - delay);
    enhanced(idx) = weights.' * buffer;
    errorSignal(idx) = signal(idx) - enhanced(idx);
    weights = weights + twoMu * errorSignal(idx) * buffer;
end

headLength = min(delay + order - 1, sampleCount);
enhanced(1:headLength) = signal(1:headLength);
end
