function filtered = bandpassSignal(signal, fs, passband)
%BANDPASSSIGNAL Zero-phase band-pass filter with smooth IIR response.
%   Uses Butterworth + filtfilt for ripple-free output.
%   Falls back to tapered-FFT filter if Signal Processing Toolbox unavailable.

signal = signal(:);
passband = sort(passband(:).');
passband(1) = max(passband(1), 0.01);
passband(2) = min(passband(2), fs / 2 - 0.01);

try
    nyquist = fs / 2;
    Wn = passband / nyquist;
    [b, a] = butter(4, Wn, 'bandpass');
    filtered = filtfilt(b, a, signal);
catch
    % Graceful fallback: FFT filter with smooth taper to reduce ringing
    sampleCount = numel(signal);
    fftSignal = fft(signal);
    freqAxis = (0:(sampleCount - 1)).' .* (fs / sampleCount);

    taperHz = 1.0;
    mask = zeros(size(freqAxis));
    for k = 1:numel(freqAxis)
        f = min(freqAxis(k), fs - freqAxis(k));
        lo = passband(1); hi = passband(2);
        if f >= lo && f <= hi
            mask(k) = 1;
        elseif f < lo
            d = min(1, (lo - f) / max(taperHz, 0.1));
            mask(k) = (1 - d) .^ 2;
        else
            d = min(1, (f - hi) / max(taperHz, 0.1));
            mask(k) = (1 - d) .^ 2;
        end
    end

    fftSignal = fftSignal .* mask;
    filtered = real(ifft(fftSignal));
end
end
