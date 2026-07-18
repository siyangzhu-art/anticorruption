
clear; clc;

%% 设置路径
input_dir = 'C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\results';
output_dir = input_dir;
pattern = '(\d+):\s*\{''count'':\s*(\d+),\s*''avg_prob'':\s*([\d\.eE+-]+)\}';

%% 主处理流程：分别处理 plan 和 summarize 文件
fprintf('=== 开始处理数据 ===\n');

% 存储各来源的结果（省份和城市分别存储）
prov_cos_plan_all = table(); prov_js_plan_all = table();
prov_cos_sum_all = table(); prov_js_sum_all = table();
city_cos_plan_all = table(); city_js_plan_all = table();
city_cos_sum_all = table(); city_js_sum_all = table();

% 原始文件年份范围 2009-2019，但后续会将年份减一，所以此处读取年份不变
years = 2009:2019;

for yr = years
    %% 处理 plan 文件
    plan_file = fullfile(input_dir, sprintf('result%dplan.csv', yr));
    if exist(plan_file, 'file')
        fprintf('处理 plan 文件: %d 年...\n', yr);
        raw_plan = readtable(plan_file, 'VariableNamingRule', 'preserve');
        [p_cos, p_js, c_cos, c_js] = compute_metrics_for_year(raw_plan, yr, pattern);
        prov_cos_plan_all = [prov_cos_plan_all; p_cos];
        prov_js_plan_all  = [prov_js_plan_all; p_js];
        city_cos_plan_all = [city_cos_plan_all; c_cos];
        city_js_plan_all  = [city_js_plan_all; c_js];
    else
        warning('plan 文件缺失: %s', plan_file);
    end
    
    %% 处理 summarize 文件
    sum_file = fullfile(input_dir, sprintf('result%dsummarize.csv', yr));
    if exist(sum_file, 'file')
        fprintf('处理 summarize 文件: %d 年...\n', yr);
        raw_sum = readtable(sum_file, 'VariableNamingRule', 'preserve');
        [p_cos, p_js, c_cos, c_js] = compute_metrics_for_year(raw_sum, yr, pattern);
        prov_cos_sum_all = [prov_cos_sum_all; p_cos];
        prov_js_sum_all  = [prov_js_sum_all; p_js];
        city_cos_sum_all = [city_cos_sum_all; c_cos];
        city_js_sum_all  = [city_js_sum_all; c_js];
    else
        warning('summarize 文件缺失: %s', sum_file);
    end
end

%% 合并省份面板
if ~isempty(prov_cos_plan_all) && ~isempty(prov_js_plan_all) && ...
   ~isempty(prov_cos_sum_all) && ~isempty(prov_js_sum_all)
    prov_plan = innerjoin(prov_cos_plan_all, prov_js_plan_all, 'Keys', {'Year','Region'});
    prov_plan.Properties.VariableNames{'Cosine'} = 'Cosine_Plan';
    prov_plan.Properties.VariableNames{'JS'} = 'JS_Plan';
    
    prov_sum = innerjoin(prov_cos_sum_all, prov_js_sum_all, 'Keys', {'Year','Region'});
    prov_sum.Properties.VariableNames{'Cosine'} = 'Cosine_Summarize';
    prov_sum.Properties.VariableNames{'JS'} = 'JS_Summarize';
    
    prov_final = innerjoin(prov_plan, prov_sum, 'Keys', {'Year','Region'});
    prov_final.Properties.VariableNames{'Region'} = 'Province';
    prov_final = prov_final(:, {'Year','Province','Cosine_Plan','JS_Plan','Cosine_Summarize','JS_Summarize'});
    
    % ---------- 年份减一（2009→2008, 2010→2009, ..., 2019→2018）---------
    
    % --------------------------------------------------------------------
    
    prov_out = fullfile(output_dir, 'province_panel_full.xlsx');
    writetable(prov_final, prov_out);
    fprintf('省份面板已保存: %s (%d 条记录)\n', prov_out, height(prov_final));
else
    warning('省份数据不足，无法合并。请检查 plan/summarize 文件是否有效。');
end

