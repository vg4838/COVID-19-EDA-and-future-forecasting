README

------------------------------------------------------------------------------------------------------------------
main.py:
This is the main file calling the files for cleaning and prediction
Take two user input. The first input prompts the user to reclean the data with a valid option of yes, else it proceeds with an user input for prediction of Week or Month (Case sensitive) for forecast analysis.

main():
This is the main function where the call to cleaning data sources and prediction of algorithms is performed.

clean_sources.py:
add_missing_dates_eur():
Adds the missing dates from the first day of data recorded until today in europe
add_missing_dates_usa():
Adds the missing dates from the first day of data recorded until today in usa
add_missing_dates_can():
Adds the missing dates in canada source from the first day of data recorded until today in the America continent

clean_europe():
Reads the raw europe data and formats to a standard format
clean_usa():
Reads the raw usa data and formats to a standard format
clean_canada():
Reads the raw canada data and formats to a standard format

Arima.py:
arima():
Takes one function input (file name created after cleaning data) passed by merge_files.py

Decision_Tree.py:
dt():
Takes two function input (file name created after cleaning data and type for analysis i.e. Month or Week) passed by merge_files.py. Take a user input of yes or no to re-train the model.

Execution process:
Run the merge_files.py 
It will retrieve data from the sources, clean them and run ML algorithms for analysis. User input to reclean the data and another input to select type of analysis (i.e Monthly or Weekly).
------------------------------------------------------------------------------------------------------------------
