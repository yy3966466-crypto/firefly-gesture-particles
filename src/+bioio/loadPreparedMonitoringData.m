function bundle = loadPreparedMonitoringData(projectRoot, plan)
%LOADPREPAREDMONITORINGDATA Prepare dataset files and cache processed results.

manifest = bioio.ensurePublicDatasets(projectRoot, plan);
cacheFolder = fullfile(projectRoot, 'data', 'cache');
if ~isfolder(cacheFolder)
    mkdir(cacheFolder);
end

ecgCacheFile = fullfile(cacheFolder, sprintf('ecg_%s_lead1.mat', plan.ecgRecord));
respCacheFile = fullfile(cacheFolder, sprintf('resp_%s.mat', plan.respRecord));

ecgCacheHit = isfile(ecgCacheFile);
respCacheHit = isfile(respCacheFile);

if ecgCacheHit
    ecgData = load(ecgCacheFile, 'ecg');
    ecg = ecgData.ecg;
else
    ecgRecord = bioio.loadMitdbRecord(manifest.mitdbFolder, plan.ecgRecord, 1);
    ecg = bioalg.processEcg(ecgRecord.signal, ecgRecord.fs);
    ecg.recordName = ecgRecord.recordName;
    ecg.leadName = ecgRecord.leadName;
    save(ecgCacheFile, 'ecg');
end

if respCacheHit
    respData = load(respCacheFile, 'resp');
    resp = respData.resp;
else
    respRecord = bioio.loadBidmcRespiration(manifest.bidmcFolder, plan.respRecord);
    resp = bioalg.processRespiration(respRecord.signal, respRecord.fs);
    resp.recordId = respRecord.recordId;
    resp.channelName = respRecord.channelName;
    save(respCacheFile, 'resp');
end

bundle = struct();
bundle.manifest = manifest;
bundle.ecg = ecg;
bundle.resp = resp;
bundle.ecgCacheHit = ecgCacheHit;
bundle.respCacheHit = respCacheHit;
bundle.cacheFolder = cacheFolder;
end
