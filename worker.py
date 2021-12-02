from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import requests, time, os, random
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from PIL import Image
import config


final_message = """Если не получилось найти похожего на Вас человека, то загрузите фото в другом ракурсе. \\n\\nЕсли Вас заинтересовало фото, то напишите нам и мы вам скажем как с этим человеком связаться\\n\\nУ нас есть еще больше результатов для Вас! Получите их, приобретя полный доступ:\\nСтоимость 50₽ (более 100 фотографий похожих на вас людей со всего мира )"""


def cut_list(list):
    output = []
    last = 6
    i = 1
    while i <= len(list)/last:
        b = list[last*(i-1):last*i]
        output.append(b)
        i +=1
    return output


class Worker:
    def __init__(self, api, uid, photo_url, sex, year=1990, donut=False, momentary=False):
        self.api = api
        self.uid = uid
        self.photo_url = photo_url
        self.year = year
        self.sex = sex
        self.donut = donut
        self.momentary = momentary


    def get_random_string(self): return ''.join([random.choice('qwertyuiopasddfhghkjklzxcbnmQWEERYTIUOASFSDHGFKJLZXCVXCNBM') for i in range(12)])

    def cut_photo(self, path):
        img = Image.open(path)
        width, height = img.size  # Get dimensions
        cropped_example = img.crop((0, 0, width, height-60))
        cropped_example.save(path)

    def send_results(self, results):
        upload = VkUpload(self.api)
        photos = []
        for result in results:
            c = requests.get(result['photo']).content
            path = 'bin/%s' % result['photo'].split('/')[-1]
            with open(path, 'wb') as f: f.write(c)
            self.cut_photo(path)
            photos.append(path)
        print(2, photos)
        photo_list = []
        for i in cut_list(photos):
            a = upload.photo_messages(i, self.uid)
            for i in a:
                photo_list.append(i)
        print(1, photo_list)
        code = ''
        ind = 0
        for j, result in enumerate(results[:len(photo_list)]):
            code += 'API.messages.send({"user_id": %s, "message": "%s", "random_id": %s, "attachment": "%s"});\n' % (
                self.uid, "%s\\n%s" % (result['country'], result['score']), random.randint(1, 10000000000000000),
                'photo%s_%s' % (photo_list[j]['owner_id'], photo_list[j]['id'])
            )
            ind += 1
            if ind > 15:
                ind = 0
                for i in photos:
                    try:
                        os.remove(i)
                    except Exception:
                        pass
                self.api.execute(code=code)
                code = ''
        code = 'API.messages.send({"user_id": %s, "message": "%s", "random_id": %s});\n' % (
        self.uid, final_message, random.randint(1, 10000000000000000))
        self.api.execute(code=code)
        if self.donut and not momentary:
            self.api.messages.send(user_id=self.uid, message="Выберите действие.", random_id=random.randint(1, 10000000000000000), keyboard=config.get_keyboard_contact().get_keyboard())
        else:
            self.api.messages.send(user_id=self.uid, message="Выберите действие.", random_id=random.randint(1, 10000000000000000), keyboard=config.get_keyboard_contact_and_level().get_keyboard())


    def start(self):
        #try:
            self.run()
        #except Exception as e: print(e)

    def not_found(self):
        self.api.messages.send(user_id=self.uid, message="К сожалению, для человека на этой фотографии не нашлось близнецов.\nВозможно, произошел сбой в программе, попробуйте еще раз.", random_id=random.randint(1, 10000000000000000))
        #self.api.messages.send(user_id=self.uid, message="Выберите действие.", random_id=random.randint(1, 10000000000000000), keyboard=get_keyboard_choice().get_keyboard())

    def run(self):
        print("Получено задание от %s, фото:\n%s" % (self.uid, self.photo_url))
        print(self.year, self.sex)
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")  # linux only
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("user-data-dir=SeleniumProfile/")
        driver = Chrome(options=chrome_options, executable_path=config.driver_path)
        print('Переходим на сайт')
        driver.get('https://twinstrangers.net/')
        time.sleep(2)
        try: driver.find_element_by_class_name('closelink').click()
        except: pass
        print('Качаем фото')
        img_bytes = requests.get(self.photo_url).content
        name = self.photo_url.split('/')[-1]
        path = 'bin/%s' % name
        with open(path, 'wb') as f: f.write(img_bytes)
        print('Фото сохранено в %s' % path)
        abspath = os.path.abspath(path)
        driver.find_element_by_xpath("//input[@type='file']").send_keys(abspath)
        driver.find_element_by_xpath("//input[@type='submit' and @value='ACCOUNT SETUP']").click()
        time.sleep(3)
        try:
            driver.find_element_by_xpath("//input[@name='f[username]']").send_keys(self.get_random_string())
        except:
            cnt = 0
            while cnt < 5:
                driver.refresh()
                time.sleep(1)
                try:
                    driver.find_element_by_xpath("//input[@name='f[username]']").send_keys(self.get_random_string())
                    break
                except:
                    cnt += 1
                    continue
            if cnt == 5: return self.not_found()
        p = self.get_random_string()
        driver.find_element_by_xpath("//input[@name='f[password]']").send_keys(p)
        driver.find_element_by_xpath("//input[@name='password2']").send_keys(p)
        driver.find_element_by_xpath("//input[@name='f[first_name]']").send_keys(self.get_random_string())
        driver.find_element_by_xpath("//input[@name='f[surname]']").send_keys(self.get_random_string())
        driver.find_element_by_xpath("//input[@name='f[email]']").send_keys(self.get_random_string() + '@mail.ru')
        driver.execute_script("document.getElementsByClassName('datep date_of_birth hasDatepicker')[0].value='16/06/%s';"
                              "document.getElementsByClassName('country')[0].value='199';" % self.year)
        driver.find_element_by_id({'f': 'ifemale', 'm': 'imale'}[self.sex]).click()
        driver.find_element_by_xpath("//input[@name='terms']").click()
        driver.find_element_by_xpath("//input[@value='CREATE USER']").click()
        time.sleep(2)
        os.remove(path)

        if 'profile/ai_results' not in driver.current_url: return self.not_found()
        driver.save_screenshot('a.png')
        time.sleep(4)
        with open('d.html', 'w', encoding='utf-8') as f: f.write(driver.find_element_by_xpath('//html').get_attribute('innerHTML'))
        try:
            driver.find_element_by_class_name('rsi').click()
        except:
            cnt = 0
            while cnt < 5:
                driver.refresh()
                time.sleep(1)
                try:
                    driver.find_element_by_class_name('rsi').click()
                    break
                except:
                    cnt += 1
                    continue
            if cnt == 5: return self.not_found()
        time.sleep(2)
        driver.save_screenshot('a2.png')
        #time.sleep(400)
        output = []
        page = [1]
        if self.donut == True:
            page = [1, 2, 3, 4, 5]
        for i in page:
            try:
                if i != 1:
                    driver.find_element_by_link_text(str(i)).click()
                    time.sleep(4)
                results = driver.find_elements_by_class_name('rowhld')
                if not results: return self.not_found()
                else:
                    for result in results:
                        country = result.find_element_by_xpath(".//img[@class='country']").get_attribute('title')
                        score = result.find_element_by_xpath(".//h2[contains(text(), 'AI Match Score:')]").text
                        score = score.replace('AI Match Score: ', '')
                        photo = result.find_element_by_xpath(".//img[@class='photo']").get_attribute('src')
                        output.append({'country': country, 'score': score, 'photo': photo})
            except Exception as e:
                print(e)
                break
        self.send_results(output)
        driver.get("https://twinstrangers.net/profile/unsubscribe")
        driver.refresh()
        time.sleep(2)
        driver.quit()