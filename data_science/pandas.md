# Document Format Configuration

```python
# float format
pd.options.display.float_format = '{:,.2f}'.format
# Note: `.format` is required. It specifies that the formatting string should be used as a function to format floating-point numbers.
# '{:,.2f}' is a template for formatting numbers. To format a specific number, use it this way: `'{:,.2f}'.format(1234.56789101112)`. => '1,234.57'
# '{:,.2f}'.format turns the template into a function. Assigning it to `pd.options.display.float_format` makes pandas use it to display all floating-point numbers in the project. 
```

# Import Google drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

# Create a dataframe

```python
# by reading from a csv file
df_data = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/data.csv')

# by a specified json data
data = {
    'year': [2020, 2021],
    'category': ['Physics', 'Chemistry'],
    'laureate_type': ['Individual', 'Organization'],
    'birth_date': ['1970-01-01', '1980-01-01'],
    'full_name': ['John Doe', 'Jane Smith'],
    'organization_name': ['Org1', 'Org2'],
    'country': ['USA', 'UK']
}
# in each key-value pair, values are lists with the same length
df_data = pd.DataFrame(data)
```

# Data Exploration & Cleaning

## Check number of rows and columns

```python
# number of rows
df_data.shape[0]
# number of columns
df_data.shape[1]
```

## Check all headers of the dataframe

```python
df_data.columns
```
output:
```plaintext
Index(['year', 'category', 'laureate_type', 'birth_date', 'full_name', 'organization_name',
       'country'],
dtype='object')
```

## Sorting

```python
# single column
df_data.sort_values(by='column_name', ascending=False)

# multiple columns
df_data.sort_values(by=['column1', 'column2'], ascending=[True, False])
```

## Select the first and last n rows

```python
# first 3 rows
df_data.head(3)
# or
df_data[:3]

# last 5 rows
df_data.tail(5)
# or
df_data[-5:]
```

## Check for duplicates and missing values

```python
# check duplicates
df_data.duplicated()

# check if missing values
df_data.isna()
```
This will return a dataframe of boolean values:
```plaintext
0      False
1      False
2      False
3      False
4      False
       ...  
957    False
958    False
959    False
960    False
961    False
Length: 962, dtype: bool
```

## Convert a dataframe to a numpy array

```python
df_data.duplicated().values  # note: .values is an attribute, not a method
```

## Check if any values in a Series or DataFrame are True

```python
df_data.isna().any()  # check each row in the dataframe
df_data.isna().values.any()  # convert the dataframe to a numpy array then check each values in the array
# both methods work
```

## Check the summary of all columns

```python
df_data.info()
```
This method is generally used to check for columns having missing values.

This is a sample output:
```plaintext
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 962 entries, 0 to 961
Data columns (total 16 columns):
 #   Column                 Non-Null Count  Dtype 
---  ------                 --------------  ----- 
 0   year                   962 non-null    int64 
 1   category               962 non-null    object
 2   prize                  962 non-null    object
 3   motivation             874 non-null    object
 4   prize_share            962 non-null    object
 5   laureate_type          962 non-null    object
 6   full_name              962 non-null    object
 7   birth_date             934 non-null    object
 8   birth_city             931 non-null    object
 9   birth_country          934 non-null    object
 10  birth_country_current  934 non-null    object
 11  sex                    934 non-null    object
 12  organization_name      707 non-null    object
 13  organization_city      707 non-null    object
 14  organization_country   708 non-null    object
 15  ISO                    934 non-null    object
dtypes: int64(1), object(15)
memory usage: 120.4+ KB
```

We see that maximum rows are 962. Columns having less than 962 value counts definitely have NaN values.

## Check the number of duplicated and missing values in each column with `.sum()` method
```python
df_data.duplicated().sum()
df_data.isna().sum()
```
Sample output:
```plaintext
year                       0
category                   0
prize                      0
motivation                88
prize_share                0
laureate_type              0
full_name                  0
birth_date                28
birth_city                31
birth_country             28
birth_country_current     28
sex                       28
organization_name        255
organization_city        255
organization_country     254
ISO                       28
dtype: int64
```