%% 合并城市面板
if ~isempty(city_cos_plan_all) && ~isempty(city_js_plan_all) && ...
   ~isempty(city_cos_sum_all) && ~isempty(city_js_sum_all)
    city_plan = innerjoin(city_cos_plan_all, city_js_plan_all, 'Keys', {'Year','Region'});
    city_plan.Properties.VariableNames{'Cosine'} = 'Cosine_Plan';
    city_plan.Properties.VariableNames{'JS'} = 'JS_Plan';
    
    city_sum = innerjoin(city_cos_sum_all, city_js_sum_all, 'Keys', {'Year','Region'});
    city_sum.Properties.VariableNames{'Cosine'} = 'Cosine_Summarize';
    city_sum.Properties.VariableNames{'JS'} = 'JS_Summarize';
    
    city_final = innerjoin(city_plan, city_sum, 'Keys', {'Year','Region'});
    city_final.Properties.VariableNames{'Region'} = 'City';
    city_final = city_final(:, {'Year','City','Cosine_Plan','JS_Plan','Cosine_Summarize','JS_Summarize'});
    
    % ---------- 年份减一（2009→2008, 2010→2009, ..., 2019→2018）----------
    % --------------------------------------------------------------------
    
    city_out = fullfile(output_dir, 'city_panel_full.xlsx');
    writetable(city_final, city_out);
    fprintf('城市面板已保存: %s (%d 条记录)\n', city_out, height(city_final));
else
    warning('城市数据不足，无法合并。请检查 plan/summarize 文件是否有效。');
end

fprintf('=== 全部处理完成 ===\n');

%% ---------------------------------------------------------------------
%% 辅助函数定义（必须放在脚本末尾）

% 1. JS 散度计算函数（值域 [0,1]，0=完全相同）
function jsd = calc_js_div(p, q)
    m = (p + q) / 2;
    idx_p = (p > 0) & (m > 0);
    kl_pm = 0;
    if any(idx_p)
        kl_pm = sum(p(idx_p) .* log(p(idx_p) ./ m(idx_p)));
    end
    idx_q = (q > 0) & (m > 0);
    kl_qm = 0;
    if any(idx_q)
        kl_qm = sum(q(idx_q) .* log(q(idx_q) ./ m(idx_q)));
    end
    jsd = 0.5 * (kl_pm + kl_qm);
    jsd = jsd / log(2);
    jsd = max(0, min(1, jsd));
end

