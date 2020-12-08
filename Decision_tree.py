import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from sklearn.model_selection import GridSearchCV
from pandas.tseries.offsets import *
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split

pd.set_option('display.max_columns', 5000)


def dt(file,forecast):
    print("Decision Tree processing")
    df = pd.read_excel(file)
    df['Date'] = pd.to_datetime(df.REPORT_DATE)
    df.sort_values(by='Date', inplace=True)
    ftr = (df['REPORT_DATE'] + pd.Timedelta(16, unit='W')).to_frame()
    ftr['CONTINENT_NAME'] = None
    ftr['COUNTRY_SHORT_NAME'] = None
    ftr['COUNTRY_ALPHA_3_CODE'] = None
    ftr['PEOPLE_POSITIVE_NEW_CASES_COUNT'] = 0
    ftr['PEOPLE_DEATH_NEW_COUNT'] = 0
    ftr['PEOPLE_POSITIVE_CASES_COUNT'] = df['PEOPLE_POSITIVE_CASES_COUNT']
    ftr['PEOPLE_DEATH_COUNT'] = 0
    ftr["DATA_SOURCE_NAME"] = None
    ftr["COUNTY_NAME"] = None
    ftr["PROVINCE_STATE_NAME"] = None
    ftr["COUNTY_FIPS_NUMBER"] = None

    df1 = pd.concat([df, ftr], ignore_index=True)
    df1.sort_values(by='Date', inplace=True)
    X_train, X_test = df, ftr

    X_train =  X_train.resample('D', on='REPORT_DATE')['PEOPLE_POSITIVE_CASES_COUNT'].sum().reset_index()
    X_test =  X_test.resample('D', on='REPORT_DATE')['PEOPLE_POSITIVE_CASES_COUNT'].sum().reset_index()

    X_train["Year"] = pd.to_datetime(X_train['REPORT_DATE']).dt.year
    X_train["Week"] = pd.to_datetime(X_train['REPORT_DATE']).dt.week
    X_train["Month"] = pd.to_datetime(X_train['REPORT_DATE']).dt.month
    X_train["Day"] = pd.to_datetime(X_train['REPORT_DATE']).dt.day
    X_test["Year"] = pd.to_datetime(X_test['REPORT_DATE']).dt.year
    X_test["Week"] = pd.to_datetime(X_test['REPORT_DATE']).dt.week
    X_test["Month"] = pd.to_datetime(X_test['REPORT_DATE']).dt.month
    X_test["Day"] = pd.to_datetime(X_test['REPORT_DATE']).dt.day

    X_train = X_train[X_train['PEOPLE_POSITIVE_CASES_COUNT'] < 29063399]
    X_train = X_train[X_train['PEOPLE_POSITIVE_CASES_COUNT'] > 27]

    predictors = X_train.drop(['REPORT_DATE', 'PEOPLE_POSITIVE_CASES_COUNT'], axis=1)
    target = X_train['PEOPLE_POSITIVE_CASES_COUNT']
    x_train, x_test, y_train, y_test = train_test_split(predictors, target, test_size=0.2)

    """
    To check which model best suites for the data
    """


    user = input("Want to retrain?")
    if user.lower() == "yes":
        params = {'max_leaf_nodes': list(range(2, 100)), 'min_samples_split': [2, 3, 4]}
        model = GridSearchCV(DecisionTreeRegressor(random_state=0),params, verbose=1, cv=3)
        pickle.dump(model, open("dt-obj", "wb"))
    else:
        model = pickle.load(open("dt-obj", "rb"))

    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    test1 = X_test.drop(['REPORT_DATE', 'PEOPLE_POSITIVE_CASES_COUNT'], axis=1)
    pred2 = model.predict(test1)
    X_test['PEOPLE_POSITIVE_CASES_COUNT'] = pred2.round(0)
    result = X_test[['REPORT_DATE', 'PEOPLE_POSITIVE_CASES_COUNT']]
    X_test.to_csv('Prediction.csv')
    sns.lineplot(X_train[forecast], X_train['PEOPLE_POSITIVE_CASES_COUNT'], label="Actual data")
    sns.lineplot(X_test[forecast], X_test['PEOPLE_POSITIVE_CASES_COUNT'], label="Predicted data")
    plt.ticklabel_format(style='plain', axis='y', useOffset=False)
    plt.ylabel("AVG. People Positive Cases Count")
    plt.title("Actual and Prediction using Decision Tree")
    plt.legend(loc="best")
    plt.savefig("Actual and Prediction using Decision Tree.png")
    plt.show()
    plt.pause(3)
    plt.close()
