import os
import time
import csv
from datetime import datetime, timedelta, date

if __name__ == "__main__":
    condition = True
    while condition:
        f = open("productList_historicalData.txt", "r")
        csvReader = csv.reader(f)
        header = next(csvReader)
        startDateIndex = header.index("startDate")
        endDateIndex = header.index("endDate")
        delayTimeIndex = header.index("delayTime")

        if f.mode == 'r': #Start date, end date, and delays must be the same for every product.
            for row in csvReader:
                startDate = row[startDateIndex]
                endDate = row[endDateIndex]
                delay = int(row[delayTimeIndex])
        f.close()

        dt_start = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S")
        if(endDate == ""):
            dt_end = datetime.now()
        else:
            dt_end = datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S")
        queryDay = (dt_start + timedelta(seconds=delay* 30.0 * 60.0)).weekday()
        queryHour = (dt_start + timedelta(seconds=delay * 30.0 * 60.0)).hour

        if(dt_start > dt_end):
            print("*** End date is greater than start date ***")
            break
        elif(queryDay < 5 and (queryHour >= 5 and queryHour < 17)):
            os.system('python HistoricalData.py')
            time.sleep(60.1)
        else:
            with open("productList_historicalData.txt", "r") as file:
                filedata = file.read()

            oldStr = "," + str(delay) + ","
            newStr = "," + str(delay+2) + ","
            filedata = filedata.replace(oldStr, newStr)

            with open("productList_historicalData.txt", "w") as file:
                file.write(filedata)