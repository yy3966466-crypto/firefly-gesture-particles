function downloadPhysioNetFile(url, destination)
%DOWNLOADPHYSIONETFILE Download a PhysioNet file with a temporary target.

[parentFolder, ~, ~] = fileparts(destination);
if ~isfolder(parentFolder)
    mkdir(parentFolder);
end

tempDestination = [destination, '.download'];
options = weboptions( ...
    'Timeout', 60, ...
    'UserAgent', 'MATLAB BioMonitor Downloader');

if isfile(tempDestination)
    delete(tempDestination);
end

lastError = [];
for attempt = 1:3
    try
        if isfile(tempDestination)
            delete(tempDestination);
        end
        websave(tempDestination, url, options);
        movefile(tempDestination, destination, 'f');
        return;
    catch ME
        lastError = ME;
        pause(0.8 * attempt);
    end
end

escapedUrl = strrep(url, '''', '''''');
escapedTemp = strrep(tempDestination, '''', '''''');
psCommand = sprintf([ ...
    'powershell -NoProfile -Command "Invoke-WebRequest -Uri ''%s'' -OutFile ''%s''"'], ...
    escapedUrl, escapedTemp);
[status, cmdout] = system(psCommand);
if status == 0 && isfile(tempDestination)
    movefile(tempDestination, destination, 'f');
    return;
end

if ~isempty(lastError)
    error('下载失败: %s | powershell fallback: %s', lastError.message, strtrim(cmdout));
else
    error('下载失败: %s', strtrim(cmdout));
end
end
