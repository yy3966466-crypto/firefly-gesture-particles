function report = export_analysis_report(mode)
%EXPORT_ANALYSIS_REPORT Export ECG/respiration comparison figures and data.

if nargin < 1 || strlength(string(mode)) == 0
    mode = "abnormal";
end

projectRoot = fileparts(mfilename('fullpath'));
addpath(genpath(fullfile(projectRoot, 'src')));

plan = bioio.getRandomDatasetPlan(mode, projectRoot);
bundle = bioio.loadPreparedMonitoringData(projectRoot, plan);
report = bioout.exportAnalysisReport(projectRoot, bundle, plan);

disp("分析图和数据已导出到:");
disp(report.outputFolder);
end
