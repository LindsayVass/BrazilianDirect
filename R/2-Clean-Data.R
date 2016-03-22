library(dplyr)
library(lubridate)

# clean campaign data
cleanData <- origData %>%
  filter(Campaign.state == "enabled") %>%
  select(Campaign, Day, Impressions, Clicks, Cost, Conversions) %>%
  arrange(Campaign, Day)

cleanData$Day <- mdy(cleanData$Day)
cleanData$Cost <- as.numeric(cleanData$Cost)

# remove campaigns that didn't run for the whole time period
goodCampaigns <- cleanData %>%
  filter(Day == max(Day)) %>%
  select(Campaign)
cleanData <- inner_join(cleanData, goodCampaigns)

# clean keyword data
cleanKeywordData <- keywordData %>%
  filter(Keyword.state == "enabled") %>%
  select(Keyword, Campaign, Ad.group, Day, Clicks, Cost, Conversions) %>%
  arrange(Campaign, Ad.group, Keyword, Day)

cleanKeywordData$Day <- mdy(cleanKeywordData$Day)
cleanKeywordData$Cost <- as.numeric(cleanKeywordData$Cost)
