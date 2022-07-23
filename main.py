
from playwright.sync_api import sync_playwright, Page
import time
import slack

def token():
    from dotenv import load_dotenv
    import os
    env_path=os.path.join("D://Documents//GitHub//automationSlack//secret", '.env')
    load_dotenv(dotenv_path=env_path)
    TOKEN = os.getenv("TOKEN")
    return TOKEN



def get_urls_client_page(client_endpoint: str, pass_page: Page):
    pass_page.goto(client_endpoint)
    rows = pass_page.locator('//h3[contains(text(),"Encentivizer Catalog Widget")]/ancestor::div[1]/p/a')
    count = rows.count()
    dict_page_url = {}
    for i in range(count):
        dict_page_url[rows.nth(i).text_content()] = rows.nth(i).get_attribute('href')

    return dict_page_url , count


def check_widget_in_page(pass_dict_pages: dict, pass_page: Page):
    failed_page_item = {}
    number_of_matched_items_list = []
    number_of_matched_item = 0
    for page_name, page_url in pass_dict_pages.items():
        print(page_name , flush=True)
        print(page_url , flush=True)
        if page_name == "Cooper Lighting":
            
            pass_page.goto(page_url, wait_until="domcontentloaded", timeout=90000)
            time.sleep(5)
            elementHandle = pass_page.wait_for_selector('iframe[title="TrustArc Cookie Consent Manager"]')
            frame = elementHandle.content_frame()
            frame.wait_for_selector('//a[text()[contains(.,"Agree and proceed")]]').click()
            pass_page.wait_for_selector('select[class="ee-widget-form-control"]')
        elif page_name == "Dialight":
            pass_page.goto(page_url, wait_until="networkidle", timeout=90000)
            # page.wait_for_selector('iframe[owner="archetype"]')
            # frame = elementHandle.content_frame()
            pass_page.locator('#onetrust-accept-btn-handler').click()
            pass_page.wait_for_selector('select[class="ee-widget-form-control"]')
        elif page_name == "GE CURRENT, A DAINTREE COMPANY":
            pass
            #pass_page.goto(page_url, wait_until="networkidle", timeout=90000)
            #try:pass_page.wait_for_selector("#_evidon-decline-button").click()
            #except :pass
            #number_of_matched_item = pass_page.wait_for_selector('select[class="ee-widget-form-control"]').count()
        elif page_name == "FSC Lighting":
            pass_page.goto(page_url, wait_until="networkidle", timeout=100000)
            time.sleep(5)
            number_of_matched_item = pass_page.locator('select[class="ee-widget-form-control"]').count()
        elif page_name == "Universal Lighting Technologies":
            pass_page.goto(page_url, wait_until="networkidle", timeout=100000)
            time.sleep(10)
            number_of_matched_item = pass_page.locator('select[class="ee-widget-form-control"]').count()
        elif page_name == "LED Stick":
            page_url = page_url.replace("/widgets", "/rebateguide")
            pass_page.goto(page_url, wait_until="networkidle", timeout=100000)
            
            number_of_matched_item = pass_page.locator('select[class="ee-widget-form-control"]').count()
        elif page_name == "Visionaire Lighting":
            pass

        else:
            try:
                pass_page.goto(page_url, wait_until="networkidle", timeout=90000)
            except:
                pass
        if page_name == "Topaz Lighting Corp.":
            elementHandle = pass_page.wait_for_selector('iframe[src]')
            frame = elementHandle.content_frame()
            frame.wait_for_selector('select[class="ee-widget-form-control"]')
            number_of_matched_item=frame.locator('select[class="ee-widget-form-control"]').count()
        else:
                
                number_of_matched_item = pass_page.locator('select[class= "ee-widget-form-control"]').count()
            
        if number_of_matched_item == 0:
            failed_page_item[page_name] = page_url
            number_of_matched_items_list.append(page_name)
    return failed_page_item, number_of_matched_items_list


def get_result_to_send(failed_page_item:dict, number_items_detail:list , total_pages:int):
    result = ""
    number = len(number_items_detail)
    total_pgs = total_pages
    if len(failed_page_item) == 0:
        result = f"The test for checking widgets is : SUCCESSFUL \n{total_pgs} pages were tested \n{total_pgs} pages were passed"
    else:
        result = f"The test for checking widgets is : UNSUCCESSFUL \n{total_pgs} pages were tested \n{number} pages were failed which are {number_items_detail}"
    return result


def send_result_to_Slack(channel:str, token:str, result:str):
    client = slack.WebClient(token=token)
    client.chat_postMessage(channel=channel, text = result)

    
    

if __name__ == '__main__':
    CLIENT_URL = "https://www.encentivenergy.com/livewidgets"
    try:
        with sync_playwright() as p:

                print("Starting............")
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                dictionary_pages , count = get_urls_client_page(CLIENT_URL, pass_page=page)
                #dictionary_pages = {"Acuity Brands":"http://www.acuitybrands.com/solutions/renovation/energy-efficient-products"}
                dict_failed_pages, list_page_name = check_widget_in_page(pass_dict_pages=dictionary_pages, pass_page=page)
                result_to_send= get_result_to_send(dict_failed_pages,list_page_name , count)
                send_result_to_Slack("#encentivizerbots",token(),result_to_send)
                print(dict_failed_pages)
                print("Result sent to Slack")
                print("Closing app.....")
                time.sleep(5)

                browser.close()
    except Exception as e:
            print("Task aborted due to some error !" ,e)
            print("Please Try again")
            