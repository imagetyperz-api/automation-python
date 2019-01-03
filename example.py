from imagetyperzapi2 import ImageTyperzAPI
try:
    from selenium import webdriver
except:
    raise Exception('selenium package missing. Install with: pip install selenium')
try:
    import requests as req
except:
    raise Exception('requests package missing. Install with: pip install requests')
try:
    from lxml import html
except:
    raise Exception('lxml package missing. Install with: pip install lxml')

from time import sleep

# ----------------------------------------------------------
# credentials
IMAGETYPERS_TOKEN = 'your_access_token'

# recaptcha test page
TEST_PAGE_NORMAL = 'https://imagetyperz.xyz/automation/recaptcha-v2.html'
TEST_PAGE_INVISIBLE = 'https://imagetyperz.xyz/automation/recaptcha-invisible.html'
# ----------------------------------------------------------

# browser (selenium) test
def browser_test_normal():
    print '[=] BROWSER TEST STARTED (NORMAL RECAPTCHA) [=]'
    d = webdriver.Chrome()      # open browser
    try:
        d.get(TEST_PAGE_NORMAL)               # go to test page
        # complete regular info
        d.find_element_by_name('username').send_keys('get-this-user')
        d.find_element_by_name('password').send_keys('mypassword')

        print '[+] Completed regular info'

        # get sitekey from page
        site_key = d.find_element_by_class_name('g-recaptcha').get_attribute('data-sitekey')
        print '[+] Site key: {}'.format(site_key)

        # complete captcha
        print '[+] Waiting for recaptcha to be solved ...'
        i = ImageTyperzAPI(IMAGETYPERS_TOKEN)
        recaptcha_params = {
            'page_url': TEST_PAGE_NORMAL,
            'sitekey': site_key,
            'type': 1  # normal (v2)
        }
        recaptcha_id = i.submit_recaptcha(recaptcha_params)      # submit recaptcha
        while i.in_progress(recaptcha_id):      # check if still in progress
            sleep(10)       # every 10 seconds
        g_response_code = i.retrieve_recaptcha(recaptcha_id)        # get g-response-code
        
        #g_response_code = raw_input('CODE:')

        print '[+] Got g-response-code: {}'.format(g_response_code) # we got it
        javascript_code = 'document.getElementById("g-recaptcha-response").innerHTML = "{}";'.format(g_response_code)
        d.execute_script(javascript_code)       # set g-response-code in page (invisible to the 'naked' eye)
        print '[+] Code set in page'

        # submit form
        d.find_element_by_tag_name('form').submit()     # submit form
        print '[+] Form submitted'
        print '[+] Page source: {}'.format(d.page_source)     # show source
        sleep(10)
    finally:
        d.quit()        # quit browser
        print '[=] BROWSER TEST FINISHED [=]'

# requests test
def requests_test_normal():
    print '[=] REQUESTS TEST STARTED (NORMAL RECAPTCHA) [=]'
    try:
        print '[+] Getting sitekey from test page...'
        resp = req.get(TEST_PAGE_NORMAL)      # make request and get response
        tree = html.fromstring(resp.text)                               # init tree for parsing
        site_key = tree.xpath('//div[@class="g-recaptcha"]')[0].attrib['data-sitekey']  # get sitekey
        # get url for submission (not needed with browser automation)
        submission_endpoint = '{}/{}'.format('/'.join(TEST_PAGE_NORMAL.split('/')[:-1]), tree.xpath('//form')[0].attrib['action'])
        print '[+] Site key: {}'.format(site_key)
        print '[+] Submission endpoint: {}'.format(submission_endpoint)

        # solve captcha
        print '[+] Waiting for recaptcha to be solved ...'
        i = ImageTyperzAPI(IMAGETYPERS_TOKEN)
        recaptcha_params = {
            'page_url': TEST_PAGE_NORMAL,
            'sitekey': site_key,
            'type': 1  # normal (v2)
        }
        recaptcha_id = i.submit_recaptcha(recaptcha_params)      # submit recaptcha
        while i.in_progress(recaptcha_id):      # check if still in progress
            sleep(10)       # every 10 seconds
        g_response_code = i.retrieve_recaptcha(recaptcha_id)        # get g-response-code

        #g_response_code = raw_input('CODE:')
        
        print '[+] Got g-response-code: {}'.format(g_response_code)  # we got it

        # make request with data
        resp = req.post(submission_endpoint, data={
            'username' : 'get-this-user',
            'password' : 'mypassword',
            'g-recaptcha-response' : g_response_code
            }
        )
        print '[+] Form submitted'
        print '[+] Response: {}'.format(resp.text.encode('utf-8'))

    finally:
        print '[=] REQUESTS TEST FINISHED [=]'

