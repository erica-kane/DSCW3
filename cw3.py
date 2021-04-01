# Import packages 
import pandas as pd

# Read in the data files 
ab_full = pd.read_excel('2018-2019/england_abs.xlsx')
census_full = pd.read_excel('2018-2019/england_census.xlsx')
ks4_full = pd.read_excel('2018-2019/england_ks4final.xlsx')
sch_full = pd.read_excel('2018-2019/england_school_information.xlsx')

# Cut each data set to the relevant number of variables 

# Drop percentage absentees - taken absoloute number instead 
ab_full.head()
ab = ab_full.drop(['PPERSABS10'], axis=1)

# Get the index of the variables of interest taking their name from metadata 
# Create a final dataset with these variables using iloc
census_full.head()
census_full.columns.get_loc('NUMFSM')
census = pd.DataFrame(census_full.iloc[:, [0, 1, 2, 3, 4, 9, 13, 19]]) 

ks4_full.head()
ks4_full.columns.get_loc('EBACCAPS')
ks4 = pd.DataFrame(ks4_full.iloc[
    :, [0, 1, 2, 3, 4, 9, 10, 16,\
         17, 18, 20, 26, 41, 45, 57,\
              60, 66, 99]]) 

sch_full.head()
sch_full.columns.get_loc('ADMPOL')
ks4 = pd.DataFrame(ks4_full.iloc[
    :, [0, 1, 2, 3, 5, 9, 10, 11, \
        14, 15, 17, 18, 21, 22, 23]]) 


# Loot at NA's across the 4 data frames - see if any will pose an issue for the join (lots of missing URN's)