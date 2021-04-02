# Import packages 
import pandas as pd

# Read in the data files 
ab_full = pd.read_excel('2018-2019/england_abs.xlsx', dtype={"URN": str})
census_full = pd.read_excel('2018-2019/england_census.xlsx', dtype={"URN": str})
ks4_full = pd.read_excel('2018-2019/england_ks4final.xlsx', dtype={"URN": str})
sch_full = pd.read_excel('2018-2019/england_school_information.xlsx', dtype={"URN": str})

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
sch = pd.DataFrame(sch_full.iloc[
    :, [0, 1, 2, 3, 5, 9, 10, 11, \
        14, 15, 17, 18, 21, 22, 23]]) 


# Loot at NA's across the 4 data frames - 
# see if any will pose an issue for the join (lots of missing URN's)
for df in [ab, census, ks4, sch]:
    print(df.isnull().sum(axis = 0))

# URN missingness: ab = 3, census = 0, ks4 = 157 (I suspect these are the rows which represent LA's rather than schools), sch = 0

# ks4 needs to be the leading data set as the others include primary schools as well as secondary
ks4['RECTYPE'].value_counts()
# Rectypes 4, 7 and 5 are not schools and their value counts add to the number of missing URNs so these can be dropped 
ks4 = ks4.drop(ks4[(ks4['RECTYPE'] >= 4) & (ks4['RECTYPE'] <= 7)].index)
# check the drop was correct 
ks4['RECTYPE'].value_counts()
ks4.isnull().sum(axis = 0)

# Finally, check all URNs are unique 
ks4['URN'].is_unique
# And for the remaining data sets 
for df in [ab, census, sch]:
    print(df['URN'].is_unique)

# Sch and ks4 have all unique URNs, ab and census don't 
ab['URN'].nunique() # out of 21217 rows, 21214 are unique 
ab[ab['URN'].duplicated()]
census['URN'].nunique() # out of 23942 rows, 23940 are unique 
census[census['URN'].duplicated()]
# Rows in ab which URN's aren't unique (3 rows) are where URN is missing - these are National summary rows so can be dropped 
# Rows in census in which URN's aren't unique (2 rows) are rows where URN = 'NAT', these are also national sum
ab = ab.drop(ab[ab['URN'].isnull()].index)
census = census.drop(census[census['URN'] == 'NAT'].index)

# ALl datasets now have no missing URNs and unique URNs 


sch['ISSECONDARY'].value_counts()
sch = sch.drop(sch[sch['ISSECONDARY'] == 0].index)
ks4.join(sch.set_index('URN'), on='URN', how='outer', lsuffix='_ks4', rsuffix='_sch')

