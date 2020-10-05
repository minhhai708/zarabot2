import csv


class Account(object):
    def __init__(self, nick, brand, email, pwd):
        self.nick = nick
        self.email = email
        self.pwd = pwd
        self.brand = brand
        self.lastCheck = ""

    def getEmail(self):
        return self.email

    def getPassword(self):
        return self.pwd

    def getBrand(self):
        return self.brand

    def getNick(self):
        return self.nick

    def __str__(self):
        return self.nick + "-" + self.brand + "-" + self.email + "-" + self.pwd


class AccountList(object):
    def __init__(self, fileName):
        self.listAcc = []
        with open(fileName) as csvfile:
            contentReader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in contentReader:
                account = Account(row[0], row[1], row[2], row[3])
                self.listAcc.append(account)

    def getAccList(self):
        return self.listAcc
