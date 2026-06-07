function result = processEcg(signal, fs)
%PROCESSECG Filtered ECG plus differential-threshold R-wave detection.

signal = signal(:);
t = (0:(numel(signal) - 1)).' ./ fs;

baselineWindow = max(5, round(0.20 * fs));
baseline = movmedian(signal, baselineWindow, 'omitnan');
detrended = signal - baseline;
filtered = bioalg.bandpassSignal(detrended, fs, [5, 18]);
filtered = movmean(filtered, max(3, round(0.02 * fs)));

diffSignal = [0; diff(filtered)];
diffEnvelope = movmean(abs(diffSignal), max(3, round(0.08 * fs)));
trend = movmean(diffEnvelope, max(5, round(1.50 * fs)));
spread = movmean(abs(diffEnvelope - trend), max(5, round(1.50 * fs)));
threshold = trend + 1.40 .* spread;

candidateLocs = find(filtered(2:end-1) >= filtered(1:end-2) & ...
                     filtered(2:end-1) > filtered(3:end)) + 1;
candidateLocs = candidateLocs(diffEnvelope(candidateLocs) >= threshold(candidateLocs));

if numel(candidateLocs) < 5
    fallbackThreshold = mean(diffEnvelope, 'omitnan') + 0.60 * std(diffEnvelope, 'omitnan');
    candidateLocs = find(filtered(2:end-1) >= filtered(1:end-2) & ...
                         filtered(2:end-1) > filtered(3:end) & ...
                         diffEnvelope(2:end-1) >= fallbackThreshold) + 1;
end

rLocs = bioalg.selectPeaks(candidateLocs, filtered, round(0.25 * fs));
if numel(rLocs) > 3
    peakValues = filtered(rLocs);
    peakFloor = median(peakValues, 'omitnan') - 1.20 * std(peakValues, 'omitnan');
    rLocs = rLocs(peakValues >= peakFloor);
end

rr = diff(rLocs) ./ fs;
heartRate = 60 ./ rr;
heartRateTimes = t(rLocs(2:end));

result = struct();
result.fs = fs;
result.t = t;
result.raw = signal;
result.filtered = filtered;
result.diffEnvelope = diffEnvelope;
result.threshold = threshold;
result.rLocs = rLocs(:);
result.heartRate = heartRate(:);
result.heartRateTimes = heartRateTimes(:);
result.snrDb = bioalg.estimateSnr(signal, filtered);
end
