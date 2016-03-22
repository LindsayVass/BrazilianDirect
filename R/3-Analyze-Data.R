library(dplyr)
library(ggplot2)

analyzeData <- cleanData %>%
  group_by(Campaign) %>%
  select(-Day) %>%
  summarise_each(funs(sum)) %>%
  mutate(CostPerConversion = Cost/Conversions)

ggplot(analyzeData, aes(x = CostPerConversion, y = Conversions, color = Campaign)) +
  geom_point(size = 5) +
  geom_text(aes(label = Campaign, hjust = 0, vjust = -1))

ggplot(cleanData, aes(x = Day, y = Conversions)) + 
  geom_point() +
  facet_wrap(~Campaign) +
  ggtitle("Conversions Over Time")


