# Import packages 
import pandas as pd

# Read in the data files 
ab_full = pd.read_excel('2018-2019/england_abs.xlsx', dtype={"URN": str})
census_full = pd.read_excel('2018-2019/england_census.xlsx', dtype={"URN": str})
ks4_full = pd.read_excel('2018-2019/england_ks4final.xlsx', dtype={"URN": str}, na_values=['NE', 'NP', 'SUPP'])
sch_full = pd.read_excel('2018-2019/england_school_information.xlsx', dtype={"URN": str})

# Cut each data set to the relevant number of variables 

# Drop percentage absentees - taken absoloute number instead 
ab = ab_full.drop(['PPERSABS10'], axis=1)

# Get the index of the variables of interest taking their name from metadata 
# Create a final dataset with these variables using iloc
census_full.columns.get_loc('NUMFSM')
census = pd.DataFrame(census_full.iloc[:, [0, 1, 2, 3, 4, 9, 13, 19]]) 

ks4_full.columns.get_loc('EBACCAPS')
ks4 = pd.DataFrame(ks4_full.iloc[
    :, [0, 1, 2, 3, 4, 9, 10, 16,\
         17, 18, 20, 26, 41, 45, 57,\
              60, 66, 99]]) 

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
ks4 = ks4.drop(ks4[(ks4['RECTYPE'] >= 4) & (ks4['RECTYPE'] <= 7)].index).reset_index(drop=True)
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
ab = ab.drop(ab[ab['URN'].isnull()].index).reset_index(drop=True)
census = census.drop(census[census['URN'] == 'NAT'].index).reset_index(drop=True)

# ALl datasets now have no missing URNs and unique URNs 
# See what else is missing from Ks4
ks4.isnull().sum(axis = 0)
# Drop cases where attainment 8 score is missing as this will be the predicted value so is necessary 
ks4 = ks4.drop(ks4[ks4['ATT8SCR'].isnull()].index).reset_index(drop=True)

# Start joining - first with sch
# Full join with ks4 and sch loses no data - everything in ks4 is in sch (5516 rows)
ks4_sch = ks4.join(sch.set_index('URN'), on='URN', how='inner', lsuffix='_ks4', rsuffix='_sch')
ks4_sch.isnull().sum(axis = 0)
# New data set without the repeat variables 
ks4_sch = pd.DataFrame(ks4_sch.iloc[
    :, [0, 2, 3, 4, 5, 6, 7,\
         8, 10, 11, 12, 13, 14, 15,\
             16, 18, 19, 22, 24, 25, 26]]) 
# For any missing town value, replace with other town column if present there
ks4_sch.TOWN_ks4.fillna(ks4_sch.TOWN_sch,inplace=True)
ks4_sch = ks4_sch.drop(['TOWN_sch'], axis=1)

# Now with census (left join to keep all KS4 data)
ks4_sch_census = ks4_sch.join(census.set_index('URN'), on='URN', how='left', rsuffix='_cen')
ks4_sch_census.isnull().sum(axis = 0)
ks4_sch_census.TEALGRP2.fillna(ks4_sch_census.NUMEAL,inplace=True)
ks4_sch_census.TSENELSE.fillna(ks4_sch_census.SEN_ALL,inplace=True)
ks4_sch_census = pd.DataFrame(ks4_sch_census.iloc[
    :, [0, 1, 2, 3, 4, 5, 6, 7,\
         8, 9, 10, 11, 13, 14, 15,\
             16, 17, 18, 19, 24, 26]]) 

# Join with ab
final_na = ks4_sch_census.join(ab.set_index('URN'), on='URN', how='left', rsuffix='_ab') 
final_na.isnull().sum(axis = 0)
final_na = final_na.drop(['LA_ab', 'ESTAB'], axis=1)

# Clarify variable names 
final_na = final_na.rename(columns={"RECTYPE": "record",
"ESTAB_ks4": "estab_numb",
'URN': 'urn',
'SCHNAME_ks4': 'school_name',
'TOWN_ks4': 'town',
'PCODE': 'postcode',
'NFTYPE': 'school_type1',
'RELDENOM': 'religion',
'EGENDER': 'gender',
'TOTPUPS': 'total_pupils',
'TFSM6CLA1A': 'disadvantage',
'TEALGRP2': 'eal',
'ATT8SCR': 'att8_score',
'ATT8SCREBAC': 'att8_ebacc',
'LANAME':'la_name',
'LA': 'la_code',
'SCHSTATUS': 'status',
'MINORGROUP': 'school_type2',
'SCHOOLTYPE': 'school_type3',
'NUMFSM': 'fsm',
'TSENELSE': 'sen',
'PERCTOT': 'per_abs'
})

final_na.to_csv('final_na.csv')

# Drop na's from final dataframe 
final = final_na.dropna().reset_index(drop=True)

final.to_csv('final.csv')