% 2. 从原始数据表计算给定年份的余弦相似度和 JS 散度
function [prov_cos, prov_js, city_cos, city_js] = compute_metrics_for_year(raw, year, pattern)
    var_names = raw.Properties.VariableNames;
    if length(var_names) >= 4
        if any(strcmp(var_names, 'x__'))
            year_col = 'x__';
            region_col = 'x__1';
            type_col = 'x__2';
            topic_col = 'x____';
        elseif any(strcmp(var_names, 'Year'))
            year_col = 'Year';
            region_col = 'Region';
            type_col = 'Type';
            topic_col = 'TopicDistribution';
        else
            year_col = 1;
            region_col = 2;
            type_col = 3;
            topic_col = 4;
        end
    else
        error('列数不足4，请检查文件格式。');
    end
    
    if ischar(year_col) || isstring(year_col)
        Year_data = raw.(year_col);
        Region_data = raw.(region_col);
        Type_data = raw.(type_col);
        TopicDist_data = raw.(topic_col);
    else
        Year_data = raw{:, year_col};
        Region_data = raw{:, region_col};
        Type_data = raw{:, type_col};
        TopicDist_data = raw{:, topic_col};
    end
    
    if isnumeric(Year_data); Year_data = num2cell(Year_data); end
    if iscategorical(Type_data); Type_data = cellstr(Type_data); end
    if iscategorical(Region_data); Region_data = cellstr(Region_data); end
    if ischar(TopicDist_data); TopicDist_data = cellstr(TopicDist_data); end
    if ~iscell(TopicDist_data); TopicDist_data = cellstr(TopicDist_data); end
    
    Year_list = []; Region_list = {}; Type_list = {};
    topic_id_list = []; topic_count_list = []; topic_avg_prob_list = [];
    n_rows = length(Year_data);
    for i = 1:n_rows
        year_val = Year_data{i};
        region_val = Region_data{i};
        type_val = char(Type_data{i});
        topic_str = TopicDist_data{i};
        if isempty(topic_str) || ~ischar(topic_str); continue; end
        tokens = regexp(topic_str, pattern, 'tokens');
        for j = 1:length(tokens)
            tok = tokens{j};
            if length(tok) >= 3
                Year_list = [Year_list; year_val];
                Region_list{end+1,1} = region_val;
                Type_list{end+1,1} = type_val;
                topic_id_list = [topic_id_list; str2double(tok{1})];
                topic_count_list = [topic_count_list; str2double(tok{2})];
                topic_avg_prob_list = [topic_avg_prob_list; str2double(tok{3})];
            end
        end
    end
    
    if isempty(Year_list)
        prov_cos = table(); prov_js = table(); city_cos = table(); city_js = table();
        return;
    end
    
    result_table = table(Year_list, Region_list, Type_list, ...
        topic_id_list, topic_count_list, topic_avg_prob_list, ...
        'VariableNames', {'Year','Region','Type','TopicID','Count','AvgProb'});
    
    [G,~] = findgroups(result_table.Year, result_table.Region, result_table.Type);
    total_counts = splitapply(@sum, result_table.Count, G);
    result_table.TotalCount = total_counts(G);
    result_table.Proportion = result_table.Count ./ result_table.TotalCount;
    
    central_data = result_table(strcmp(result_table.Type,'中央'),:);
    province_data = result_table(strcmp(result_table.Type,'省份'),:);
    city_data = result_table(strcmp(result_table.Type,'城市'),:);
    all_topics = unique(result_table.TopicID)';
    
    central_vec = zeros(length(all_topics),1);
    central_valid = false;
    central_year = central_data(central_data.Year == year, :);
    if ~isempty(central_year)
        for i = 1:length(all_topics)
            idx = central_year.TopicID == all_topics(i);
            if any(idx)
                central_vec(i) = central_year.Proportion(idx);
            end
        end
        s = sum(central_vec);
        if s > 0
            central_vec = central_vec / s;
            central_valid = true;
        end
    end
    
    prov_names = unique(province_data.Region)';
    prov_cos = table(); prov_js = table();
    for p = 1:length(prov_names)
        pname = prov_names{p};
        prov_vec = zeros(length(all_topics),1);
        prov_rows = province_data(strcmp(province_data.Region, pname), :);
        if isempty(prov_rows)
            cos_val = NaN; js_val = NaN;
        else
            for i = 1:length(all_topics)
                idx = prov_rows.TopicID == all_topics(i);
                if any(idx)
                    prov_vec(i) = prov_rows.Proportion(idx);
                end
            end
            s = sum(prov_vec);
            if s > 0; prov_vec = prov_vec / s; end
            if ~central_valid || norm(central_vec) < eps || norm(prov_vec) < eps
                cos_val = 0;
            else
                cos_val = dot(central_vec, prov_vec) / (norm(central_vec)*norm(prov_vec));
            end
            if ~central_valid || norm(central_vec) < eps || norm(prov_vec) < eps
                js_val = NaN;
            else
                js_val = calc_js_div(central_vec, prov_vec);
            end
        end
        prov_cos = [prov_cos; table(year, {pname}, cos_val, ...
            'VariableNames', {'Year','Region','Cosine'})];
        prov_js  = [prov_js;  table(year, {pname}, js_val, ...
            'VariableNames', {'Year','Region','JS'})];
    end
    
    if ~central_valid
        city_names = unique(city_data.Region)';
        city_cos = table(); city_js = table();
        for c = 1:length(city_names)
            cname = city_names{c};
            city_cos = [city_cos; table(year, {cname}, NaN, ...
                'VariableNames', {'Year','Region','Cosine'})];
            city_js  = [city_js;  table(year, {cname}, NaN, ...
                'VariableNames', {'Year','Region','JS'})];
        end
    else
        city_names = unique(city_data.Region)';
        city_cos = table(); city_js = table();
        for c = 1:length(city_names)
            cname = city_names{c};
            city_vec = zeros(length(all_topics),1);
            city_rows = city_data(strcmp(city_data.Region, cname), :);
            if isempty(city_rows)
                cos_val = NaN; js_val = NaN;
            else
                for i = 1:length(all_topics)
                    idx = city_rows.TopicID == all_topics(i);
                    if any(idx)
                        city_vec(i) = city_rows.Proportion(idx);
                    end
                end
                s = sum(city_vec);
                if s > 0; city_vec = city_vec / s; end
                if norm(city_vec) < eps
                    cos_val = 0; js_val = NaN;
                else
                    cos_val = dot(central_vec, city_vec) / (norm(central_vec)*norm(city_vec));
                    js_val = calc_js_div(central_vec, city_vec);
                end
            end
            city_cos = [city_cos; table(year, {cname}, cos_val, ...
                'VariableNames', {'Year','Region','Cosine'})];
            city_js  = [city_js;  table(year, {cname}, js_val, ...
                'VariableNames', {'Year','Region','JS'})];
        end
    end
end
