try:
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
    import os
    import boto3
    from datetime import datetime
    print("All Modules are ok ...")

except Exception as e:
    print("Error in Imports ")



class WebDriver(object):

    def __init__(self):
        self.options = Options()

        self.options.binary_location = '/opt/headless-chromium'
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--start-fullscreen')
        self.options.add_argument('--single-process')
        self.options.add_argument('--disable-dev-shm-usage')

    def get(self):
        driver = Chrome('/opt/chromedriver', options=self.options)
        return driver

# The Login bot function
def login_crawler(uname: str, pwd: str, url: str, driver) -> bool:
    driver.get(url)
    user = driver.find_element_by_css_selector("#UserLogin_username")
    user.clear()
    user.send_keys(uname)
    password = driver.find_element_by_css_selector("#UserLogin_password")
    password.clear()
    password.send_keys(pwd)
    btn = driver.find_element_by_css_selector("#login-submit")
    btn.click()
    return execution_crawler(driver)


# The Clockin/Clockout function
def execution_crawler(driver) -> bool:
    try:
        driver.implicitly_wait(2)
        emote = driver.find_element_by_xpath('//*[@id="5"]')
        emote.click()
        driver.implicitly_wait(2)
        submit = driver.find_element_by_xpath('//*[@id="plus-status-btn"]')
        submit.click()
        driver.implicitly_wait(2)
        js_statement = "document.querySelector('a#attendance-logger-widget').click();"
        driver.execute_script(js_statement)
        driver.quit()
        return True
    except:
        driver.implicitly_wait(2)
        js_statement = "document.querySelector('a#attendance-logger-widget').click();"
        driver.execute_script(js_statement)
        driver.quit()
        return True


# SNS Email notification function
def send_notification(status: bool) -> bool:
    sns_client = boto3.client(
        'sns',
        region_name=os.environ.get('REGION'),
        aws_access_key_id=os.environ.get('ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY')
    )
    topic_arn = 'arn:aws:sns:ap-south-1:807126171454:ts-attendace-bot-notifier'
    if not status:
        message = f"Attendance crawler failed to punch at {datetime.now().strftime('%H:%m:%S')}!! Please login and punch manually :)"
    else:
        message = f"Clock in at {datetime.now().strftime('%H:%m:%S')}" if datetime.now().hour < 12 else f"Clock out at {datetime.now().strftime('%H:%m:%S')}"
    sns_client.publish(TopicArn=topic_arn, Message=message, Subject=f"{datetime.now().strftime('%b-%d-%Y')}")


def lambda_handler(event, context):
     # Retrieving constants from environment variables
    link = os.environ.get("TS_LINK")
    username = os.environ.get("TS_USER")
    password = os.environ.get("TS_PASSWORD")
    
    instance_ = WebDriver()
    driver = instance_.get()
    bot_status = login_crawler(username, password, link, driver)
    return send_notification(bot_status)
