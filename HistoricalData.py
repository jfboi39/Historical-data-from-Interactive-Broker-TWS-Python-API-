from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import *
from ibapi.ticktype import TickTypeEnum
from ibapi.order import *
from ibapi.common import *
from ibapi.order_state import *
from threading import Timer
from datetime import datetime, timedelta, date
from ContractSamples import ContractSamples
import csv
import math
import time
import atexit
import sys

contract = {}
marketRequestId = {}
initialDelay = 0
delay = 0
startDate = "2020-12-31 00:00:00"
currentFilename = None

class App(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def historicalData(self, reqId:int, bar: BarData):
        strFilename = str(marketRequestId[reqId]) + ".txt"
        f = open(strFilename, "a")
        f.write("%s,%s,BID,%f,%f,\n" % (bar.date,marketRequestId[reqId],bar.open,bar.close))
        f.close()

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd ", reqId, "from", start, "to", end)

    def start(self):
        self.importProductList()
        requestID = 0
        #CANNOT DO THE FOLLOWING:
        #Making identical historical data requests within 15 seconds.
        #Making six or more historical data requests for the same Contract, Exchange and Tick Type within two seconds.
        #Making more than 60 requests within any ten minute period. (BID_ASK is counted as twice).
        # (30+31+30+31+31+30)*24*2 = 8,784 requests/product
        global delay, initialDelay
        initialDelay = delay
        while initialDelay > (delay - 2):
            for productName in contract:
                dt = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S")
                queryTime = (dt + timedelta(seconds=delay*30.0*60.0)).strftime("%Y%m%d %H:%M:%S") #30 minutes step.
                requestID += 1
                self.reqHistoricalData(requestID, contract[productName], queryTime, "1800 S", "1 secs", "BID_ASK", 1, 1, False, [])
                marketRequestId.update({requestID: productName})
                #print(requestID,queryTime,marketRequestId[requestID])
                #self.cancelHistoricalData(requestID)
            delay += 1
        self.modifyProductList()
        time.sleep(10.1) #We need to wait for processing the request.
        self.disconnect()

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("nextValidOrderId: ", self.nextValidOrderId)
        self.start()

    def importProductList(self):
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
        delayTimeIndex = header.index("delayTime")

        if f.mode == 'r':
            for row in csvReader:
                contract.update({row[uniqueIDIndex]: Contract()})
                contract[row[uniqueIDIndex]].symbol = row[symbolIndex]
                contract[row[uniqueIDIndex]].secType = row[securityIndex]
                contract[row[uniqueIDIndex]].exchange = row[exchangeIndex]
                contract[row[uniqueIDIndex]].currency = row[currencyIndex]
                contract[row[uniqueIDIndex]].lastTradeDateOrContractMonth = row[expirationIndex]
                contract[row[uniqueIDIndex]].multiplier = row[multiplierIndex]
                global startDate, delay
                startDate = row[startDateIndex]
                delay = int(row[delayTimeIndex])
        f.close()

    def modifyProductList(self):
        with open("productList_historicalData.txt", "r") as file :
            filedata = file.read()

        oldStr = "," + str(initialDelay) + ","
        newStr = "," + str(delay) + ","
        filedata = filedata.replace(oldStr, newStr)

        with open("productList_historicalData.txt", "w") as file:
            file.write(filedata)

if __name__ == "__main__":
    app = App()
    app.connect("127.0.0.1", 8658, clientId=14)
    app.run()