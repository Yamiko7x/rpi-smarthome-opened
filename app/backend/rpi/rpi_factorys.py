from gpiozero.pins.pigpio import PiGPIOFactory
import extensions.globals as g
import extensions.logger as log
from rpi.actions_system import reload_actions
import datetime
#________________________________________________________________________
#
# STARTER VARS
#

host_ip_list = {} # {local : {ip: 192.168.1.1, work: False, enable: 1}, ...}
factory_dict = {} # {local : {ip: 192.168.1.1, factory: factory, pin_state: pin_dict, gpio_link: gpio_link}, ...}
warnings = {} # {local : ['new_factory_faild']}

# pin_table {..., 3   :   { pin: 3,  type: "pin", modes: ["GPIO", "I2C SDA"], gpio: 2, mode: "GPIO", gpio_obj:None, binded_actions: []}, ...}
# gpio_link { 3: link_to_pin_in_pin_dict, 5: link_to_pin_in_pin_dict, ...}

#________________________________________________________________________
#
# GPIO DATAS
#

def log_warning(factory_alias, warning):
    if factory_alias in warnings:
        if warning in warnings[factory_alias]:
            return False
        else:
            warnings[factory_alias].append(warning)
            return True
    else:
        warnings[factory_alias] = [warning]        
        return True


