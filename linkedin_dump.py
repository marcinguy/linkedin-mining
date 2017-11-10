# coding=utf-8
import pprint
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import mysql.connector

from random import randint

from bs4 import BeautifulSoup

import logging
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
import re

import argparse

# create logger with 'spam_application'
logger = logging.getLogger('linkedin-miner')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('miner.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

def monthToNum(shortMonth):

  return{
        'January' : 1,
        'February' : 2,
        'March' : 3,
        'April' : 4,
        'May' : 5,
        'June' : 6,
        'July' : 7,
        'August' : 8,
        'September' : 9, 
        'October' : 10,
        'November' : 11,
        'December' : 12
  }[shortMonth]

def remove_html_markup(s):
    tag = False
    quote = False
    out = ""

    for c in s:
        if c == '<' and not quote:
            tag = True
        elif c == '>' and not quote:
            tag = False
        elif (c == '"' or c == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + c

    return out


def update_db(p_id, field, text):
    p_id = str(p_id)
    logger.debug("Updating database")
    # Open database connection
    try:
        db = mysql.connector.connect(user='root', password='root',
                                     host='localhost',
                                     database='linkedin_miner')

        # prepare a cursor object using cursor() method
        cursor = db.cursor()

        sql = "UPDATE samplesheet set " + field + "=%s where p_id=%s"

        data = (text, p_id)

        # Execute the SQL command
        cursor.execute(sql, data)
        db.commit()
        logger.debug("SQL query:" + cursor.statement)
    except Exception as error:
        logger.debug(error)
    finally:
        cursor.close()
        db.close()


def search(name, p_id):
    global driver
    sleeptime = randint(0, 60)
    logger.debug("Sleeping for:" + str(sleeptime) + "secs\n")
    sleep(sleeptime)
    logger.debug("Searching: " + name + "\n")
    sleep(5)
    # Search for people
    try:
        dropdown_button = driver.find_element_by_xpath(
            "/html[@class='os-linux']/body[@id='pagekey-oz-winner']/div[@id='header']/div[@id='top-header']/div[@class='wrapper']/div[@class='header-section first-child']/form[@id='global-search']/fieldset/div[@id='control_gen_2']/span[@class='label']/span[@class='styled-dropdown-select-all']")
        dropdown_button.click()
        sleep(3)
        dropdown_item = driver.find_element_by_xpath(
            "/html[@class='os-linux']/body[@id='pagekey-oz-winner']/div[@id='header']/div[@id='top-header']/div[@class='wrapper']/div[@class='header-section first-child']/form[@id='global-search']/fieldset/div[@id='control_gen_2']/ul[@class='search-selector']/li[@class='people option']")
        dropdown_item.click()
        sleep(3)
        search_field = driver.find_element_by_xpath(
            "/html[@class='os-linux']/body[@id='pagekey-oz-winner']/div[@id='header']/div[@id='top-header']/div[@class='wrapper']/div[@class='header-section first-child']/form[@id='global-search']/fieldset/div[@id='search-box-container']/span[@id='search-autocomplete-container']/span[@class='twitter-typeahead']/input[@id='main-search-box']")
        search_field.send_keys(name)
        search_field.send_keys(Keys.ENTER)
        sleep(10)
    except Exception as e:
        print e
        logger.debug("Something went wrong...")
        update_db(p_id, "Status", "review")
        driver.get("https://linkedin.com")
        return
    try:
        result_no = driver.find_element_by_xpath(".//*[@id='results_count']/div/p")
        sleep(3)
        result_no = result_no.get_attribute('innerHTML')
        sleep(2)
        ret = result_no.find("<strong>1</strong>")
    except Exception as e:
        ret = -1

    # print ret
    if (ret >= 0):
        try:
            sleep(5)
            user = driver.find_element_by_xpath(
                "/html[@class='os-linux']/body[@id='pagekey-voltron_people_search_internal_jsp']/div[@id='body']/div[@class='wrapper hp-nus-wrapper']/div[@id='srp_main_']/div[@id='srp_container']/div[@id='results-col']/div[@id='results-container']/ol[@id='results']/li[@class='mod result idx%d people']/div[@class='bd']/h3/a[@class='title main-headline']" % 1)
            user_name = user.get_attribute('innerHTML')
            # print user_name
            sleep(6)
            user.click()

            sleeptime = randint(0, 60)
            logger.debug("Sleeping for:" + str(sleeptime) + "secs\n")
            sleep(sleeptime)
            update_db(p_id, "Status", "complete")

            try:
                user_summary = driver.find_element_by_xpath(
                    "/html[@class='os-linux']/body[@id='pagekey-nprofile_view_nonself']/div[@id='body']/div[@class='wrapper hp-nus-wrapper']/div[@id='wrapper']/div[@id='profile']/div[@id='background']/div[@class='background-content ']/div[@id='background-summary-container']/div[@id='background-summary']/div[@id='summary-item']/div[@id='summary-item-view']/div[@class='summary']/p[@class='description']")
                user_summary_html = user_summary.get_attribute('innerHTML')
                # logger.debug(user_summary_html)
                soup = BeautifulSoup(user_summary_html, "lxml")
                for script in soup(["script", "style"]):
                    script.extract()  # rip it out
                user_summary_text = soup.get_text(separator='\n')
                sleeptime = randint(0, 10)
                logger.debug("Sleeping for:" + str(sleeptime) + "secs\n")
                sleep(sleeptime)
            except Exception as e:
                print e
                logger.debug("Summary missing!")
                user_summary_text = ""
                user_summary_html = ""
            try:
                sleep(2)
                link = driver.find_element_by_xpath(".//*[@id='top-card']/div/div[2]/div[2]/ul/li[1]/dl/dd/a")
                sleep(2)
                link_html = link.get_attribute('innerHTML')
                update_db(p_id, "Website", link_html)
                sleep(5)
            except Exception as e:
                print e
                logger.debug("Link missing!. Looking second location")
                sleep(2)
                try:
                    link = driver.find_element_by_xpath(".//*[@id='top-card']/div/div[2]/div/ul/li[1]/dl/dd/a")
                    sleep(2)
                    link_html = link.get_attribute('innerHTML')
                    update_db(p_id, "Website", link_html)
                    sleep(5)
                except Exception as e:
                    print e
                    logger.debug("Link missing!. Giving up")

            try:

                user_experience = driver.find_element_by_xpath(
                    "/html[@class='os-linux']/body[@id='pagekey-nprofile_view_nonself']/div[@id='body']/div[@class='wrapper hp-nus-wrapper']/div[@id='wrapper']/div[@id='profile']/div[@id='background']/div[@class='background-content ']/div[@id='background-experience-container']/div[@id='background-experience']")
                user_experience_html = user_experience.get_attribute('innerHTML')
                # logger.debug(user_experience_html)

                soup = BeautifulSoup(user_experience_html, "lxml")
                for script in soup(["script", "style"]):
                    script.extract()  # rip it out
                user_experience_text = soup.get_text(separator='\n')
                 
                tenure_duration = user_experience_text.splitlines()[3]+" "+user_experience_text.splitlines()[4]
                
                if "Present" in tenure_duration:
                  start = tenure_duration.split("–")
                  datestr=start[0].strip()
                  mon = datestr.split(" ")[0]
                  try:
                    year = datestr.split(" ")[1]
                  except:
                    mon="January"
                    year=datestr.split(" ")[0]

                  mon_n= monthToNum(mon)
                  datestr = str(mon_n)+"/1/"+str(year)


                update_db(p_id, "Resume_Text", user_summary_text + user_experience_text)
                update_db(p_id, "Resume_Text_Html", user_summary_html + user_experience_html)
                sleep(5)
              
                update_db(p_id, "Duration", tenure_duration) 
                  
                update_db(p_id,"Start",datestr)


                update_db(p_id, "Status", "complete")

            except Exception as e:
                print e
                logger.debug("Experience missing!")

            sleeptime = randint(0, 10)
            logger.debug("Sleeping for:" + str(sleeptime) + "secs\n")
            sleep(sleeptime)

            try:
                official_title = driver.find_element_by_xpath(".//*[@id='headline']/p")

                official_title_html = official_title.get_attribute('innerHTML')
                update_db(p_id, "Official_Title", official_title_html)
                sleep(5)

                company = official_title_html.split("at")
                company = company[1].strip()
                if not company:
                    update_db(p_id, "Company", company[1].strip())
                sleep(5)
            except Exception as e:
                print e
                logger.debug("Official title missing or non stanard!")

            titles = list()
            companies = list()

            for a in soup.findAll('a'):
                href = a['href']
                if ("mprofile_title" in href):
                    titles.append(a.contents[0])
                if ("prof-exp-company-name" in href):
                    company_html = str(a.contents[0])
                    company = remove_html_markup(company_html)
                    companies.append(company)

            prev_official_title = str(titles.pop(1))

            update_db(p_id, "Previous_Official_Title", prev_official_title)

            i = 0
            company_str = ""
            for company in companies:
                if (i > 1):
                    company_str = company_str + company + "\n"
                i = i + 1

            update_db(p_id, "Prior_Companies", company_str)

            try:

                phone = driver.find_element_by_xpath(".//*[@id='contact-comments-view']/p")
                phone_html = phone.get_attribute('innerHTML')
                results = re.findall(
                    "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})",
                    phone_html)
                phone_html_only_digits = ""
                for x in results:
                    phone_html_only_digits += str(x) + " "
                update_db(p_id, "Work_phone", phone_html_only_digits)
                sleep(5)

                email = driver.find_element_by_xpath(".//*[@id='contact-comments-view']/p")
                email_html = email.get_attribute('innerHTML')
                results = re.search(r'[\w\.-]+@[\w\.-]+', email_html)
                email_match = results.group(0)
                update_db(p_id, "Personal_Email_1", email_match)
                sleep(5)

            except:
                logger.debug("Contact info (Work Phone and/or Personal Email 1) missing!")
                driver.execute_script("window.history.go(-2)")

            driver.execute_script("window.history.go(-2)")
        except:
            logger.debug("Fields missing. Skipping!")
            update_db(p_id, "Status", "review")
            driver.execute_script("window.history.go(-1)")

    else:
        update_db(p_id, "Status", "review")
        logger.debug("0 results or Too many people. Skipping!")
        driver.execute_script("window.history.go(-1)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LinkedIn Dump v0.99')
    parser.add_argument('-u', '--user', help='username', required=True)
    parser.add_argument('-p', '--passwd', help='password', required=True)
    args = parser.parse_args()
    username = args.user
    password = args.passwd

fp = webdriver.FirefoxProfile()
fp.add_extension(extension='/home/marcin/linkedin-miner/firebug.xpi')
fp.set_preference("extensions.firebug.currentVersion", "2.0.17")
fp.set_preference("extensions.firebug.onByDefault", True)
driver = webdriver.Firefox(firefox_profile=fp,timeout=60)

driver.get("https://linkedin.com/uas/login")

emailElement = driver.find_element_by_id("session_key-login")
emailElement.send_keys(username)
passElement = driver.find_element_by_id("session_password-login")
passElement.send_keys(password)
passElement.submit()

logger.debug("Logging in to LinkedIn\n")

# Open database connection
db = mysql.connector.connect(user='root', password='root',
                             host='localhost',
                             database='linkedin_miner')

# prepare a cursor object using cursor() method
cursor = db.cursor()

# Prepare SQL query to INSERT a record into the database.
sql = "SELECT * FROM samplesheet where status='pending'"

# Execute the SQL command
cursor.execute(sql)
# Fetch all the rows in a list of lists.
results = cursor.fetchall()
i = 0
for row in results:
    if (i == 1000):
        i = 0
        logger.debug("Sleeping for 8h...")
        sleep(8 * 60 * 60)

    person = row[0]
    company = row[6]
    location = row[3]
    p_id = row[43]
    # Processed
    p_person = person.split(",")
    p_person = p_person[1].strip() + " " + p_person[0].strip()
    try:
        p_location = location.split(",")
        p_location = p_location[0]
    except:
        p_location = ""

    if not p_location:
        if not company:
            search(p_person, p_id)
        else:
            search(p_person + "," + company, p_id)
    else:
        if not company:
            search(p_person + "," + p_location, p_id)
        else:
            search(p_person + "," + p_location + "," + company, p_id)

    i = i + 1

db.close()
exit();