## Filter Dataframe

### Filter columns

```python
#1 direct way: use a list of column names: ['column1', 'column2'] inside df_data[]:
df_data[['column1', 'column2']] 
# Note: single column (df_data['column1']) will work, but df_data['column1', 'column2'] will not. We have to pass a list of column names to df_data[] if there are more than one column.

#2 using filter() function - filter based on patterns:
df_data.filter(items=['column1', 'column2']) 
## filter() function is more flexible if we want to apply pattern filtering criteria, namely `like`, `regex`. Example:
df_data.filter(like='name', axis=1)  # select columns that contain "name". 
df_data.filter(regex='^na', axis=1)  # select columns that match the regular expression. `^na` means start with "na".
## Note: param `axis` is optional. Value 1 stands for `column`, while 0 stands for `row`. See the `Filter rows` section for more info regarding row filtering.

#3 using `.loc[]`, filter based on labels or values:
col_subset = ['year', 'category', 'laureate_type', 'birth_date', 'full_name', 'organization_name']
df_data.loc[col_subset]
```

### Filter rows

```python
#1 direct way, aka boolean indexing
df_data[df_data['column_name'] == 'value']

#2 using filter() function, filter based on labels only, not values!
## assumed that we have a data value:
data = {
    'A': [1, 2, 3],
    'B': [4, 5, 6]
}
## create a dataframe
df_data = pd.DataFrame(data)
```
Printing the dataframe would yield:
| \# | A | B |
| --- | --- | --- |
| 0 | 1 | 4 |
| 1 | 2 | 5 |
| 2 | 3 | 6 |

Using `filter()` to filter rows by <span style="color: orange;">index label</span>:
```python
df_data.filter(items=[0, 2], axis=0)  # the `items` param is omittable: df_data.filter([0,2], axis=0)
```
This will yield:
| \# | A | B |
| --- | --- | --- |
| 0 | 1 | 4 |
| 2 | 3 | 6 |

<u>NOTE</u>: `filter()` is generally used to filter <span style="color:orange;">columns</span> based on patterns. It's rarely used to filter rows. For row filtering, the `.filter()` function can only filter based on the index label, not record values, i.e., `df_data['category'].filter(regex='^Phys', axis=0)` seems be be legit, but it will not work.

```python
#3 using `.loc[]`, which is an `indexer` used for label-based indexing, allowing us to select rows and columns by labels, boolean conditions, and slices.

## only filter rows where `birth_date` is NaN and return all columns
df_data.loc[df_data.birth_date.isna()]

## filter rows where `birth_date` is NaN and return specified columns, i.e., filter rows and columns at the same time
col_subset = ['year', 'category', 'laureate_type', 'birth_date', 'full_name', 'organization_name']
df_data.loc[df_data.birth_date.isna(), col_subset]
```

**More about `.loc[]`**:
- Flexibility: `.loc[]` is highly flexible and often preferred for selecting rows and columns based on labels, boolean conditions, or specific ranges. It allows us to specify both row and column filters simultaneously.
- Preference: While `.loc[]` is versatile and powerful, it is not always the only or the most preferred way in all situations. `Direct boolean indexing` is often clearer and more concise. `.loc[]` becomes particularly useful when we need to filter rows and columns together or when dealing with more complex indexing needs.
- More examples of `.loc[]` indexer:
```python
# example with labels or indices
df_data.loc[0:2, ['A', 'B']]

# example with boolean conditions
df_data.loc[df_data['A'] > 1, ['A', 'B']]
```

