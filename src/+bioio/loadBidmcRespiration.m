function record = loadBidmcRespiration(bidmcFolder, recordId)
%LOADBIDMCRESPIRATION Load a BIDMC respiration signal from CSV.

csvFile = fullfile(bidmcFolder, ['bidmc_', recordId, '_Signals.csv']);
fixFile = fullfile(bidmcFolder, ['bidmc_', recordId, '_Fix.txt']);

headerLine = string(readlines(csvFile));
headerLine = headerLine(1);
channelNames = strtrim(split(headerLine, ','));

signalMatrix = readmatrix(csvFile);
timeVector = signalMatrix(:, 1);
respirationSignal = signalMatrix(:, 2);

dt = median(diff(timeVector), 'omitnan');
fs = round(1 / dt);

record = struct();
record.recordId = recordId;
record.time = timeVector;
record.signal = respirationSignal;
record.channelName = char(channelNames(2));
record.channelNames = cellstr(channelNames);
record.fs = fs;

if isfile(fixFile)
    record.note = strjoin(string(readlines(fixFile)), newline);
else
    record.note = "";
end
end
