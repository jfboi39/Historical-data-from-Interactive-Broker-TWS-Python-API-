import os
import time
import csv
from datetime import datetime, timedelta, date

def evaluateTimeStamp(productV, startDateV, endDateV, delayV):
    with open("productList_historicalData.txt", "r") as file:
        filedata = file.read()

    condition = True
    stepCount = 0

    while condition:
        dt_start = datetime.strptime(startDateV, "%Y-%m-%d %H:%M:%S")
        if(endDateV == ""):
            dt_end = datetime.now()
        else:
            dt_end = datetime.strptime(endDateV, "%Y-%m-%d %H:%M:%S")
        queryDay = (dt_start + timedelta(seconds=(delayV + stepCount) * 30.0 * 60.0)).weekday()
        queryHour = (dt_start + timedelta(seconds=(delayV + stepCount) * 30.0 * 60.0)).hour
        dt_start_adj = dt_start + timedelta(seconds=(delayV + stepCount) * 30.0 * 60.0)

        if(delayV == -999 or dt_start_adj >= dt_end):
            return 0

        if (queryDay < 5 and (queryHour >= 5 and queryHour < 17)):
            condition = False
        else:
            stepCount += 2

    oldStr = str(productV) + "," + str(delayV) + ","
    newStr = str(productV) + "," + str(delayV + stepCount) + ","
    filedata = filedata.replace(oldStr, newStr)

    with open("productList_historicalData.txt", "w") as file:
        file.write(filedata)

    return 1

if __name__ == "__main__":
    condition = True
    while condition:
        f = open("productList_historicalData.txt", "r")
        csvReader = csv.reader(f)

        header = next(csvReader)
        uniqueIDIndex = header.index("uniqueID")
        symbolIndex = header.index("symbol")
        securityIndex = header.index("securityType")
        exchangeIndex = header.index("exchange")
        currencyIndex = header.index("currency")
        expirationIndex = header.index("expiration")
        multiplierIndex = header.index("multiplier")
        startDateIndex = header.index("startDate")
        endDateIndex = header.index("endDate")
        delayTimeIndex = header.index("delayTime")

        sumValidRequest = 0
        if f.mode == 'r':
            for row in csvReader:
                sumValidRequest += evaluateTimeStamp(row[uniqueIDIndex],row[startDateIndex],row[endDateIndex],int(row[delayTimeIndex]))
        f.close()

        print(datetime.now())
        os.system('python HistoricalData.py')
        time.sleep((2.0 * 2.0 * sumValidRequest)/60.0 * (10.0 * 60.0) + 10.1) #Need to implement the logic in HistoricalData as well
        #No more than 60 requests within any ten minute period; BID_ASK is counted as twice and we request 2x 30 minutes.