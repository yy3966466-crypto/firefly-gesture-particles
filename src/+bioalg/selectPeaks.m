function peakLocs = selectPeaks(candidateLocs, signal, minDistance)
%SELECTPEAKS Keep the largest peak in each refractory window.

candidateLocs = unique(candidateLocs(:));
if isempty(candidateLocs)
    peakLocs = zeros(0, 1);
    return;
end

candidateLocs = sort(candidateLocs);
peakLocs = zeros(size(candidateLocs));
writeIdx = 0;
cursor = 1;
totalCandidates = numel(candidateLocs);

while cursor <= totalCandidates
    blockEnd = candidateLocs(cursor) + minDistance;
    bestIdx = cursor;
    probe = cursor + 1;
    while probe <= totalCandidates && candidateLocs(probe) <= blockEnd
        if signal(candidateLocs(probe)) > signal(candidateLocs(bestIdx))
            bestIdx = probe;
        end
        probe = probe + 1;
    end
    writeIdx = writeIdx + 1;
    peakLocs(writeIdx) = candidateLocs(bestIdx);
    cursor = probe;
end

peakLocs = peakLocs(1:writeIdx);
end
