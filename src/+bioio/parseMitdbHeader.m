function header = parseMitdbHeader(headerFile)
%PARSEMITDBHEADER Parse a MIT-BIH WFDB header file.

lines = splitlines(string(fileread(headerFile)));
lines = strtrim(lines);
lines(lines == "") = [];

recordTokens = split(lines(1));
header = struct();
header.recordName = char(recordTokens(1));
header.numSignals = str2double(recordTokens(2));
header.fs = str2double(recordTokens(3));
header.numSamples = str2double(recordTokens(4));
emptyChannel = struct( ...
    'fileName', '', ...
    'format', NaN, ...
    'gain', NaN, ...
    'bitResolution', NaN, ...
    'zeroValue', NaN, ...
    'firstValue', NaN, ...
    'checksum', NaN, ...
    'blockSize', NaN, ...
    'description', "");
header.channels = repmat(emptyChannel, header.numSignals, 1);
header.comments = strings(0, 1);

for idx = 1:header.numSignals
    tokens = split(lines(1 + idx));
    tokens(tokens == "") = [];
    channel = struct();
    channel.fileName = char(tokens(1));
    channel.format = str2double(tokens(2));
    channel.gain = localParseNumericToken(tokens(3), 200);
    channel.bitResolution = localParseNumericToken(tokens(4), 11);
    channel.zeroValue = localParseNumericToken(tokens(5), 0);
    channel.firstValue = localParseNumericToken(tokens(6), 0);
    channel.checksum = localParseNumericToken(tokens(7), 0);
    channel.blockSize = localParseNumericToken(tokens(8), 0);
    channel.description = strjoin(tokens(9:end), " ");
    header.channels(idx) = channel;
end

if numel(lines) > 1 + header.numSignals
    header.comments = lines((2 + header.numSignals):end);
end
end

function value = localParseNumericToken(token, defaultValue)
matches = regexp(char(token), '[-+]?\d+(\.\d+)?', 'match', 'once');
if isempty(matches)
    value = defaultValue;
else
    value = str2double(matches);
end
end
