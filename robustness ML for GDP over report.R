rm(list = ls())
library(grf)
library(xgboost)
library(haven)
library(e1071)  # 用于支持向量机 (SVR)
library(earth)  # 用于多元自适应回归样条 (MARS)
library(nlme)
library(mgcv)   # 用于广义加性模型 (GAM)

# 1. 读取数据与清洗
df <- read_dta("C:/Users/siyang zhu/Desktop/Anti-corruption/proposition1/forcontdid.dta")

df$row_id <- 1:nrow(df) # 记录原始行号用于最后对齐

# 筛选核心变量无缺失值的完整样本
idx <- !is.na(df$growth_gdp) & 
  !is.na(df$growth_realgdp) & 
  !is.na(df$growth_night)

df_comp <- df[idx, ]

# 提取特征矩阵 X 和因变量 Y
X <- as.matrix(df_comp[, "growth_realgdp", drop = FALSE])
Y <- as.numeric(df_comp$growth_gdp)
N <- nrow(df_comp)

# ==================== 2. Regression Forest (自带 OOB 机制) ====================
print("正在运行基准模型：Regression Forest...")
rf <- regression_forest(X = X, Y = Y, num.trees = 2000, seed = 42)

# grf 默认预测值即为袋外（Out-of-Bag）预测，天然免受过拟合干扰
df_comp$m_hat_rf  <- predict(rf)$predictions
df_comp$f_hat_rf  <- Y - df_comp$m_hat_rf


# ==================== 3. 5折交叉拟合 (Cross-Fitting) 模块 ====================
print("正在构建 5折交叉拟合：XGBoost, SVR, MARS, GAM...")

# 初始化样本外预测向量容器
df_comp$m_hat_xgb  <- NA
df_comp$m_hat_svm  <- NA
df_comp$m_hat_mars <- NA
df_comp$m_hat_gam  <- NA

# 生成 5 折交叉验证标签
set.seed(42)
folds <- sample(rep(1:5, length.out = N))

# 开始交叉拟合循环
for (k in 1:5) {
  cat(sprintf("--> 正在处理第 %d / 5 折...\n", k))
  
  train_idx <- which(folds != k)
  test_idx  <- which(folds == k)
  
  # 提取训练集与测试集
  X_train <- X[train_idx, , drop = FALSE]
  Y_train <- Y[train_idx]
  X_test  <- X[test_idx, , drop = FALSE]
  
  # 数据框格式（供 GAM 模型使用）
  train_df <- data.frame(Y = Y_train, growth_night = X_train[, 1])
  test_df  <- data.frame(growth_night = X_test[, 1])
  
  # --- (1) XGBoost (防过拟合严谨参数版) ---
  dtrain <- xgb.DMatrix(data = X_train, label = Y_train)
  dtest  <- xgb.DMatrix(data = X_test)
  params <- list(
    objective   = "reg:squarederror", 
    eval_metric = "rmse", 
    max_depth   = 4, 
    eta         = 0.05, 
    subsample   = 0.8
  )
  xgb_fit <- xgb.train(params = params, data = dtrain, nrounds = 300, verbose = 0)
  df_comp$m_hat_xgb[test_idx] <- predict(xgb_fit, dtest)
  
  # --- (2) Support Vector Regression (SVR 高斯核) ---
  svm_fit <- svm(X_train, Y_train, kernel = "radial", cost = 1, gamma = 1/ncol(X))
  df_comp$m_hat_svm[test_idx] <- predict(svm_fit, X_test)
  
  # --- (3) MARS (多元自适应回归样条) ---
  mars_fit <- earth(X_train, Y_train, degree = 1) 
  df_comp$m_hat_mars[test_idx] <- as.numeric(predict(mars_fit, X_test))
  
  # --- (4) GAM (广义加性模型) ---
  gam_fit <- gam(Y ~ s(growth_night, bs = "cr"), data = train_df, family = gaussian())
  df_comp$m_hat_gam[test_idx] <- as.numeric(predict(gam_fit, newdata = test_df))
}


