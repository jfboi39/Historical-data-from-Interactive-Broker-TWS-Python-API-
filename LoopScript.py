import os
import time
import csv
import sys
from datetime import datetime, timedelta, date

updateDelay = {}

class HandleUpdateDelay():
    def __init__(self):
        self.previousString = ""
        self.newString = ""

    def updateElement(self,previousStringV,newStringV):
        self.previousString = previousStringV
        self.newString = newStringV

def evaluateTimeStamp(productV, startDateV, endDateV, delayV):
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

        if(delayV < 0 or dt_start_adj >= dt_end):
            break
        if (queryDay <= 3 or (queryDay == 4 and queryHour <= 17) or (queryDay == 6 and queryHour >= 17)): # Friday = 4
            condition = False
        else:
            stepCount += 2

    oldStr = str(productV) + "," + str(delayV) + ","
    newStr = str(productV) + "," + str(delayV + stepCount) + ","
    updateDelay[productV].updateElement(oldStr,newStr)

    if(delayV < 0 or dt_start_adj >= dt_end): #Out-of-scope; no datastream required.
        return 0
    else:
        return 1

if __name__ == "__main__":
    condition = True

    f = open("productList_historicalData.txt", "r")
    csvReader = csv.reader(f)
    header = next(csvReader)
    uniqueIDIndex = header.index("uniqueID")

    if f.mode == 'r':
        for row in csvReader:
            updateDelay.update({row[uniqueIDIndex]: HandleUpdateDelay()})
    f.close()
    #Create mapping to update delays for skipping overnights and weekend.

    while condition:
        f = open("productList_historicalData.txt", "r")
        csvReader = csv.reader(f)

        header = next(csvReader)
        uniqueIDIndex = header.index("uniqueID")
        startDateIndex = header.index("startDate")
        endDateIndex = header.index("endDate")
        delayTimeIndex = header.index("delayTime")

        sumValidRequest = 0
        if f.mode == 'r':
            for row in csvReader:
                #print(row[uniqueIDIndex],row[startDateIndex],row[endDateIndex],int(row[delayTimeIndex]))
                sumValidRequest += evaluateTimeStamp(row[uniqueIDIndex],row[startDateIndex],row[endDateIndex],int(row[delayTimeIndex]))
        f.close()
        #Evaluate how many data streams need to be opened.

        if sumValidRequest == 0:
            sys.exit("No datastream required")
        #Stop the script if there is nothing to request.

        with open("productList_historicalData.txt", "r") as file:
            filedata = file.read()
        file.close()

        with open("productList_historicalData.txt", "w") as file:
            for key in updateDelay:
                filedata = filedata.replace(updateDelay[key].previousString,updateDelay[key].newString)

            file.write(filedata)
        #Update the delays to skip overnights and weekends.

        print(datetime.now())
        if(sumValidRequest > 15):
            sys.exit("Number of products greater than 15")
        time.sleep((2.0 * 2.0 * sumValidRequest) / 60.0 * (10.0 * 60.0) + 10.1)
        os.system('python HistoricalData.py')
        #No more than 60 requests within any ten minute period; BID_ASK is counted as twice and we request 2x 30 minutes.