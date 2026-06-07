function result = smoke_test()
%SMOKE_TEST Validate downloads, parsing, algorithms, and temperature stream.

projectRoot = fileparts(mfilename('fullpath'));
addpath(genpath(fullfile(projectRoot, 'src')));

plan = bioio.getRandomDatasetPlan("abnormal", projectRoot);
bundle = bioio.loadPreparedMonitoringData(projectRoot, plan);
manifest = bundle.manifest;
ecg = bundle.ecg;
resp = bundle.resp;

tempStream = tempsrc.TemperatureStream("demo", struct());
tempValues = nan(12, 1);
for k = 1:numel(tempValues)
    tempValues(k) = tempStream.next("body");
end
delete(tempStream);

result = struct();
result.summary = sprintf( ...
    'ECG peaks=%d, meanHR=%.2f bpm, Resp peaks=%d, meanRR=%.2f bpm, Temp mean=%.2f C', ...
    numel(ecg.rLocs), mean(ecg.heartRate, 'omitnan'), ...
    numel(resp.peakLocs), mean(resp.respRate, 'omitnan'), ...
    mean(tempValues, 'omitnan'));
result.ecgSNRdB = ecg.snrDb;
result.respSNRdB = resp.snrDb;
result.plan = plan;
result.downloadCount = manifest.downloadCount;
result.ecgLead = ecg.leadName;
result.respChannel = resp.channelName;
result.tempRange = [min(tempValues, [], 'omitnan'), max(tempValues, [], 'omitnan')];

disp(sprintf('Random ECG=%s, Random Resp=%s, Mode=%s, Downloads=%d, ECG cache=%d, Resp cache=%d', ...
    plan.ecgRecord, plan.respRecord, plan.mode, manifest.downloadCount, ...
    bundle.ecgCacheHit, bundle.respCacheHit));
disp(result.summary);
end
