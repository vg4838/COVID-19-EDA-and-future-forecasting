import pandas as pd
from ARIMA import arima
from Decision_tree import dt
from clean_sources import *

def main():
    '''
    Start of program where it first retrieves, cleans and merges data from sources and then makes call for prediction
     using ARIMA and decision tree models
    :return: None
    '''
    user_input = input("Do you want to re-clean data ? \n Yes | No \n Disclaimer: Need active internet connection for "
                       "same \n ")
    if user_input.lower() == "yes":
        eur = clean_europe()
        eur.to_csv('EUR_.csv', index=False)
        usa = clean_usa()
        usa.to_csv('USA_.csv', index=False)
        can = clean_canada(usa)
        can.to_csv('CAN_.csv', index=False)
        final_dataset = pd.concat([can, eur, usa])
        final_dataset = final_dataset.reset_index(drop=True)
        data = pd.DataFrame(final_dataset)

        # since dataset merged is large, splitting into excel sheets
        data1 = pd.DataFrame(data.iloc[:len(data) // 2])
        data2 = pd.DataFrame(data.iloc[len(data) // 2:])
        writer = pd.ExcelWriter('project_file_join.xlsx', engine='xlsxwriter')
        data1.to_excel(writer, sheet_name='Sheeta')
        data2.to_excel(writer, sheet_name='Sheetb')
        writer.save()
    forecast = input("Predict forecast for: \n -Week \n -Month : ")
    if forecast != "Month" and forecast != "Week":
        print("Enter correct choice! \n")
        forecast = input("Predict forecast for: \n -Week \n -Month : ")
    arima("project_file_join.xlsx")
    dt("project_file_join.xlsx", forecast)


if __name__ == '__main__':
    main()
