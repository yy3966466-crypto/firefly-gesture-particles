function snrDb = estimateSnr(rawSignal, cleanedSignal)
%ESTIMATESNR Crude signal-quality estimate from residual energy.

rawSignal = rawSignal(:);
cleanedSignal = cleanedSignal(:);
residual = rawSignal - cleanedSignal;
signalPower = mean(cleanedSignal .^ 2, 'omitnan');
noisePower = mean(residual .^ 2, 'omitnan');
snrDb = 10 * log10((signalPower + eps) / (noisePower + eps));
end