# browser (selenium) test - invisible
def browser_test_invisible():
    print '[=] BROWSER TEST STARTED (INVISIBLE RECAPTCHA) [=]'
    d = webdriver.Chrome()      # open browser
    try:
        d.get(TEST_PAGE_INVISIBLE)               # go to test page
        # complete regular info
        d.find_element_by_name('username').send_keys('get-this-user')
        d.find_element_by_name('password').send_keys('mypassword')

        print '[+] Completed regular info'

        # get sitekey from page
        site_key = d.find_element_by_class_name('g-recaptcha').get_attribute('data-sitekey')
        data_callback = d.find_element_by_class_name('g-recaptcha').get_attribute('data-callback')
        print '[+] Site key: {}'.format(site_key)
        print '[+] Callback method: {}'.format(data_callback)

        # complete captcha
        print '[+] Waiting for recaptcha to be solved ...'
        i = ImageTyperzAPI(IMAGETYPERS_TOKEN)
        recaptcha_params = {
            'page_url': TEST_PAGE_INVISIBLE,
            'sitekey': site_key,
            'type': 2  # invisible
        }
        recaptcha_id = i.submit_recaptcha(recaptcha_params)      # submit recaptcha
        while i.in_progress(recaptcha_id):      # check if still in progress
            sleep(10)       # every 10 seconds
        g_response_code = i.retrieve_recaptcha(recaptcha_id)        # get g-response-code

        print '[+] Got g-response-code: {}'.format(g_response_code) # we got it

        # submit form
        js = '{}("{}");'.format(data_callback, g_response_code)
        d.execute_script(js)

        print '[+] Form submitted (through JavaScript)'
        sleep(10)
    finally:
        d.quit()        # quit browser
        print '[=] BROWSER TEST FINISHED [=]'

# requests test - invisible
def requests_test_invisible():
    print '[=] REQUESTS TEST STARTED (INVISIBLE RECAPTCHA) [=]'
    try:
        print '[+] Getting sitekey from test page...'
        resp = req.get(TEST_PAGE_INVISIBLE)      # make request and get response
        tree = html.fromstring(resp.text)                               # init tree for parsing
        site_key = tree.xpath('//button')[0].attrib['data-sitekey']  # get sitekey
        submission_endpoint = '{}/{}'.format('/'.join(TEST_PAGE_INVISIBLE.split('/')[:-1]),
                                             tree.xpath('//form')[0].attrib['action'])
        print '[+] Site key: {}'.format(site_key)
        print '[+] Submission endpoint: {}'.format(submission_endpoint)

        # complete captcha
        print '[+] Waiting for recaptcha to be solved ...'
        i = ImageTyperzAPI(IMAGETYPERS_TOKEN)
        recaptcha_params = {
            'page_url': TEST_PAGE_INVISIBLE,
            'sitekey': site_key,
            'type': 2  # normal (v2)
        }
        recaptcha_id = i.submit_recaptcha(recaptcha_params)      # submit recaptcha
        while i.in_progress(recaptcha_id):      # check if still in progress
            sleep(10)       # every 10 seconds
        g_response_code = i.retrieve_recaptcha(recaptcha_id)        # get g-response-code
        
        print '[+] Got g-response-code: {}'.format(g_response_code)  # we got it

        # make request with data
        resp = req.post(submission_endpoint, data={
            'username' : 'get-this-user',
            'password' : 'my-password',
            'g-recaptcha-response' : g_response_code
            }
        )
        print '[+] Form submitted'
        print '[+] Response: {}'.format(resp.text.encode('utf-8'))

    finally:
        print '[=] REQUESTS TEST FINISHED [=]'

def main():
    print '[==] TESTS STARTED [==]'
    print '--------------------------------------------------------------------'
    try:
        browser_test_normal()       # with submit button (old recaptcha)
        print '--------------------------------------------------------------------'
        requests_test_normal()
        print '--------------------------------------------------------------------'
        browser_test_invisible()
        print '--------------------------------------------------------------------'
        requests_test_invisible()
    except Exception, ex:
        print '[!] Error occured: {}'.format(ex)
        print '[==] ERROR [==]'
    finally:
        print '--------------------------------------------------------------------'
        print '[==] TESTS FINISHED [==]'

if __name__ == "__main__":
    main()
