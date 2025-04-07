clc;
clear;

spike_matrix = load("111-20_spike_matrix.csv");
original_time_record = load("111-20_time_record.csv");
total_neuron_number = 20;

time_record = original_time_record - original_time_record(1); % unit: milliseconds
[time, buff] = size(time_record);

figure('Position', [100 100 1800 900])
tiledlayout(4, 5, 'Padding','compact', 'TileSpacing','compact');
for j=1:total_neuron_number
    nexttile
    for i =1:time
        if spike_matrix(j,i) ~= 0
            plot([time_record(i) time_record(i)], [0 1], 'Color', 'black', LineWidth=2)
            hold on
        end
    end
    xlim([0,max(time_record)]);
    ylim([0,1.5]);
    box on;
    set(gca, 'fontsize', 12, 'fontweight', 'bold');
    str = sprintf('Neuron %d',j);
    ylabel('Spike', FontSize=12, FontWeight='bold');
    xlabel('Time [ms]', FontSize=12, FontWeight='bold');
    title(str, FontSize=12, FontWeight='bold');
end