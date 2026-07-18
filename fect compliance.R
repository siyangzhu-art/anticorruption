library(haven)
fect <- read_dta("C:/Users/siyang zhu/Desktop/Anti-corruption/proposition1/fect.dta")
View(fect)
library(panelView)
library(fect)


df <- read_dta("C:/Users/siyang zhu/Desktop/Anti-corruption/proposition1/R.dta")
df$anti_shock <- as.numeric(zap_labels(df$anti_shock))

library(dplyr)
df_clean <- df %>%
  arrange(city_id, year) %>%          # 严格按城市和年份排序
  group_by(city_id) %>%               # 按城市分组
  mutate(
    Cosine_Plan_lag1 = lag(Cosine_Plan, 1),
    JS_Plan_lag1     = lag(JS_Plan, 1)
  ) %>%
  ungroup()
out.fect.Cos <- fect(Cosine_Plan_lag1 ~ anti_shock, data = df_clean, index = c("city_id","year"),
                     force = "two-way", method="ife",
                     se = TRUE, nboots = 1000, parallel = TRUE, cores = 16)
plot(out.fect.Cos, highlight.fill = TRUE)

out.fect.Cos <- fect(Cosine_Plan~anti_shock,data = as.data.frame(df), index = c("city_id","year"),
                         force = "two-way", method = "fe",
                         se = TRUE, nboots = 1000, parallel = TRUE, cores = 16,
                        cl="city_id")
plot(out.fect.Cos, highlight.fill = TRUE)
out.fect.JS <- fect(JS_Plan_lag1 ~ anti_shock, data = df_clean, index = c("city_id","year"),
                    force = "two-way", method = "fe",
                    se = TRUE, nboots = 1000, parallel = TRUE, cores = 16,
                    cl="city_id")
plot(out.fect.JS, highlight.fill = TRUE)


out.fect.JS <- fect(JS_Plan~anti_shock,data = as.data.frame(df), index = c("city_id","year"),
                     force = "two-way", method = "fe",
                     se = TRUE, nboots = 1000, parallel = TRUE, cores = 16,
                     cl="city_id")
plot(out.fect.JS, highlight.fill = TRUE)

out.fect.carry <- fect(Cosine_Plan~anti_shock,data = as.data.frame(df), index = c("city_id","year"),
                         force = "two-way", method = "fe",
                         se = TRUE, nboots = 1000, parallel = TRUE, cores = 16,
                        carryoverTest = TRUE, carryover.period = c(1,2),na.rm = TRUE)
plot(out.fect.carry, highlight.fill = TRUE)

out.fect.placebo <- fect(JS_Plan~anti_shock,data = as.data.frame(df), index = c("city_id","year"),
                         force = "two-way", method = "fe",
                         se = TRUE, nboots = 1000, parallel = TRUE, cores = 16,
                         placeboTest = TRUE, placebo.period = c(-1, 0),na.rm = TRUE,cl="city_id")
plot(out.fect.placebo, highlight.fill = TRUE)
out.fect.carry <- fect(JS_Plan~anti_shock,data = as.data.frame(df), index = c("city_id","year"),
                       force = "two-way", method = "fe",
                       se = TRUE, nboots = 1000, parallel = TRUE, cores = 16,
                       carryoverTest = TRUE, carryover.period = c(1,2),na.rm = TRUE)
plot(out.fect.carry, highlight.fill = TRUE)



