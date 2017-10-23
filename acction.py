from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

WAIT_TIME = 2
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

    def getOrdersFromMenu(self, browser):
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

    def clickInvoices(self, browser):
        invoicesLink = "Invoices"
        try:
            WebDriverWait(browser, WAIT_TIME).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT,invoicesLink )))
            browser.find_element_by_partial_link_text(invoicesLink).click()
        except NoSuchElementException:
            print("NoSuchElementException- clickInvoices")

