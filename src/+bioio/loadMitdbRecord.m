function record = loadMitdbRecord(mitdbFolder, recordName, leadIndex)
%LOADMITDBRECORD Load a MIT-BIH ECG record without external WFDB tooling.

if nargin < 3
    leadIndex = 1;
end

headerFile = fullfile(mitdbFolder, [recordName, '.hea']);
dataFile = fullfile(mitdbFolder, [recordName, '.dat']);

header = bioio.parseMitdbHeader(headerFile);

if header.numSignals ~= 2 || header.channels(1).format ~= 212
    error('当前解析器仅实现了 2 通道 MIT-BIH 212 格式记录。');
end

fid = fopen(dataFile, 'r');
if fid < 0
    error('无法打开 ECG 数据文件: %s', dataFile);
end
cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
rawBytes = fread(fid, inf, 'uint8=>uint8');

frameCount = floor(numel(rawBytes) / 3);
rawBytes = rawBytes(1:(frameCount * 3));
triplets = reshape(rawBytes, 3, frameCount);

lead1 = double(triplets(1, :)) + bitshift(bitand(double(triplets(2, :)), 15), 8);
lead2 = double(triplets(3, :)) + bitshift(bitand(double(triplets(2, :)), 240), 4);

lead1(lead1 >= 2048) = lead1(lead1 >= 2048) - 4096;
lead2(lead2 >= 2048) = lead2(lead2 >= 2048) - 4096;

digitalSignals = [lead1; lead2];
physicalSignals = zeros(size(digitalSignals));
for idx = 1:header.numSignals
    gain = header.channels(idx).gain;
    zeroValue = header.channels(idx).zeroValue;
    physicalSignals(idx, :) = (digitalSignals(idx, :) - zeroValue) ./ gain;
end

leadNames = cellstr(string({header.channels.description}));
leadIndex = max(1, min(leadIndex, numel(leadNames)));
t = (0:(size(physicalSignals, 2) - 1)) ./ header.fs;

record = struct();
record.recordName = recordName;
record.fs = header.fs;
record.time = t(:);
record.signals = physicalSignals.';
record.signal = physicalSignals(leadIndex, :).';
record.leadName = leadNames{leadIndex};
record.leadNames = leadNames;
record.header = header;
end
