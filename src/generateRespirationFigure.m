%% Generate respiration signal comparison figure (before/after ALE)
% For Section 4.2.3 Figure 4.5

clear; close all;

% Load processed respiration data
data = load('../data/cache/resp_01.mat');
resp = data.resp;

fs = double(resp.fs);
t = double(resp.t);
raw = double(resp.raw);
bandpassed = double(resp.bandpassed);
enhanced = double(resp.enhanced);
peakLocs = double(resp.peakLocs);

% Select a 10-second window for clear visualization
windowLen = 10; % seconds
startTime = 10; % start at 10s to avoid transient
startIdx = find(t >= startTime, 1);
endIdx = min(startIdx + windowLen * fs - 1, length(t));

idxRange = startIdx:endIdx;
t_win = t(idxRange);
raw_win = raw(idxRange);
bandpassed_win = bandpassed(idxRange);
enhanced_win = enhanced(idxRange);

% Find peaks within window
peakIdxInWin = peakLocs(peakLocs >= startIdx & peakLocs <= endIdx);
peakTimes = t(peakIdxInWin);

% Create figure
figure('Position', [100, 100, 1200, 700], 'Color', 'w');

% Subplot 1: Raw respiratory signal
subplot(3, 1, 1);
plot(t_win, raw_win, 'k-', 'LineWidth', 0.8);
ylabel('Amplitude (a.u.)', 'FontSize', 11);
title('Original Respiratory Signal', 'FontSize', 12, 'FontWeight', 'bold');
set(gca, 'FontSize', 10, 'FontName', 'Times New Roman');
grid on;
xlim([t_win(1), t_win(end)]);
ylim([min(raw_win) - 0.05 * range(raw_win), max(raw_win) + 0.05 * range(raw_win)]);

% Subplot 2: Bandpassed signal (pre-ALE)
subplot(3, 1, 2);
plot(t_win, bandpassed_win, 'b-', 'LineWidth', 0.8);
ylabel('Amplitude (a.u.)', 'FontSize', 11);
title('Bandpass Filtered (0.08–0.80 Hz)', 'FontSize', 12, 'FontWeight', 'bold');
set(gca, 'FontSize', 10, 'FontName', 'Times New Roman');
grid on;
xlim([t_win(1), t_win(end)]);
ylim([min(bandpassed_win) - 0.05 * range(bandpassed_win), max(bandpassed_win) + 0.05 * range(bandpassed_win)]);

% Subplot 3: ALE-enhanced signal
subplot(3, 1, 3);
plot(t_win, enhanced_win, 'r-', 'LineWidth', 0.8);
hold on;
% Mark detected peaks
for pi = 1:length(peakTimes)
    if peakTimes(pi) >= t_win(1) && peakTimes(pi) <= t_win(end)
        peakVal = enhanced(peakLocs(peakLocs == find(t == peakTimes(pi), 1)));
        if isempty(peakVal)
            % Find nearest index
            [~, nearestIdx] = min(abs(t - peakTimes(pi)));
            peakVal = enhanced(nearestIdx);
        end
        % Get the value at this peak
        [~, peakTIdx] = min(abs(t - peakTimes(pi)));
        plot(peakTimes(pi), enhanced(peakTIdx), 'k^', 'MarkerFaceColor', 'k', 'MarkerSize', 6);
    end
end
hold off;
xlabel('Time (s)', 'FontSize', 11);
ylabel('Amplitude (a.u.)', 'FontSize', 11);
title('ALE-Enhanced Signal with Detected Peaks (▼)', 'FontSize', 12, 'FontWeight', 'bold');
set(gca, 'FontSize', 10, 'FontName', 'Times New Roman');
grid on;
xlim([t_win(1), t_win(end)]);
ylim([min(enhanced_win) - 0.05 * range(enhanced_win), max(enhanced_win) + 0.05 * range(enhanced_win)]);

% Print SNR info
snrVal = double(resp.snrDb);
fprintf('SNR = %.2f dB\n', snrVal);

% Save as high-res PNG
exportgraphics(gcf, '../fig_respiration_comparison.png', 'Resolution', 300);
fprintf('Saved to fig_respiration_comparison.png\n');

% Also save as TIFF for Word
exportgraphics(gcf, '../fig_respiration_comparison.tif', 'Resolution', 300);
fprintf('Saved to fig_respiration_comparison.tif\n');

close;
