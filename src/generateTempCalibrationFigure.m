%% Generate temperature calibration comparison figure (图4.7)
% Based on processTemperature.m calibration model

clear; close all;

% Simulate calibration data (replace with actual measured values)
T_ref = [35; 37; 39];          % Standard temperatures
V_out = [1.652; 1.548; 1.453]; % Measured voltages (replace with real data)

% Least-squares linear fit: same as processTemperature.m
V_mat = [V_out, ones(size(V_out))];
coeff = V_mat \ T_ref;
k = coeff(1); b = coeff(2);
T_fit = k * V_out + b;
calError = max(abs(T_fit - T_ref));

fprintf('k = %.4f, b = %.4f\n', k, b);
fprintf('Max residual = %.4f °C\n', calError);

% Dense curve for plotting
V_dense = linspace(min(V_out)-0.02, max(V_out)+0.02, 100);
T_dense = k * V_dense + b;

% Create figure
figure('Position', [100, 100, 900, 400], 'Color', 'w');

% Left: Calibration curve
subplot(1, 2, 1);
plot(V_out, T_ref, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r'); hold on;
plot(V_dense, T_dense, 'b-', 'LineWidth', 1.5);
xlabel('Sensor Output Voltage (V)', 'FontSize', 11);
ylabel('Temperature (°C)', 'FontSize', 11);
title('Linear Calibration Curve', 'FontSize', 12, 'FontWeight', 'bold');
legend('Calibration Points', sprintf('T = %.1f×V + %.1f', k, b), 'Location', 'northwest');
grid on; set(gca, 'FontSize', 10, 'FontName', 'Times New Roman');

% Right: Residuals
subplot(1, 2, 2);
bar(T_ref, T_fit - T_ref, 0.4, 'FaceColor', [0.3 0.5 0.8]); hold on;
plot(T_ref, zeros(size(T_ref)), 'k-', 'LineWidth', 0.8);
plot(T_ref, 0.1*ones(size(T_ref)), 'r--', 'LineWidth', 0.8);
plot(T_ref, -0.1*ones(size(T_ref)), 'r--', 'LineWidth', 0.8);
xlabel('Reference Temperature (°C)', 'FontSize', 11);
ylabel('Residual (°C)', 'FontSize', 11);
title(sprintf('Residuals (Max = %.4f°C)', calError), 'FontSize', 12, 'FontWeight', 'bold');
legend('Residual', 'Zero line', '±0.1°C', 'Location', 'best');
grid on; set(gca, 'FontSize', 10, 'FontName', 'Times New Roman');

% Print
exportgraphics(gcf, 'fig_temp_calibration_matlab.png', 'Resolution', 300);
fprintf('Saved fig_temp_calibration_matlab.png\n');
