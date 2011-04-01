import _winreg
import datetime
import os
import platform
import re
import socket
import sys

class Rumormonger:
    version = "0.1"
    depversion = "0.1"
    DBG = True
    
    reg_hklm = _winreg.HKEY_LOCAL_MACHINE
    reg_hkcu = _winreg.HKEY_CURRENT_USER
    reg_hkcr = _winreg.HKEY_CLASSES_ROOT
    
    paths = {}
    rumors = {}
    
    def __init__(self):
        self.paths = {
            'profilesdir' : [self.reg_hklm, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList", "ProfilesDirectory"],
            'profilesdefaultdir' : [self.reg_hklm, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList", "Default"],
            'profilespublicdir' : [self.reg_hklm, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList", "Public"],
        }
        self.get_general()
        self.get_folders()
        self.get_network()
        self.get_windows()
        self.get_path()
        self.get_time()
        
        self.show_facts()

    def show_facts(self):
        for k,v in self.rumors.items():
            print "%s => %s" % (k, v)

    def get_general(self, compatibility=True):
        self.rumors['rumormongerversion'] = self.version
        self.rumors['strawmanversion'] = self.depversion
        #pv = sys.version_info
        #pvr = "%s.%s.%s" % (pv.major.__str__(), pv.minor.__str__(), pv.micro.__str__())
        self.rumors['pythonversion'] = platform.python_version()
        if compatibility:
            self.rumors['facterversion'] = self.version
            self.rumors['puppetversion'] = self.depversion
        
        machine = platform.machine()
        if machine == "x86":
            _,_,_,_,_,x = platform.uname()
            if x.startswith('x86 Family 6'):
                machine = 'i686'
        self.rumors['hardwaremodel'] = machine

    def get_time(self):
        x = datetime.datetime.now()
        print self.get_uptime()

    def get_uptime(self):
        cmd = "net statistics server"
        for line in os.popen(cmd):
            if line.strip():
                print line
                #date,time,x = lines
                #print dt

    def get_path(self, native_format=False):
        path = sys.path
        rumor = ';'.join(path)
        
        self.rumors['path'] = rumor

    def get_network(self):
        self.rumors['hostname'] = socket.gethostname()
        self.rumors['ipaddress'] = socket.gethostbyname(self.rumors['hostname'])
        self.rumors['fqdn'] = socket.getfqdn(self.rumors['hostname'])
        
        if self.rumors['fqdn'] != self.rumors['hostname']:
            ln = len(self.rumors['hostname'] + ".")
            self.rumors['domain'] = self.rumors['fqdn'][ln:]
        self.get_macaddress()
        

    def get_macaddress(self):
        if sys.platform == 'win32':
            cmd = "ipconfig /all"
            for line in os.popen(cmd):
                if line.lstrip().startswith('Physical Address'):
                    mac = line.split(':')[1].strip().replace('-',':')
                    self.rumors['macaddress'] = mac
                    break
        else:
            pass

    def get_windows(self):
        if sys.platform == 'win32':
            x = sys.getwindowsversion()
            major = x.major.__str__() + "." + x.minor.__str__()
            release = major + "." + x.build.__str__()
            
            self.rumors['kernelmajversion'] = major
            self.rumors['kernelrelease'] = release
            self.rumors['kernelversion'] = release
            self.rumors['operatingsystemrelease'] = release
            self.rumors['operatingsystem'] = 'windows'
        else:
            pass

    def get_folders(self):
        for rumor,v in self.paths.items():
            val = self.find_value(v[0], v[1], v[2])
            self.rumors[rumor] = val
        
    def reg_open(self, root, path, mode=_winreg.KEY_READ):
        if self.DBG: print "    Opening %s " % (path)
        reg = _winreg.OpenKey(root, path, 0, mode)
        return reg
        
    def find_value(self, root, path, key):
        reg = self.reg_open(root, path)
        try:
            i = 0
            while 1:
                n,v,t = _winreg.EnumValue(reg, i)
                if n == key:
                    if self.DBG: print "    Found '%s': %s" % (n, v)
                    return v
                i += 1
        except WindowsError:
            print


        

r = Rumormonger()