# ==================== 4. 模型融合 (Stacking / Super Learner) ====================
print("正在通过带非负约束的优化算法进行元融合...")

# 1. 组装 5 个模型的预测值矩阵 (N x 5)
M_mat <- as.matrix(df_comp[, c("m_hat_rf", "m_hat_xgb", "m_hat_svm", "m_hat_mars", "m_hat_gam")])

# 2. 定义目标函数：最小化残差平方和 (RSS)
loss_function <- function(w) {
  w_normalized <- w / sum(w) # 强行约束权重之和为 1
  pred <- M_mat %*% w_normalized
  return(sum((Y - pred)^2))
}

# 3. 运行 L-BFGS-B 优化器，限制权重在 [0, 1] 之间
init_weights <- rep(1/5, 5) # 初始等权分配
opt_res <- optim(
  par    = init_weights, 
  fn     = loss_function, 
  method = "L-BFGS-B", 
  lower  = rep(0, 5), 
  upper  = rep(1, 5)
)

# 4. 提取并归一化最终权重，在控制台打印结果（方便你写进论文里）
final_weights <- opt_res$par / sum(opt_res$par)
cat("\n--- 各个非线性模型的融合权重 ---\n")
cat(sprintf(" 随机森林 (RF) : %.3f\n XGBoost     : %.3f\n 支持向量回归 : %.3f\n MARS 样条    : %.3f\n GAM 样条     : %.3f\n", 
            final_weights[1], final_weights[2], final_weights[3], final_weights[4], final_weights[5]))
cat("--------------------------------\n")

# 5. 生成 Stacking 融合预测值与对应残差
df_comp$m_hat_stack <- as.numeric(M_mat %*% final_weights)
df_comp$f_hat_stack <- Y - df_comp$m_hat_stack

# 统一计算所有模型的对应残差 (f_hat)
df_comp$f_hat_xgb   <- Y - df_comp$m_hat_xgb
df_comp$f_hat_svm   <- Y - df_comp$m_hat_svm
df_comp$f_hat_mars  <- Y - df_comp$m_hat_mars
df_comp$f_hat_gam   <- Y - df_comp$m_hat_gam



# ==================== 5. 精准合并回原数据集 ====================
print("正在将结果对齐并合并回原始数据集...")
match_idx <- match(df$row_id, df_comp$row_id)

# 批量赋值到含缺失值的完整大表
df$m_hat_rf    <- df_comp$m_hat_rf[match_idx]
df$f_hat_rf    <- df_comp$f_hat_rf[match_idx]

df$m_hat_xgb   <- df_comp$m_hat_xgb[match_idx]
df$f_hat_xgb   <- df_comp$f_hat_xgb[match_idx]

df$m_hat_svm   <- df_comp$m_hat_svm[match_idx]
df$f_hat_svm   <- df_comp$f_hat_svm[match_idx]

df$m_hat_mars  <- df_comp$m_hat_mars[match_idx]
df$f_hat_mars  <- df_comp$f_hat_mars[match_idx]

df$m_hat_gam   <- df_comp$m_hat_gam[match_idx]
df$f_hat_gam   <- df_comp$f_hat_gam[match_idx]

df$m_hat_stack <- df_comp$m_hat_stack[match_idx]
df$f_hat_stack <- df_comp$f_hat_stack[match_idx]

df$row_id <- NULL # 移除辅助列

# ==================== 6. 导出为 Stata 格式 ====================
print("正在导出 Stata 数据文件...")
# 导出到当前工作目录
write_dta(df, "anti_corruption_with_ml.dta")
# 导出到指定的绝对路径
write_dta(df, "C:/Users/siyang zhu/Desktop/Anti-corruption/anti_corruption_with_ml.dta")

print("全部完成！脚本运行成功。")