```python
#4 using .str.contains() method
## As mentioned above, `filter()` method only works if we intend to filter COLUMNS based on patterns or filter ROWS based on the index label column. `.str.contains()` enables row filtering:

## `.str` is a `Special Accessor` for String operations on Series Data. It allows us to apply `string methods` directly to each element in a Pandas Series containing string values, enabling us to manipulate and analyze text data.
## `df_data['category'].str` will return a string accessor type which will cause a KeyError. `.str` cannot be used as an indexer by itself, it has to be followed by string method(s) or condition(s), for example: .str.contains('some_string'); .str.startswith('some_string')
filtered_df = df_data[df_data['category'].str.contains('Physics')]
filtered_df = df_data[df_data['category'].str.startswith('Phy')]
filtered_df = df_data[df_data['category'].str.endswith('try')]

## Extra: Operations on rows using `.str`
df_data['category_upper'] = df_data['category'].str.upper()  # convert each value in the category column to uppercase
df_data['category_replaced'] = df_data['category'].str.replace('Physics', 'Science')  # replace each value in the category column
```

# Custom Index in Pandas

By default, indices in pandas are integers, starting from 0. If we want to use a custom index, we need to predefine them first then apply methods as follow:

## Using `.set_index(<index_column_name>)`:

```python
import pandas as pd
# Sample DataFrame with indices as part of the data
data = {
    'CustomIndex': ['row1', 'row2', 'row3', 'row4'],
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'City': ['New York', 'Los Angeles', 'New York', 'Chicago']
}

# Create DataFrame and set the predefined 'CustomIndex' column as the index
df_data = pd.DataFrame(data).set_index('CustomIndex')
```

Output:

```plaintext
           Name         City
CustomIndex                        
row1      Alice     New York
row2        Bob  Los Angeles
row3    Charlie     New York
row4      David      Chicago
```

**Note: We can also use the `set_index('CustomIndex')` method after creating the dataframe.**

```python
# Create DataFrame 
df_data = pd.DataFrame(data)

# Set 'CustomIndex' column as the index
df_data = df_data.set_index('CustomIndex')
```


## Use .DataFrame's `index` param *for date indices*:
```python
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'City': ['New York', 'Los Angeles', 'New York', 'Chicago']
}

dates = pd.date_range(start='2025-01-01', periods=len(data['Name']), freq='D')

df_data = pd.DataFrame(data, index=dates)
```

## Use .DataFrame's `index` param *for string indices*:

```python
data = {
       'Name': ['Alice', 'Kaylee', 'Sophia', 'Lyly'],
       'City': ['New York', 'Los Angeles', 'New York', 'Chicago']
}

custom_index = ['customIndex' + i for i in range(len(data['Name']))]

df_data = pd.DataFrame(data)
df_data.index = custom_index  ## index is a parameter of the .DataFrame() method, we can specify it like this
```

Note: The `index` param of the `.DataFrame()` method can accept several types of inputs, including:
- List or Array: Simple lists or arrays of values (as above)
- DatetimeIndex: A pandas `DatetimeIndex` object (as above)
- MultiIndex: A pandas `MultiIndex` object
```python
index = pd.MultiIndex.from_product([['Group1', 'Group2'], ['SubGroup1', 'SubGroup2']], names=['Group', 'SubGroup'])
```
Output:
```plaintext
                     Value
Group  Subgroup           
Group1 Subgroup1 -0.977278
       Subgroup2  0.950088
Group2 Subgroup1 -0.151357
       Subgroup2 -0.103219
```

- CategoricalIndex: A pandas `CategoricalIndex` object
```python
index= pd.CategoricalIndex(['Category1', 'Category2', 'Category1', 'Category2'], categories=['Category1', 'Category2'])
```
Output:
```plaintext
           Value
Category1     10
Category2     20
Category1     30
Category2     40
```

# Data Types 

## Check Datatype of a value (of a Pandas Series)

```python
type(df_data.birth_date[0])
```

# Data Type Conversion

```python
# to convert a Series or DataFrame to a Primitive Data Type, use `.astype()`
df_data.prize_share.astype(str)  # convert values in a series to string
df_data.scores.astype(float)  # convert to float
df_data.level.astype(int)  # convert to int
df_data.is_alive.astype(bool)  # convert to bool


# convert to datetime, which is quite different and cannot use the .astype() as above
df_data.birth_date = pd.to_datetime(df_data.birth_date)
```

# Column Manipulation

