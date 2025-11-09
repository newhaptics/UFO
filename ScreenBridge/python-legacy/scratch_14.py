from ufo.automator.app_apis.word import wordclient
app_root_name = "WINWORD.EXE"
clsid = "Word.Application"
process_name = ""


import psutil
import pygetwindow as gw

# Iterate through all running processes
for process in psutil.process_iter(attrs=['pid', 'name']):
    try:
        if "WINWORD.EXE" in process.info['name']:
            print(process.info)
            print(f"Process Name: {process.info['name']}, PID: {process.info['pid']}")
            process_name=process.info['name']
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass


temp = wordclient.WordWinCOMReceiver(app_root_name,process_name,clsid)

temp.get_object_from_process_name()

print(temp)
