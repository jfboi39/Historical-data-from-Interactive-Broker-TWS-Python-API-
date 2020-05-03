import os
import time
import csv
from datetime import datetime, timedelta, date

if __name__ == "__main__":
    i = 0
    while i < 8000:
        f = open("productList_historicalData.txt", "r")
        csvReader = csv.reader(f)
        header = next(csvReader)
        startDateIndex = header.index("startDate")
        delayTimeIndex = header.index("delayTime")

        if f.mode == 'r':
            for row in csvReader:
                startDate = row[startDateIndex]
                delay = int(row[delayTimeIndex])
        f.close()

        dt = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S")
        #queryTime = (dt + timedelta(seconds=delay * 30.0 * 60.0)).strftime("%Y%m%d %H:%M:%S") # 30 minutes step.
        queryDay = (dt + timedelta(seconds=delay* 30.0 * 60.0)).weekday()
        queryHour = (dt + timedelta(seconds=delay * 30.0 * 60.0)).hour

        if queryDay < 5 and queryHour >= 5 and queryHour < 17:
            #print("OS: ",i)
            os.system('python HistoricalData.py')
            i += 1
            time.sleep(60.1)
        else:
            with open("productList_historicalData.txt", "r") as file:
                filedata = file.read()

            oldStr = "," + str(delay) + ","
            newStr = "," + str(delay+2) + ","
            filedata = filedata.replace(oldStr, newStr)

            with open("productList_historicalData.txt", "w") as file:
                file.write(filedata)