def create_pin_dict():
    return {
    1   :   {"pin":1,  "type":"power", "modes":["power"], "power":"3.3V"},
    2   :   {"pin":2,  "type":"power", "modes":["power"], "power":"5V"},
    3   :   {"pin":3,  "type":"pin", "modes":["GPIO", "I2C SDA"], "gpio":2, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    4   :   {"pin":4,  "type":"power", "modes":["power"], "power":"5V"},
    5   :   {"pin":5,  "type":"pin", "modes":["GPIO", "I2C SDA"], "gpio":3, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    6   :   {"pin":6,  "type":"power", "modes":["power"], "power":"GND"},
    7   :   {"pin":7,  "type":"pin", "modes":["GPIO"], "gpio":4, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    8   :   {"pin":8,  "type":"pin", "modes":["GPIO", "TXD0"], "gpio":14, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    9   :   {"pin":9,  "type":"power", "modes":["power"], "power":"GND"},
    10  :   {"pin":10, "type":"pin", "modes":["GPIO", "RXD0"], "gpio":15, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    11  :   {"pin":11, "type":"pin", "modes":["GPIO"], "gpio":17, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    12  :   {"pin":12, "type":"pin", "modes":["GPIO"], "gpio":18, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    13  :   {"pin":13, "type":"pin", "modes":["GPIO"], "gpio":27, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    14  :   {"pin":14, "type":"power", "modes":["power"], "power":"GND"},
    15  :   {"pin":15, "type":"pin", "modes":["GPIO"], "gpio":22, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    16  :   {"pin":16, "type":"pin", "modes":["GPIO"], "gpio":23, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    17  :   {"pin":17, "type":"power", "modes":["power"], "power":"3.3V"},
    18  :   {"pin":18, "type":"pin", "modes":["GPIO"], "gpio":24, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    19  :   {"pin":19, "type":"pin", "modes":["GPIO"], "gpio":10, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    20  :   {"pin":20, "type":"power", "modes":["power"], "power":"GND"},
    21  :   {"pin":21, "type":"pin", "modes":["GPIO"], "gpio":9, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    22  :   {"pin":22, "type":"pin", "modes":["GPIO"], "gpio":25, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    23  :   {"pin":23, "type":"pin", "modes":["GPIO"], "gpio":11, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    24  :   {"pin":24, "type":"pin", "modes":["GPIO"], "gpio":8, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    25  :   {"pin":25, "type":"power", "modes":["power"], "power":"GND"},
    26  :   {"pin":26, "type":"pin", "modes":["GPIO"], "gpio":7, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    27  :   {"pin":27, "type":"pin", "modes":["ID_SD"], "mode":"ID_SD"},
    28  :   {"pin":28, "type":"pin", "modes":["ID_SC"], "mode":"ID_SC"},
    29  :   {"pin":29, "type":"pin", "modes":["GPIO"], "gpio":5, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    30  :   {"pin":30, "type":"power", "modes":["power"], "power":"GND"},
    31  :   {"pin":31, "type":"pin", "modes":["GPIO"], "gpio":6, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    32  :   {"pin":32, "type":"pin", "modes":["GPIO"], "gpio":12, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    33  :   {"pin":33, "type":"pin", "modes":["GPIO"], "gpio":13, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    34  :   {"pin":34, "type":"power", "modes":["power"], "power":"GND"},
    35  :   {"pin":35, "type":"pin", "modes":["GPIO"], "gpio":19, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    36  :   {"pin":36, "type":"pin", "modes":["GPIO"], "gpio":16, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    37  :   {"pin":37, "type":"pin", "modes":["GPIO"], "gpio":26, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    38  :   {"pin":38, "type":"pin", "modes":["GPIO"], "gpio":20, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]},
    39  :   {"pin":39, "type":"power", "modes":["power"], "power":"GND"},
    40  :   {"pin":40, "type":"pin", "modes":["GPIO"], "gpio":21, "mode":"GPIO", "gpio_obj":None, "binded_actions":[]}
    }


def create_gpio_link(pin_state):
    gpio_link = {}
    for k, v in pin_state.items():
        if "GPIO" in v["modes"]:
            gpio_link[v["gpio"]] = pin_state[k]
    return gpio_link


def run_factory(factory_alias, silent=False):
        dic = host_ip_list[factory_alias]
        if not factory_alias in factory_dict and dic['enable']:
            if g.tryip(dic["ip"]):
                try:
                    factory = PiGPIOFactory(host=dic["ip"])
                    pin_dict = create_pin_dict()
                    nowtime = datetime.datetime.now()
                    factory_dict[factory_alias] = {"ip":dic["ip"], "factory":factory, "pin_state":pin_dict, "gpio_link":create_gpio_link(pin_dict), 'time': f'{nowtime}'}
                    host_ip_list[factory_alias]['work'] = True
                    log.logger(['terminal', 'log', 'suc'], f'run_factory: Connected to: {factory_alias} - {dic["ip"]} - {nowtime}')
                    if silent: reload_actions()
                    if factory_alias in warnings: warnings.pop(factory_alias)
                    return {'type':'success', 'msg': 'Urządzneie zostało uruchomione.'}
                except:
                    if log_warning(factory_alias, 'new_factory_faild'): log.logger(["terminal", 'log', 'war'], f'run_factory: Nie można utworzyć factory: {dic["ip"]}')
            else:
                if log_warning(factory_alias, 'cannot_ping'): log.logger(['terminal', 'log', 'war'], f'run_factory: Nie można zapingować: {dic["ip"]}')
                return {'type':'faild', 'msg': 'Nie wykryto urządzenia w sieci.'}
        elif factory_alias in factory_dict:
            if dic['enable']:
                if log_warning(factory_alias, 'exist') and not silent: log.logger(['terminal', 'log', 'war'], f'run_factory: Factory {dic["ip"]} już istnieje\n{factory_dict.keys()}')
                return {'type':'info', 'msg': 'Urządzenie już działa.'}
            else:
                if log_warning(factory_alias, 'not_active') and not silent: log.logger(['terminal', 'log', 'war'], f'run_factory: Factory {factory_alias} : {dic["ip"]} widnieje jako nieaktywny (enable: 0)')
                return {'type':'faild', 'msg': f'Factory {factory_alias} : {dic["ip"]} widnieje jako nieaktywny (enable: 0)'}

        return {'type':'faild', 'msg': 'Wystąpił problem przy próbie uruchomienia.'}


def prepare_factorys(silent=False, alias=None):
    global factory_dict
    if alias: return run_factory(alias, silent=silent)
    else:
        for for_alias in host_ip_list:
            run_factory(for_alias, silent=silent)
    return None
