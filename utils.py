import numpy as np 
import pandas as pd
from sklearn import preprocessing


# replace NaN values with means of each class
def numeric_features(data, dataInfo):
    """
        Args: pd.DataFrame, indices of subjects with missing values, shoe sizes of subjects with missing values
        Return: dataframe without NaNs (missing values are replaced according to the strategies defined in the for loop)
    """
    correct_features = dataInfo[(dataInfo['Format'].str.contains("numeric"))  | (dataInfo['Name']=='cntry')]
    # 1 - GET RID OF COUNTRY-SPECIFIC DATA:
    correct_features = correct_features[(correct_features['Country_specific']=='no') | (correct_features['Name']=='cntry')]['Name'] # WHAT DOES THIS LINE DO?  | (correct_features['Name']=='cntry')][
    #print(list(correct_features.values))
    data_sliced = data[list(correct_features.values)]


    return data_sliced

#helper methods for replace_nans

# replace no-anwer cell values with with NaN
def change_to_nans(data_sliced):
    data_sliced = data_sliced.copy()
    data_sliced.replace([66, 77, 88, 99], np.NaN, inplace = True)
    return data_sliced


#long, we may divide it
def replace_nan(data_sliced, columns_no_cntry):
    # mean before nan-replacement
    meansDF = data_sliced.groupby('cntry').mean()
    print("mean BEFORE")
    # meansDF (uncomment to see)
    data_sliced = change_to_nans(data_sliced)
    # Calculate percentage of NaN-values per column
    tmp_dic = {}
    all_columns = len(data_sliced)
    for column in columns_no_cntry:
        number = (data_sliced[column].isna().sum())
        tmp_dic[column] =  round((number)/(all_columns)*100 , 2)

    nan_valuesDF = pd.DataFrame.from_dict(data = tmp_dic, orient='index', columns = ['nan_val_percent'])
    nan_valuesDF.head()
    """
        Above: Since the percentag of NaN-values per column is on a relatively low level (less than 15 %), we decided to replace all NaN-values with the mean of the respective column, instead of dropping the whole row.
        
        Make mean per country where NaN
    """
    # get the means per country as a DF with NanN-values
    print("mean post")
    meansNaNDF = data_sliced.groupby('cntry').mean()
    # meansNaNDF (uncomment to see)

    #Replace NaN with mean for each country

    # Maybe there is a way to do it faster - it takes sooo long.
    # + can normalization be done here? We need max for every country
    countries = data_sliced['cntry'].unique()
    new = pd.DataFrame(columns=data_sliced.columns)
    #print(data_sliced.isna().sum())
    for country in countries:
        x = data_sliced[data_sliced['cntry']  == country]
        for column in columns_no_cntry:
            x[column].fillna(meansNaNDF.loc[country, column], inplace = True)
        new = new.append(x)
    data_sliced= new
    print(data_sliced.isna().sum())
    print("are there any null values? : ")
    print(data_sliced.isnull().values.any())
    return data_sliced

#Below - create a target variable with 3 categories
#Add new column where lrscale3 that represents: left, center, right. Calculations based on lrscale column.

def add_target_column(data_sliced):
    data_sliced['lrscale3'] = data_sliced['lrscale']
    # Lookup: left - value 0, right - value 2, center - value 1.
    for index,row in data_sliced.iterrows(): # 0 means very left and 10 means very right
        if row['lrscale'] < 5:
            #row['lrscale3'] = 'lef ft'
            data_sliced.at[index,'lrscale3'] = 0
        elif row['lrscale'] > 5:
            #row['lrscale3'] = 'right'
            data_sliced.at[index,'lrscale3'] = 2
        else:
            #row['lrscale3'] = 'center'
            data_sliced.at[index,'lrscale3'] = 1
    return data_sliced

def normalize_data(data_sliced):
    data_sliced_no_country = data_sliced.drop('cntry', axis=1)
    x = data_sliced_no_country.values #returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    data_sliced_normalised = pd.DataFrame(x_scaled)
    return data_sliced_normalised
