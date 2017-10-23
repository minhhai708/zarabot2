import string
import csv

class Order(object):
    def __init__(self, date,orderNumber, totalValue, status,brand, client,email):
        self.date = date
        self.orderNumber = orderNumber
        self.totalValue = totalValue
        self.status = status
        self.brand = brand
        self.client = client
        self.email = email

    def getDate(self):
        return self.date

    def getOrderNum(self):
        return self.orderNumber

    def getOrderValue(self):
        return self.totalValue

    def getOrderStatus(self):
        return self.status

    def getOrderBrand(self):
        return self.brand

    def getOrderClient(self):
        return self.client

    def getOrderEmail(self):
        return self.email

    def __str__(self):
        return self.date +'\t' + self.orderNumber + '\t' + self.totalValue+ '\t'\
               + self.status + '\t' + self.brand+ '\t' + self.client

class OrderList(object):
    def __init__(self):
        self.orderList = []
        self.oldOrderlist = []

    #return orderList
    def getOrderList(self):
        return self.orderList
    #add an order to OrderList
    def addOrder(self, neworder):
        new = True
        for order in self.orderList:
            if (order.getOrderNum() == neworder.getOrderNum()):
                new = False
        for order in self.oldOrderlist:
            if (order.getOrderNum() == neworder.getOrderNum()):
                new = False
        if(new == True):
            self.orderList.append(neworder)

    def addOldOrder(self, oldOrder):
        self.oldOrderlist.append(oldOrder)

    def printOrder(self):
        for order in self.orderList:
            print(order)
    def getZaraOrder(self, rawText, client, email, brand):
        #rawText.replace('SEE DETAILS\n','')
        space = ' '
        newLine = '\n'
        lastOrder = False
        existOrder = True
        rawText = rawText[rawText.find(newLine)+1:]
        while (existOrder == True) :
            skipLine = False

            date = rawText[:rawText.find(space)]
            rawText = rawText[rawText.find(space)+1:]
            if (date == "SEE" and date == "Page"):
                skipLine = True

            order = rawText[:rawText.find(space)]
            rawText = rawText[rawText.find(space)+1:]
            #Shipped + Delivered
            status = rawText[:rawText.find(space)]
            rawText = rawText[rawText.find(space)+1:]

            if (status == "Being"): #Being prepared
                status =  status + rawText[:rawText.find(space)]
                rawText = rawText[rawText.find(space) + 1:]
            elif (status == "Partial"):#Partial delivery
                status =  status + rawText[:rawText.find(space)]
                rawText = rawText[rawText.find(space) + 1:]
            elif (status == "At"): #At the store
                status =  status + rawText[:rawText.find(space)]
                rawText = rawText[rawText.find(space) + 1:]

                status =  status + rawText[:rawText.find(space)]
                rawText = rawText[rawText.find(space) + 1:]


            value = rawText[:rawText.find(space)] #OrderValue
            rawText = rawText[rawText.find(space)+1:]
            if (value == "of"):
                skipLine = True

            coid = rawText[:rawText.find(space)] #EURO-moneda
            rawText = rawText[rawText.find(space)+1:]

            #check if we reach the last row
            if rawText.find(newLine) != -1:
                rawText = rawText[rawText.find(newLine)+1:]
            else:
                lastOrder = True
            if (lastOrder == True):
                existOrder = False

            if (skipLine == False):
                newOrder = Order(date,order,status,value,brand,client, email)
                print(newOrder)
                self.addOrder(newOrder)

    def orderWriter(self, outputfile):
        with open(outputfile,'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='|',quotechar='|', quoting=csv.QUOTE_MINIMAL)

            for order in self.getOrderList():
                spamwriter.writerow([order.getDate(),
                                     order.getOrderNum(),
                                     order.getOrderValue(),
                                     order.getOrderStatus(),
                                     order.getOrderBrand(),
                                     order.getOrderClient(),
                                     order.getOrderEmail()])

        return

    def orderReader(self, fileName):
        with open(fileName, 'a+') as csvfile:
            contentReader = csv.reader(csvfile, delimiter='|',quotechar = '|')
            for row in contentReader:
                #Date-OrderNum-Value-Status-BRand-Client-Email
                order = Order(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                self.addOldOrder(order)
        return

def test():
    outputfile = "orders.csv"
    content = "DATE NUMBER STATUS AMOUNT ACTIONS\n5/4/2017 344898419 Delivered 112.75 EUR\nSEE DETAILS\n" \
              "5/4/2017 344615638 Cancelled 39.85 EUR\nSEE DETAILS\n5/3/2017 344237880 Delivered 106.64 EUR\nSEE DETAILS\n" \
              "5/2/2017 343857972 Delivered 81.72 EUR\nSEE DETAILS\n5/1/2017 343337310 Delivered 153.65 EUR\nSEE DETAILS"
    listOrder = OrderList()
    listOrder.getZaraOrder(content, client="CHIC", email="haha@gmail.com", brand="ZARA")
    listOrder.orderWriter(outputfile)
