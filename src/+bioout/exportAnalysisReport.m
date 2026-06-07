function report = exportAnalysisReport(projectRoot, bundle, plan)
%EXPORTANALYSISREPORT Export ECG/respiration comparison figures and data.

if nargin < 3 || isempty(plan)
    plan = struct();
end

ecg = bundle.ecg;
resp = bundle.resp;

outputRoot = fullfile(projectRoot, 'output', 'analysis');
if ~isfolder(outputRoot)
    mkdir(outputRoot);
end

stamp = char(datetime('now', 'Format', 'yyyyMMdd_HHmmss'));
folderName = sprintf('report_%s_ecg_%s_resp_%s', ...
    stamp, ecg.recordName, resp.recordId);
outputFolder = fullfile(outputRoot, folderName);
if ~isfolder(outputFolder)
    mkdir(outputFolder);
end

ecgWindow = localRepresentativeWindow(ecg.heartRateTimes, ecg.heartRate, ecg.fs, numel(ecg.raw), 10);
respWindow = localRepresentativeWindow(resp.respRateTimes, resp.respRate, resp.fs, numel(resp.raw), 30);

localExportEcgComparison(ecg, ecgWindow, outputFolder);
localExportRespComparison(resp, respWindow, outputFolder);

ecgExcerpt = localBuildEcgExcerptTable(ecg, ecgWindow);
respExcerpt = localBuildRespExcerptTable(resp, respWindow);
summaryTable = localBuildSummaryTable(ecg, resp, plan);

writetable(ecgExcerpt, fullfile(outputFolder, 'ecg_excerpt.csv'));
writetable(respExcerpt, fullfile(outputFolder, 'respiration_excerpt.csv'));
writetable(summaryTable, fullfile(outputFolder, 'signal_summary.csv'));

localWriteReadme(outputFolder, ecg, resp, plan, ecgWindow, respWindow);

report = struct();
report.outputFolder = outputFolder;
report.summaryFile = fullfile(outputFolder, 'signal_summary.csv');
report.ecgExcerptFile = fullfile(outputFolder, 'ecg_excerpt.csv');
report.respExcerptFile = fullfile(outputFolder, 'respiration_excerpt.csv');
report.figureFiles = { ...
    fullfile(outputFolder, 'ecg_before_after.png'), ...
    fullfile(outputFolder, 'ecg_rwave_detection.png'), ...
    fullfile(outputFolder, 'resp_before_after.png'), ...
    fullfile(outputFolder, 'resp_peak_detection.png')};
end

function localExportEcgComparison(ecg, idx, outputFolder)
t = ecg.t(idx);
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100, 100, 1180, 760]);
tl = tiledlayout(fig, 2, 1, 'Padding', 'compact', 'TileSpacing', 'compact');

ax1 = nexttile(tl, 1);
plot(ax1, t, ecg.raw(idx), 'Color', [0.45, 0.45, 0.45], 'LineWidth', 1.0);
hold(ax1, 'on');
plot(ax1, t, ecg.filtered(idx), 'Color', [0.00, 0.37, 0.82], 'LineWidth', 1.2);
hold(ax1, 'off');
grid(ax1, 'on');
title(ax1, sprintf('ECG处理前后对比 - MIT-BIH Record %s', ecg.recordName));
xlabel(ax1, '时间 / s');
ylabel(ax1, '幅值 / mV');
legend(ax1, {'原始ECG', '滤波后ECG'}, 'Location', 'best');

ax2 = nexttile(tl, 2);
plot(ax2, t, ecg.diffEnvelope(idx), 'Color', [0.10, 0.52, 0.20], 'LineWidth', 1.1);
hold(ax2, 'on');
plot(ax2, t, ecg.threshold(idx), '--', 'Color', [0.82, 0.18, 0.15], 'LineWidth', 1.0);
hold(ax2, 'off');
grid(ax2, 'on');
title(ax2, '差分包络与自适应阈值');
xlabel(ax2, '时间 / s');
ylabel(ax2, '幅值');
legend(ax2, {'差分包络', '检测阈值'}, 'Location', 'best');

exportgraphics(fig, fullfile(outputFolder, 'ecg_before_after.png'), 'Resolution', 180);
close(fig);

