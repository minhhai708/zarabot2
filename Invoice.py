import csv
import sys

from datetime import datetime


class Invoice():
    def __init__(self, date, order, amount, email):
        self.date = date
        self.order = order.replace('Order No. ', '')
        self.amount = amount.replace(" EUR", '')
        self.account = email

    def getDate(self):
        return self.date

    def getOrder(self):
        return self.order

    def getAmout(self):
        return self.amount

    def isOutdated(self, dateMin):
        """
            Check if invoice is outdated with a given date
        :param dateMin: a given date
        :return: False if invoice has date greater or equal minDate
        True if invoice has date is less than Mindate
        """
        try:
            format = '%m/%d/%Y'
            min_date = datetime.strptime(dateMin, format)
            inv_date = datetime.strptime(self.date, format)
            return inv_date < min_date
        except ValueError:
            print("ERROR DATE:" + dateMin + '-' + self.date)
            return False

    def export_csv(self, fout):
        """
        Export invoice info to csv file
        :param fout: file
        :return:
        """
        with open(fout, 'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='|', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([self.account, self.date, self.order, self.amount])

    def __str__(self):
        ret = self.date
        ret += '-' + self.order
        ret += '-' + self.amount
        return ret

#
#
# def main(argv):
#     inv = Invoice("9/24/2020", "Order No. 51781674323", "87.83 EUR")
#     print(inv.isOutdated("9/23/2020"))
#     print(inv.isOutdated("09/23/2020"))
#     print(inv.isOutdated("9/24/2020"))
#     print(inv.isOutdated("09/24/2020"))
#     print(inv.isOutdated("9/25/2020"))
#     print(inv.isOutdated("09/25/2020"))
#     print(inv)
#     return
#
#
# if __name__ == '__main__': sys.exit(main(sys.argv))
