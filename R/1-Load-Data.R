# skip first row, which contains file name from AdWords
origData <- read.csv('csv/Campaign_Report_1Jan2015-31Mar2015_DL3Jun2015.csv', 
                     header = TRUE, 
                     skip = 1)
keywordData <- read.csv('csv/Keyword_Report_1Jan2015-31Mar2015_DL6Jun2015.csv',
                        header = TRUE,
                        skip = 1)