peakMask = ecg.rLocs >= idx(1) & ecg.rLocs <= idx(end);
peakLocs = ecg.rLocs(peakMask);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100, 100, 1180, 450]);
ax = axes(fig);
plot(ax, t, ecg.filtered(idx), 'Color', [0.00, 0.37, 0.82], 'LineWidth', 1.2);
hold(ax, 'on');
scatter(ax, ecg.t(peakLocs), ecg.filtered(peakLocs), 36, [0.89, 0.19, 0.16], 'filled');
hold(ax, 'off');
grid(ax, 'on');
title(ax, sprintf('R波检测结果 - Record %s', ecg.recordName));
xlabel(ax, '时间 / s');
ylabel(ax, '滤波后幅值 / mV');
legend(ax, {'滤波后ECG', 'R波位置'}, 'Location', 'best');

exportgraphics(fig, fullfile(outputFolder, 'ecg_rwave_detection.png'), 'Resolution', 180);
close(fig);
end

function localExportRespComparison(resp, idx, outputFolder)
t = resp.t(idx);
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100, 100, 1180, 760]);
tl = tiledlayout(fig, 2, 1, 'Padding', 'compact', 'TileSpacing', 'compact');

ax1 = nexttile(tl, 1);
plot(ax1, t, resp.raw(idx), 'Color', [0.45, 0.45, 0.45], 'LineWidth', 1.0);
hold(ax1, 'on');
plot(ax1, t, resp.enhanced(idx), 'Color', [0.08, 0.55, 0.25], 'LineWidth', 1.2);
hold(ax1, 'off');
grid(ax1, 'on');
title(ax1, sprintf('呼吸信号处理前后对比 - BIDMC Record %s', resp.recordId));
xlabel(ax1, '时间 / s');
ylabel(ax1, '幅值');
legend(ax1, {'原始呼吸', '增强后呼吸'}, 'Location', 'best');

ax2 = nexttile(tl, 2);
plot(ax2, t, resp.bandpassed(idx), 'Color', [0.20, 0.40, 0.70], 'LineWidth', 1.0);
hold(ax2, 'on');
plot(ax2, t, resp.threshold(idx), '--', 'Color', [0.82, 0.18, 0.15], 'LineWidth', 1.0);
hold(ax2, 'off');
grid(ax2, 'on');
title(ax2, '带通后信号与检测阈值');
xlabel(ax2, '时间 / s');
ylabel(ax2, '幅值');
legend(ax2, {'带通/去基线后', '峰值阈值'}, 'Location', 'best');

exportgraphics(fig, fullfile(outputFolder, 'resp_before_after.png'), 'Resolution', 180);
close(fig);

peakMask = resp.peakLocs >= idx(1) & resp.peakLocs <= idx(end);
peakLocs = resp.peakLocs(peakMask);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100, 100, 1180, 450]);
ax = axes(fig);
plot(ax, t, resp.enhanced(idx), 'Color', [0.08, 0.55, 0.25], 'LineWidth', 1.2);
hold(ax, 'on');
scatter(ax, resp.t(peakLocs), resp.enhanced(peakLocs), 34, [0.90, 0.63, 0.07], 'filled');
hold(ax, 'off');
grid(ax, 'on');
title(ax, sprintf('呼吸峰检测结果 - Record %s', resp.recordId));
xlabel(ax, '时间 / s');
ylabel(ax, '增强后幅值');
legend(ax, {'增强后呼吸', '呼吸峰'}, 'Location', 'best');

exportgraphics(fig, fullfile(outputFolder, 'resp_peak_detection.png'), 'Resolution', 180);
close(fig);
end

function tbl = localBuildEcgExcerptTable(ecg, idx)
isPeak = ismember(idx(:), ecg.rLocs);
tbl = table( ...
    ecg.t(idx), ...
    ecg.raw(idx), ...
    ecg.filtered(idx), ...
    ecg.diffEnvelope(idx), ...
    ecg.threshold(idx), ...
    isPeak, ...
    'VariableNames', {'time_s', 'raw_ecg', 'filtered_ecg', 'diff_envelope', 'threshold', 'is_r_peak'});
end

function tbl = localBuildRespExcerptTable(resp, idx)
isPeak = ismember(idx(:), resp.peakLocs);
tbl = table( ...
    resp.t(idx), ...
    resp.raw(idx), ...
    resp.bandpassed(idx), ...
    resp.enhanced(idx), ...
    resp.threshold(idx), ...
    isPeak, ...
    'VariableNames', {'time_s', 'raw_resp', 'bandpassed_resp', 'enhanced_resp', 'threshold', 'is_resp_peak'});
end

function tbl = localBuildSummaryTable(ecg, resp, plan)
if nargin < 3 || isempty(plan)
    modeText = "";
