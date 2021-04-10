final = read.csv('final_na.csv')
library(mice)
md.pattern(final, rotate.names = TRUE)	
