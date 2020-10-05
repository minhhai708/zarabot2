from datetime import datetime
import csv


WAIT_TIME =5
TRUE = 1
FALSE = 0
UNSUCCESSFUL = -1
SUCCESSFUL = 1

class Tools():
    @staticmethod
    def compareDate(date1, date2, format):
        try:
            date1_Obj = datetime.strptime(date1, format)
            date2_Obj = datetime.strptime(date2, format)
            if date1_Obj > date2_Obj:
                return 1
            elif date1_Obj == date2_Obj:
                return 0
            else:
                return -1
        except ValueError:
            return -1

    #return a list of download link that has date
    @staticmethod
    def zaraGetDownloadIndexByDate(invoicePage, dateMax):
        dateformat = '%m/%d/%Y'
        count = 0
        countline = 0
        downloadList = []
        separation = "\n"
        for line in invoicePage.splitlines():
            countline = countline + 1
            if (countline % 4) == 2: #the second line is date's line
                line.partition(separation)
                date = line.partition(separation)[0]
                #If exist any order that has date is greater than dateMax return true
                if Tools.compareDate(date, dateMax,dateformat ) != -1:
                    downloadList.append(count)
                count = count + 1

        return downloadList

    @staticmethod
    def invoiceWriter(account, line, outputfile):
        with open(outputfile, 'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='|', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([account.getEmail(), line])

    @staticmethod
    def account(account, line, outputfile):
        with open(outputfile, 'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='|', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([account.getEmail(), line])