else
    modeText = string(plan.mode);
end

signalName = {'ECG'; 'Respiration'};
databaseName = {'MIT-BIH Arrhythmia Database'; 'BIDMC PPG and Respiration Dataset'};
recordId = {ecg.recordName; resp.recordId};
fs = [ecg.fs; resp.fs];
durationSec = [ecg.t(end); resp.t(end)];
snrDb = [ecg.snrDb; resp.snrDb];
eventCount = [numel(ecg.rLocs); numel(resp.peakLocs)];
meanRate = [mean(ecg.heartRate, 'omitnan'); mean(resp.respRate, 'omitnan')];
stdRate = [std(ecg.heartRate, 'omitnan'); std(resp.respRate, 'omitnan')];
minRate = [min(ecg.heartRate); min(resp.respRate)];
maxRate = [max(ecg.heartRate); max(resp.respRate)];
modeColumn = repmat(modeText, 2, 1);

tbl = table(signalName, databaseName, recordId, fs, durationSec, snrDb, ...
    eventCount, meanRate, stdRate, minRate, maxRate, modeColumn, ...
    'VariableNames', {'signal_type', 'database_name', 'record_id', 'fs_hz', ...
    'duration_s', 'snr_db', 'event_count', 'mean_rate_bpm', 'std_rate_bpm', ...
    'min_rate_bpm', 'max_rate_bpm', 'sampling_mode'});
end

function localWriteReadme(outputFolder, ecg, resp, plan, ecgWindow, respWindow)
lines = strings(0, 1);
lines(end + 1) = "多生理参数监护系统分析导出";
lines(end + 1) = " ";
lines(end + 1) = "数据库来源:";
lines(end + 1) = "1. MIT-BIH Arrhythmia Database (ECG)";
lines(end + 1) = "2. BIDMC PPG and Respiration Dataset (Respiration)";
lines(end + 1) = " ";
lines(end + 1) = "本次记录:";
lines(end + 1) = "ECG Record: " + string(ecg.recordName) + " (" + string(ecg.leadName) + ")";
lines(end + 1) = "Resp Record: " + string(resp.recordId) + " (" + string(resp.channelName) + ")";
if nargin >= 4 && ~isempty(plan)
    lines(end + 1) = "抽样模式: " + string(plan.mode);
end
lines(end + 1) = " ";
lines(end + 1) = "导出文件:";
lines(end + 1) = "- ecg_before_after.png: 心电处理前后对比图";
lines(end + 1) = "- ecg_rwave_detection.png: R波检测结果图";
lines(end + 1) = "- resp_before_after.png: 呼吸信号处理前后对比图";
lines(end + 1) = "- resp_peak_detection.png: 呼吸峰检测结果图";
lines(end + 1) = "- signal_summary.csv: 指标汇总表";
lines(end + 1) = "- ecg_excerpt.csv: ECG局部窗口数据";
lines(end + 1) = "- respiration_excerpt.csv: 呼吸局部窗口数据";
lines(end + 1) = " ";
lines(end + 1) = sprintf('ECG对比窗口: %.2f s - %.2f s', ecg.t(ecgWindow(1)), ecg.t(ecgWindow(end)));
lines(end + 1) = sprintf('Resp对比窗口: %.2f s - %.2f s', resp.t(respWindow(1)), resp.t(respWindow(end)));

fid = fopen(fullfile(outputFolder, 'README.txt'), 'w');
cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
for idx = 1:numel(lines)
    fprintf(fid, '%s\n', lines(idx));
end
end

function idx = localRepresentativeWindow(rateTimes, rates, fs, signalLength, windowSeconds)
windowSamples = min(signalLength, max(1, round(windowSeconds * fs)));

if isempty(rateTimes) || isempty(rates)
    centerSample = min(signalLength, max(1, round(signalLength / 2)));
else
    deviations = abs(rates - median(rates, 'omitnan'));
    deviations(isnan(deviations)) = -inf;
    [~, bestIdx] = max(deviations);
    if isnan(bestIdx) || bestIdx < 1
        centerSample = min(signalLength, max(1, round(signalLength / 2)));
    else
        centerTime = rateTimes(bestIdx);
        centerSample = min(signalLength, max(1, round(centerTime * fs) + 1));
    end
end

startIdx = max(1, centerSample - floor(windowSamples / 2));
endIdx = min(signalLength, startIdx + windowSamples - 1);
startIdx = max(1, endIdx - windowSamples + 1);
idx = startIdx:endIdx;
end