## Split Columns and create a new dataframe
Assumed that the `prize_share` column looks like this:
```plaintext
       category prize_share
0     Chemistry         1/1
1    Literature         1/1
2      Medicine         1/1
3         Peace         1/2
4         Peace         1/2
..          ...         ...
957    Medicine         1/3
958       Peace         1/1
959     Physics         1/4
960     Physics         1/4
961     Physics         1/2

[962 rows x 2 columns]
```
We want to create a new column called `share_pct` which is of type float. To do that, we first need to split the `prize_share` column into two columns using the `str.split()` method:
```python
separated_values = df_data.prize_share.str.split('/', expand=True)
# .split() is a string method, so it must be followed by the `.str` accessor
```
Next, we assign two variables, namely `numerator` and `denominator` for `separated_values[0]` and `separated_values[1]`, respectively. We use the `astype(int)` method to convert the values to integer.

```python
numerator = separated_values[0].astype(int)
denominator = separated_values[1].astype(int)
share_pct = numerator / denominator  # this is a pandas series with the datatype of float
```

### `expand` parameter:
By default, the `expand` value is False. Compare the outputs below:

- output from `expand=False`:
```plaintext
0      [1, 1]
1      [1, 1]
2      [1, 1]
3      [1, 2]
4      [1, 2]
        ...  
957    [1, 3]
958    [1, 1]
959    [1, 4]
960    [1, 4]
961    [1, 2]
Name: prize_share, Length: 962, dtype: object
<class 'pandas.core.series.Series'>
```
We see that there is only one column. Values in each row are lists.

- output from `expand=True`:
```plaintext
     0  1
0    1  1
1    1  1
2    1  1
3    1  2
4    1  2
..  .. ..
957  1  3
958  1  1
959  1  4
960  1  4
961  1  2

[962 rows x 2 columns]
<class 'pandas.core.frame.DataFrame'>
```
We see that there are two columns.



## Add a new column to pandas dataset 

### Using direct assignment

```python
import pandas as pd

data = {
       'state': ['CA', 'NY', 'TX', 'CA', 'TX', 'NY', 'TX', 'CA'],
       'count': [1, 2, 3, 2, 1, 1, 2, 1]
}

df = pd.DataFrame(data)

# a series to be added to the dataframe
new_int_col = [111, 222, 333, 444, 555, 666, 777, 888]

# add a new column called `new_int_col` to the dataframe
df['new_int_col'] = new_int_col
print(df)
```

Output:

```plaintext
  state  count  new_int_col
0    CA      1          111
1    NY      2          222
2    TX      3          333
3    CA      2          444
4    TX      1          555
5    NY      1          666
6    TX      2          777
7    CA      1          888
```

Note that if the length of `new_int_col` is not equal to that of `df.index`, a ValueError will be raised:

```plaintext
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-70-bec12d117801> in <cell line: 20>()
     18 # Add a new column with full state name
     19 df['full_state'] = df['state'].map(state_names)
---> 20 df['test_col'] = [111, 222, 333, 444, 555, 666, 777]
     21 print(df)
     22 

3 frames
/usr/local/lib/python3.10/dist-packages/pandas/core/common.py in require_length_match(data, index)
    574     """
    575     if len(data) != len(index):
--> 576         raise ValueError(
    577             "Length of values "
    578             f"({len(data)}) "

ValueError: Length of values (7) does not match length of index (8)
```

To avoid that, first convert the `new_int_col` to a pandas series using `pd.Series()` (see below).


### Using Pandas' `pd.Series()`

```python
# a series to be added to the dataframe
new_int_col = [111, 222, 333, 444, 555, 666, 777] # length: 7 < len(data.state) = 8
new_str_col = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG', 'HHH', 'III']   # length: 9 > len(data.state) = 8

# add a new column called `new_int_col` to the dataframe
df['new_int_col'] = pd.Series(new_int_col)
df['new_str_col'] = pd.Series(new_str_col)
print(df)
```

Output:

```plaintext
  state  count  new_int_col new_str_col
0    CA      1       111.00         AAA
1    NY      2       222.00         BBB
2    TX      3       333.00         CCC
3    CA      2       444.00         DDD
4    TX      1       555.00         EEE
5    NY      1       666.00         FFF
6    TX      2       777.00         GGG
7    CA      1          NaN         HHH
```

