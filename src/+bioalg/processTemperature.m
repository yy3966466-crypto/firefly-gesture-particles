function result = processTemperature(signal, fs, varargin)
%PROCESSTEMPERATURE Temperature signal filtering and calibration.
%   result = PROCESSTEMPERATURE(signal, fs) applies FIR low-pass filtering
%   to the temperature signal.
%
%   result = PROCESSTEMPERATURE(signal, fs, 'calibrate', true, ...
%       'calPoints', [35,37,39], 'calVoltages', [V35, V37, V39])
%   also performs linear calibration (T = k*V + b) using the given
%   calibration points.
%
%   Returns struct with fields:
%     .raw        - raw input signal
%     .filtered   - low-pass filtered signal
%     .filtFilt   - zero-phase low-pass filtered (filtfilt)
%     .k, .b      - calibration coefficients (if calibrate=true)
%     .calibrated - calibrated temperature (if calibrate=true)

    p = inputParser;
    addRequired(p, 'signal', @(x) isnumeric(x) && isvector(x));
    addRequired(p, 'fs', @(x) isscalar(x) && x > 0);
    addParameter(p, 'calibrate', false, @islogical);
    addParameter(p, 'calPoints', [35, 37, 39], @(x) isnumeric(x) && numel(x) >= 2);
    addParameter(p, 'calVoltages', [], @(x) isnumeric(x) && numel(x) >= 2);
    parse(p, signal, fs, varargin{:});

    signal = signal(:);
    result.raw = signal;

    % ---- FIR Low-Pass Filter ----
    % Cutoff: 0.05 Hz (体温为准静态信号)
    % Order: 20 (sufficient for gentle roll-off)
    filterOrder = 20;
    cutoffHz = 0.05;
    nyquist = fs / 2;

    if cutoffHz < nyquist
        % Design FIR low-pass using Hamming window
        coeffs = fir1(filterOrder, cutoffHz / nyquist, 'low', hamming(filterOrder + 1));
        result.filtered = filter(coeffs, 1, signal);
        result.filtFilt = filtfilt(coeffs, 1, signal);  % zero-phase
    else
        % Cutoff above Nyquist → no filtering needed
        result.filtered = signal;
        result.filtFilt = signal;
    end

    result.fs = fs;
    result.filterOrder = filterOrder;
    result.cutoffHz = cutoffHz;

    % ---- Linear Calibration ----
    if p.Results.calibrate && ~isempty(p.Results.calVoltages)
        calT = p.Results.calPoints(:);
        calV = p.Results.calVoltages(:);

        if length(calT) ~= length(calV)
            warning('Calibration points and voltages must have same length. Skipping calibration.');
            result.k = NaN;
            result.b = NaN;
            result.calibrated = result.filtFilt;
        else
            % Least-squares linear fit: T = k * V + b
            Vavg = [calV, ones(size(calV))];
            coeff = Vavg \ calT;
            result.k = coeff(1);
            result.b = coeff(2);

            % Apply calibration to filtered output (not raw signal)
            result.calibrated = result.k * result.filtFilt + result.b;

            % Compute residual error at calibration points
            T_fit = result.k * calV + result.b;
            result.calError = max(abs(T_fit - calT));
        end
    elseif p.Results.calibrate
        warning('calVoltages not provided. Skipping calibration.');
        result.k = NaN;
        result.b = NaN;
        result.calibrated = result.filtFilt;
    end

    % ---- Metrics ----
    result.snrDb = bioalg.estimateSnr(signal, result.filtFilt);
    if ~isnan(result.snrDb) && isfinite(result.snrDb)
        noiseStd = std(signal - result.filtFilt, 'omitnan');
        result.noiseEstimate = noiseStd;
    else
        result.noiseEstimate = NaN;
    end
end
