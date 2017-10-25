from datetime import datetime

class Tools():
    @staticmethod
    def compareDate(date1, date2, format):
        date1_Obj = datetime.strptime(date1, format)
        date2_Obj = datetime.strptime(date2, format)
        if date1_Obj > date2_Obj:
            return 1
        elif date1_Obj == date2_Obj:
            return 0
        else:
            return -1

    #return a list of download link that has date
    @staticmethod
    def zaraGetDownloadIndexByDate(invoicePage, dateMax, dateformat):
        count = 0
        downloadList = []
        separation = " "
        for line in invoicePage.splitlines():
            line.partition(separation)
            date = line.partition(separation)[0]
            #If exist any order that has date is greater than dateMax return true
            if Tools.compareDate(date, dateMax,dateformat ) != -1:
                downloadList.append(count)
            count = count + 1

        return downloadList

    @staticmethod
    def test():
        dateString= "7/22/2017 375556694 99.89 EUR DOWNLOAD\n7/20/2017 374798168 106.88 EUR DOWNLOAD\n" \
              "7/20/2017 374740581 88.83 EUR DOWNLOAD\n7/19/2017 374565283 267.10 EUR DOWNLOAD\n" \
              "7/17/2017 372825024 125.86 EUR DOWNLOAD\n"
        maxDate = "7/17/2017"
        print(Tools.zaraGetDownloadIndexByDate(dateString,maxDate, '%m/%d/%Y'))
