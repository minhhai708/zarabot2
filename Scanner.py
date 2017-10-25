
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from Order import OrderList
from Account import AccountList
import os
from Tools import Tools

WAIT_TIME =5
TRUE = 1
FALSE = 0

class Action():

    def move_NextPage(self, browser):
        nextpage = '_table-nav-next._prevPage.icon-arrow-right'
        isFinalPage = FALSE
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, nextpage)))
            browser.find_element_by_class_name(nextpage).click()
            return isFinalPage
        except TimeoutException as e:
            print("MOVE TO FINAL PAGE")
            isFinalPage = TRUE
            return isFinalPage
        except NoSuchElementException:
            print("NoSuchElementException- move_NextPage")
            isFinalPage = TRUE
            return isFinalPage

    def clickOrderAndReturns(self, browser):
        orderText = "ORDERS AND RETURNS"
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,orderText )))
            browser.find_element_by_partial_link_text(orderText).click()
        except NoSuchElementException:
            print("NoSuchElementException- clickOrderAndReturns")
            return

    def logIn(self, browser, email, password):
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.presence_of_all_elements_located((By.ID, 'sign-in-form')))
            emailUser = browser.find_element_by_id('email')  # Find the search box
            passwordUser = browser.find_element_by_id('password')
            print("Log in :" +email)
            emailUser.send_keys(email)
            passwordUser.send_keys(password + Keys.RETURN)
        except NoSuchElementException:
            print("Unable to login "+ email)
            return
        except TimeoutException:
            return
    def clickAccountMenu(self, browser):
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, '_accountLink._userName')))
            browser.find_element_by_class_name('_accountLink._userName').click()
        except NoSuchElementException:
            print("NoSuchElementException- clickAccountMenu")
            return
        except TimeoutException:
            print("TimeoutException- clickAccountMenu")
            return
    def clickLogIn(self, browser):
        loginLink = '_accountLink._login'
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, loginLink)))
            browser.find_element_by_class_name(loginLink).click()
        except NoSuchElementException:
            print("NoSuchElementException- clickLogIn")
            return
        except TimeoutException:
            print("TIME OUT")
            return
    def clickLogOut(self, browser):
        logOutLink = '_accountLink._logout'
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, logOutLink)))
            browser.find_element_by_class_name(logOutLink).click()
        except NoSuchElementException:
            print("NoSuchElementException- clickLogOut")
            return
    def accessMenuOrder(self, browser):
        ordersInfo = 'content-dotted-table.order-list-table'
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, ordersInfo)))
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, ordersInfo)))
            order = browser.find_element_by_class_name(ordersInfo)
            return order.text
        except TimeoutException:
            print("TIME OUT")
        except NoSuchElementException:
            print("NoSuchElementException- accessMenuOrder")
            return

    def getAccountInfo(self, browser, account,listOrders):
        self.clickLogIn(browser)
        self.logIn(browser, account.getEmail(),account.getPassword())
        self.clickAccountMenu(browser)
        self.clickOrderAndReturns(browser)
        isFinalPage = FALSE
        scanPage = 0
        cont = True
        while(isFinalPage == FALSE and cont == True):
            content = self.accessMenuOrder(browser)
            if (content is None):
                cont = False
            else:
                if (scanPage == 30):
                    break
                listOrders.getZaraOrder(content,client =account.getNick(), brand=account.getBrand(),email=account.getEmail())
                isFinalPage = self.move_NextPage(browser)
                scanPage = scanPage +1

        self.clickLogOut(browser)

    def orderScanner(self):
        first_page= 'https://www.zara.com/es/en/'
        accountFile = 'AccountList.csv'
        outfile =  'OrderList.csv'

        listOrders= OrderList()
        listOrders.orderReader(outfile)
        #Open First Page
        browser = webdriver.Firefox()
        browser.get(first_page)
        #create list of account from a file
        accList = AccountList()
        accList.accGetter(accountFile)
        #Scan all account and save order scanned in listOrders
        for acc in accList.getAccList():
            self.getAccountInfo(browser, acc,listOrders)
        #Save all scanned orders in a file
        listOrders.orderWriter(outfile)
        #close browser
        browser.close()
        return

    def clickInvoices(self, browser):
        invoicesLink = "Invoices"
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,invoicesLink )))
            browser.find_element_by_partial_link_text(invoicesLink).click()
        except NoSuchElementException:
            print("NoSuchElementException- clickInvoices")
            return
        except TimeoutException:
            print("TIME OUT-clickInvoices")
        return

    def clickDownloadInvoice(self, browser, dateLimit,dateFormat):
        invoicesDownload = "button-primary.button-medium._invoice-download"
        downloadText = "Download"
        contentTable = "content-dotted-table.invoice-list-table"
        tbodyTAG = "tbody"
        moreInvoice = True
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, contentTable)))
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,downloadText)))
            tbodyEle = browser.find_element_by_tag_name(tbodyTAG)
            links = browser.find_elements_by_class_name(invoicesDownload)
            linkList = Tools.zaraGetDownloadIndexByDate(tbodyEle.text, dateLimit,dateFormat)
            if not linkList:
                moreInvoice = False
                return moreInvoice
            for linkIndex in linkList:
                print("Downloading " + tbodyEle.text.splitlines()[linkIndex])
                attempt = 0
                try:
                    links[linkIndex].click()
                except StaleElementReferenceException:
                    links[linkIndex].click()

            return moreInvoice
            #for l in links:
            #    l.click()
        except TimeoutException:
            print("TIME OUT-clickDownloadInvoice")
            return
        except NoSuchElementException:
            print("NO ELEMENT-here")
            return

    def clickNextInvoicePage(self, browser):
        nextpage = 'icon-arrow-right._table-nav-next._prevPage'
        isFinalPage = False
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.CLASS_NAME, nextpage)))
            browser.find_element_by_class_name(nextpage).click()
            return isFinalPage
        except TimeoutException as e:
            print("MOVE TO FINAL PAGE")
            isFinalPage = True
            return isFinalPage
        except NoSuchElementException:
            print("NoSuchElementException- move_NextPage")
            isFinalPage = True
            return isFinalPage

    def getInvoiceByAccount(self, browser, account, dateLimit):
        isFinalPage = False
        moreInvoice = True
        self.clickLogIn(browser)
        self.logIn(browser, account.getEmail(), account.getPassword())
        self.clickAccountMenu(browser)
        self.clickInvoices(browser)

        while isFinalPage == False and moreInvoice == True:
            moreInvoice = self.clickDownloadInvoice(browser, dateLimit, dateFormat='%m/%d/%Y')
            isFinalPage = self.clickNextInvoicePage(browser)

        self.clickLogOut(browser)

        return


    def invoiceDownloader(self):

        profile = webdriver.FirefoxProfile()

        profile.set_preference('browser.download.dir', "/home/hai/Desktop/test")
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference("browser.helperApps.alwaysAsk.force", False);
        profile.set_preference("browser.download.manager.showWhenStarting", False);
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', ("application/PDF"))

        first_page = 'https://www.zara.com/es/en/'
        accountFile = 'AccountList.csv'

        browser = webdriver.Firefox(profile)
        #somethine = input("Your age? ")
        browser.get(first_page)
        # create list of account from a file
        accList = AccountList()
        accList.accGetter(accountFile)
        input("Please check autoDownload pdf")
        for account in accList.getAccList():
            self.getInvoiceByAccount(browser, account, "07/01/2017")
        browser.close()

acction = Action()
acction.invoiceDownloader()

