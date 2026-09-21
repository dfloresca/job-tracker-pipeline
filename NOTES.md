Initially not all the data displayed, when I made the window wider more data was displayed. This was resolved with 
```
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 0)
```

*   When no data is available it comes through as NAN. 
*   Close dates are not formatted as short dates and include midnight time stamps. Standardize date as short format.
    *   This is significant as consistency will make the data easier to work with.
*   Req # comes through as an object. May be due to mixed formatted requisitions.
    *   Significance lies in the fact that requisitions come in mixed formats. Sorting by Req # will be inconsistent.
*   Salary range appears as a string due to the range and differing salary values. Create a Min / Max annual range. When hourly salary is listed notate that the salary is derived from hourly salary.
    *   The significance affects sorting on the salary column. As a string it won't consistently sort. Using min max ranges would allow efficient sorting
    *   Future goal: add a differentiator for pay basis for salary vs hourly
*   Status come through with the dot(type of emoji)
    *   This will affect sorting as well as the emojis would group together.