Pandas automatically aligns the length of new_int_col and new_str_col to match df.index. If the series is shorter, pandas adds NaN for missing values; if longer, pandas ignores the extra values.

To handle missing values differently, we can use `.reindex(index=df.index, fill_value='Missing')` to fill with a specific value:

```python
new_int_col = [111, 222, 333, 444, 555, 666, 777]

# add a new column called `new_str_col` to the dataframe while customizing the default `NaN` value (use 'Missing' instead)
df['new_str_col'] = pd.Series(new_str_col).reindex(index=df.index, fill_value='Missing')
print(df)
```

Output:

```plaintext
  state  count new_str_series
0    CA      1            AAA
1    NY      2            BBB
2    TX      3            CCC
3    CA      2            DDD
4    TX      1            EEE
5    NY      1            FFF
6    TX      2            GGG
7    CA      1         Missing
```

### Using `.insert()`

#### get the column index of the `prize_share` column

```python
prize_share_index = df_data.columns.get_loc('prize_share')  # see more details of .get_loc() in other section below
```

#### add the new share_pct column next to the `prize_share` column

```python
df_data.insert(prize_share_index + 1, 'share_pct', share_pct)
```

### Other methods

#### Map an existing column to create a new one

```python
data = {
    'state': ['CA', 'NY', 'TX', 'CA', 'TX', 'NY', 'TX', 'CA'],
    'count': [1, 2, 3, 2, 1, 1, 2, 1]
}

df = pd.DataFrame(data)

# create a dictionary called `state_names` that maps the abbreviations to full state names
state_names = {
  'CA': 'California',
  'NY': 'New York',
  'TX': 'Texas'
}

# create a new column called 'full_state' by mapping the 'state' column to the 'state_names' dictionary
df['full_state'] = df.state.map(state_names)
print(df)
```


## Convert a string column to Fraction dtype

Simply creating a new `share_pct` column, and we need to get hassled creating other temporary columns (`numerator`, `denominator`) and need to have many more steps before achieving the result we want. Isn't there a faster way to do this? Actually, there is.

Another method is that, we can first convert the `prize_share` column, which values are strings but look like fractions, into fractions dtype, then convert the fractions to float.

Convert to fraction dtype:

```python
from fractions import Fraction

df_data.prize_share = df_data.prize_share.apply(lambda x: float(Fraction(x)))
```

Now the `prize_share` column is of type float, and we no longer need to create a new `share_pct` column. We could analyze data directly using the `prize_share` column.



## Get the column index, a.k.a., the position of a column

```python
df_data.columns.get_loc('share_pct')  # this return the position as an integer
# .get_loc() is a method of the .columns attribute. Hence to call it, we must call the .columns first.
```

## Count all unique values in a column

### Use `value_counts()`

```python
biology = df_data.sex.value_counts()
print(biology)
print(type(biology))
```

Output:
```plaintext
sex
Male      876
Female     58
Name: count, dtype: int64

<class 'pandas.core.series.Series'>
```

### Use `groupby()` and `count()`

```python
biology = df_data.groupby('sex')['sex'].count()
print(biology)
print(type(biology))
```

Output:

```plaintext
sex
Male      876
Female     58
Name: count, dtype: int64

<class 'pandas.core.series.Series'>
```

We see that the output is exactly the same as `value_counts()`. But using `df_data.groupby('sex')['sex'].count()` is a bit tedious if we only want to show the count of each sex in the `sex` column itself. However, this method is useful when we want to count other columns grouping by a particular column. For example:

```python
df_data.groupby('sex')[['birth_date', 'birth_city', 'birth_country']].count()
```

Here, we group by the `sex` column and count the `birth_date`, `birth_city`, and `birth_country` columns. Output is a table:

| sex | birth_date | birth_city | birth_country |
| --- |------------|------------|---------------|
| Female | 58 | 58 | 58 |
| Male | 876 | 873 | 876 |




