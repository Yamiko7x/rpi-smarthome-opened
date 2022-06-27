import subprocess
import os
import sys
import string
import random


flask_modules = ['flask', \
                 'flask_sqlalchemy', \
                 "gpiozero", \
                 "pigpio", \
                 "pythonping",\
                 "flask-cors",\
                 "hashlib"]


def install_module(module_name):
    """Zainstaluj moduły python potrzebne do uruchomienia aplikacji"""
    try:
        __import__(module_name)
        print(f"   + {module_name}: OK")
    except:
        print(f"   + Brak modułu {module_name}. Rozpoczynam instalację.")
        subprocess.call(['pip3', 'install', module_name])


def secret_key_generator(size=128, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def make_settings(filename, reinstall=False):
    """Stwórz niejawny plik konfiguracji"""
    def newsecretfile():
        print("   + [ ! ] Tworzenie nowego pliku settings.json")
        secret_key = secret_key_generator()
        newjson = "".join(['{', '"secret_key" : "', secret_key, '"}'])
        
        f = open(filename, 'w')
        f.write(newjson)
        f.close()
        if os.path.isfile(filename):
            print("   + Settings file: OK")
        else:
            print("   [ ! ] Nie można stworzyć pliku settings.json")
        
    if reinstall:
        newSecret = input("   > Wygenerować nowy plik konfiguracji? [T/n] ")
        if newSecret in ["T", "t", "Y", "y"]:
            newsecretfile()
            print("   + Settings file: OK")
    else:
        if os.path.isfile(filename):
            print("   + Settings file: OK")
        else:
            newsecretfile()


def install(reinstall=False):
    """Wykonaj instalację"""
    for module in flask_modules: install_module(module)
    make_settings("settings.json", reinstall)
    if reinstall:
        dbpath = "dbcontroller/rpismarthome.db"
        if os.path.isfile(dbpath):
            rm = input("   > Usunąć bazę danych? [T/n] ")
            if rm in ["T", "t", "Y", "y"]:
                os.remove(dbpath)
                print("   + Baza usunięta")


def remove_module(module_name):
    print(f"Removing {module_name}")
    subprocess.call(['pip3', 'uninstall', module_name, '-y'])


def print_help():
    helps = ["Install app:",
             "  sudo python3 install.py",
             "  sudo python3 install.py [option]",
             "Options:",
             "  -i default, install app",
             "  -r reinstall, install missed modules and recreate files",
             "  -u uninstall modules",
             "  -s show modules",
             "  -h help"]
    for h in helps: print(h)


# Run installation
if __name__ == "__main__":
    reinstall = False
    uninstall = False
    show_modules = False
    show_help = False
    arg = "-i"
    
    try:
        arg = sys.argv[1]
        reinstall = True if arg == "-r" else False
        uninstall = True if arg == "-u" else False
        show_modules = True if arg == "-s" else False
        show_help = True if arg == "-h" else False
    except:
        pass

    print(f"Install mode: {arg}")
    if show_help:
        print_help()
    elif show_modules:
        print(" ".join(flask_modules))
    elif uninstall:
        print("Removing modules")
        for module in flask_modules: remove_module(module)
    else:
        install(reinstall=reinstall)
