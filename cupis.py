from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from shutil import copy2
from datetime import datetime
from sys import argv, platform
from app_logger import get_logger

import os, csv, sys
import pandas as pd
import undetected_chromedriver.v2 as uc


class Cupis():
    def __init__(self, proxy) -> None:
        self.logger = get_logger(__name__)
        self.option = uc.ChromeOptions()
        self.option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        self.set_extension(proxy)
        self.option.add_argument('--load-extension={}'.format(os.path.dirname(os.path.abspath(__file__)) + '/proxy/'))
        self.driver = uc.Chrome(options=self.option)

    def set_extension(self, proxy):
        background_text = """function startProxy() {
        var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: 	"%s",		// Proxy IP or URL: type -> string
                port: 	49155		// Proxy port : type -> int
            },
            bypassList: ["localhost"]
            }
        };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        }

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "sergeygavrilof",
                    password: "bK9ZKPX5FP"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        startProxy();
                """ % proxy

        manifest_text = """{
        "name": "Chrome Proxy Extension",
        "version": "1.0",
        "description": "Proxy auto connect for ChromeDriver Option",
        "manifest_version": 2,
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
        }
        """
        with open(os.path.dirname(os.path.abspath(__file__)) + '/proxy/' + 'background.js', 'w') as f:
            f.write(background_text)
        with open(os.path.dirname(os.path.abspath(__file__)) + '/proxy/' + 'manifest.json', 'w') as f:
            f.write(manifest_text)
        

    def csv(self):
        try:
            self.driver.get('hidden website')
            with open(os.path.dirname(os.path.abspath(__file__)) + "/input.txt") as file:
                    lines = file.readlines()
                    lines = [line.rstrip() for line in lines]
                    
            for line in lines:
                try:
                    if os.path.isfile(os.path.expanduser("~")+'/Downloads/1cupis-history.csv'):
                        os.remove(os.path.expanduser("~")+'/Downloads/1cupis-history.csv')
                    creds = line.split(':')    
                    sleep(2)
                    self.driver.find_element(By.ID, "form_login_phone").send_keys(creds[1][2:])
                    self.driver.find_element(By.XPATH, '//*[@id="form_login"]/div[1]/div[2]/input').send_keys(creds[2])
                    self.driver.find_element(By.XPATH, '//*[@id="btn_authorization_enter"]').click()
                    sleep(2)    
                    self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div/h2/a').click()
                    sleep(2)
                    now = datetime.now()
                    final_path = os.path.dirname(os.path.abspath(__file__)) + \
                        "/csv/output/" + now.strftime("%m_%d_%Y_%H-%M") + '_' + creds[0] +'.csv'
                    copy2(os.path.expanduser("~")+'/Downloads/1cupis-history.csv', final_path)
                    df = pd.read_csv(final_path, sep=';', encoding ='cp1251')
                    df.to_csv(final_path, encoding='cp1251', index=False)
                    total = []
                    total_output_all = 0
                    total_input_all = 0
                    for company in list(dict.fromkeys(df['Получатель'])):
                        if not company.replace('+', '').isnumeric():
                            operations_json = df[['Сумма перевода с учетом комиссии', 'Тип операции']].where(df['Получатель'] == company).to_dict()
                            total_input = 0
                            total_output = 0
                            for j in range(0, len(operations_json['Сумма перевода с учетом комиссии'])):
                                amount = float(str(operations_json['Сумма перевода с учетом комиссии'][j]).replace(',' ,''))
                                if operations_json['Тип операции'][j] == 'ВВОД':
                                    total_input += amount
                                    total_input_all += amount
                                elif operations_json['Тип операции'][j] == 'ВЫВОД':
                                    total_output += amount
                                    total_output_all += amount
                            difference = total_output - total_input
                            total.append([company, total_input, total_output, difference])
                    fields = ['Букмекерская контора', 'Ввод', 'Вывод', 'Сальдо']
                    with open(os.path.dirname(os.path.abspath(__file__)) + \
                        '/csv/output_total/' + now.strftime('%m_%d_%Y_%H-%M') + '_' + creds[0] +'_total.csv', 'w', encoding='cp1251') as f:      
                        write = csv.writer(f)
                        write.writerow(fields)
                        write.writerows(total)
                        write.writerow(['ИТОГО', round(total_input_all, 2), round(total_output_all, 2), round(total_output_all - total_input_all, 2)])
                    self.driver.get('hidden website')
                except Exception as ex:
                    self.logger.error(str(ex))
                    self.driver.get('hidden website')
                    sleep(1)
        except Exception as ex:
            self.logger.error(str(ex))

    def total(self):
        try:
            self.driver.get('hidden website')
            with open(os.path.dirname(os.path.abspath(__file__)) + "/input.txt") as file:
                    lines = file.readlines()
                    lines = [line.rstrip() for line in lines]
                    
            for line in lines:
                creds = line.split(':')    
                sleep(2)
                self.driver.find_element(By.ID, "form_login_phone").send_keys(creds[1][2:])
                self.driver.find_element(By.XPATH, '//*[@id="form_login"]/div[1]/div[2]/input').send_keys(creds[2])
                self.driver.find_element(By.XPATH, '//*[@id="btn_authorization_enter"]').click()
                count = 2
                total_json = {}
                total_input = 0
                total_output = 0
                while 1:
                    sleep(1) 
                    operations = self.driver.find_elements(By.CLASS_NAME, 'box-flex.box-crop.flex-middle.cursor-pointer.offset-pv-4.offset-ph-6.offset-pv-2-xs.offset-ph-4-xs.border-reset.divider-bottom.divider-solid.divider-gray-01.js-history-item')
                    home = self.driver.window_handles[0]
                    for operation in operations:
                        try:
                            operation.click()
                            sleep(0.1)
                            try:
                                self.driver.find_element(By.XPATH, f'/html/body/div[1]/div[2]/div[3]/div/div/div[{count}]/div[2]/div[9]/form/button').click()
                                count+=1 
                            except: 
                                self.driver.find_element(By.XPATH, f'/html/body/div[1]/div[2]/div[3]/div/div/div[{count+1}]/div[2]/div[9]/form/button').click()
                                count+=2
                            tab = self.driver.window_handles[1]
                            sleep(1)
                            self.driver.switch_to.window(tab) 
                            type = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]').text 
                            company = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]').text

                            if type == 'Возврат остатка ЭДС (его части)':
                                sum = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[8]/div[2]').text
                                if company not in total_json.keys():
                                    total_json[company] = [0.0, 0.0, 0.0]
                                total_json[company][1] += float(sum[:-2])
                                total_output += float(sum[:-2])
                            else:
                                sum = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[7]/div[2]').text
                                if company not in total_json.keys():
                                    total_json[company] = [0.0, 0.0, 0.0]
                                total_json[company][0] += float(sum[:-2])
                                total_input += float(sum[:-2])
                            self.driver.close()
                            self.driver.switch_to.window(home)
                        except Exception as ex:
                            self.driver.switch_to.window(home)
                            
                    count = 2
                    try:
                        page_button = self.driver.find_element(By.CSS_SELECTOR, '#log_pager > div:nth-child(6) > button')
                    except:
                        break
                    if page_button.is_enabled():
                        page_button.click()
                    else:
                        break
                now = datetime.now()
            
                fields = ['Букмекереская контора', 'Ввод', 'Вывод', 'Сальдо']
                with open(os.path.dirname(os.path.abspath(__file__)) + \
                    '/total/' + now.strftime('%m_%d_%Y_%H-%M') + '_' + creds[0] +'.csv', 'w', encoding='cp1251') as f:      
                    write = csv.writer(f)
                    write.writerow(fields)
                    for i in total_json.keys():
                        write.writerow([i, round(float(total_json[i][0]), 2), round(float(total_json[i][1]), 2), (round(float(total_json[i][1])-float(total_json[i][0]), 2))])
                    write.writerow(['ИТОГО', round(float(total_input), 2), round(float(total_output), 2), round(float(total_output)-float(total_input), 2)])
                self.driver.get('hidden website')
        except Exception as ex:
            self.logger.error(str(ex))

    def operations(self):
        try:
            self.driver.get('hidden website')
            sleep(100)
            self.driver.get('hidden website')
            with open(os.path.dirname(os.path.abspath(__file__)) + "/input.txt") as file:
                    lines = file.readlines()
                    lines = [line.rstrip() for line in lines]
                    
            for line in lines:
                creds = line.split(':')    
                sleep(2)
                self.driver.find_element(By.ID, "form_login_phone").send_keys(creds[1][2:])
                self.driver.find_element(By.XPATH, '//*[@id="form_login"]/div[1]/div[2]/input').send_keys(creds[2])
                self.driver.find_element(By.XPATH, '//*[@id="btn_authorization_enter"]').click()
                count = 2
                total = []
                while 1:
                    sleep(1) 
                    operations = self.driver.find_elements(By.CLASS_NAME, 'box-flex.box-crop.flex-middle.cursor-pointer.offset-pv-4.offset-ph-6.offset-pv-2-xs.offset-ph-4-xs.border-reset.divider-bottom.divider-solid.divider-gray-01.js-history-item')
                    home = self.driver.window_handles[0]
                    for operation in operations:
                        try:
                            operation.click()
                            sleep(0.1)
                            try:
                                self.driver.find_element(By.XPATH, f'/html/body/div[1]/div[2]/div[3]/div/div/div[{count}]/div[2]/div[9]/form/button').click()
                                count+=1 
                            except: 
                                self.driver.find_element(By.XPATH, f'/html/body/div[1]/div[2]/div[3]/div/div/div[{count+1}]/div[2]/div[9]/form/button').click()
                                count+=2
                            tab = self.driver.window_handles[1]
                            sleep(1)
                            self.driver.switch_to.window(tab) 
                            type = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]').text 
                            company = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]').text
        
                            if type == 'Возврат остатка ЭДС (его части)':
                                date = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div[5]/div[2]').text
                                sum = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[8]/div[2]').text
                                #comission = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div[9]/div[2]').text
                            else:
                                date = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div[4]/div[2]').text
                                sum = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[7]/div[2]').text
                                #comission = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div[8]/div[2]').text
                            total.append([type, date, sum, company])

                            self.driver.close()
                            self.driver.switch_to.window(home)
                        except Exception as ex:
                            self.driver.switch_to.window(home)
                            
                    count = 2
                    try:
                        page_button = self.driver.find_element(By.CSS_SELECTOR, '#log_pager > div:nth-child(6) > button')
                    except:
                        break
                    if page_button.is_enabled():
                        page_button.click()
                    else:
                        break
                now = datetime.now()
            
                fields = ['Тип операции', 'Дата', 'Сумма', 'Сайт']
                with open(os.path.dirname(os.path.abspath(__file__)) + \
                    '/operations/' + now.strftime('%m_%d_%Y_%H-%M') + '_' + creds[0] +'.csv', 'w', encoding='utf-16') as f:      
                    write = csv.writer(f)
                    write.writerow(fields)
                    for i in total:
                        write.writerow(i)
                self.driver.get('hidden website')
        except Exception as ex:
            self.logger.error(str(ex))

if __name__ == '__main__':
    print('Нажмите сочетание ctrl+c для остановки')
    try:
        if '-proxy' in sys.argv:    
            cupis = Cupis(sys.argv[sys.argv.index('-proxy')+1])
        if '-csv' in sys.argv:
            cupis.csv()
        if '-total' in sys.argv:
            cupis.total()
        if '-operations' in sys.argv:
            cupis.operations()
        print('Скрипт завершен успешно')
    except Exception as ex:
        print(str(ex))
        print('Скрипт остановлен')
    