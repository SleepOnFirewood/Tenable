import os
import requests
import json

#--- NETBOX Query ---#

NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN")
netboxDeviceURL = 'https://netbox.admin.numerator.com/api/dcim/devices/?limit=100'
netboxVMURL = 'https://netbox.admin.numerator.com/api/virtualization/virtual-machines/?limit=100'
headers = {'Authorization': "Token " + NETBOX_TOKEN}
netboxDict = {} 

netboxDeviceRAW = requests.get(netboxDeviceURL, headers=headers)
netboxDeviceResults = netboxDeviceRAW.json()['results']
newResults = True


while(newResults):
    for i in range(len(netboxDeviceResults)):
        netboxAsset = str(netboxDeviceResults[i]['name']).upper()
        netboxIp = (netboxDeviceResults[i]['primary_ip4'])

        if (type(netboxIp) is dict):
            ipAdd = str(netboxIp['address']).split('/', 1)[0]
            if ipAdd not in netboxDict:
                netboxDict[ipAdd] = []
                netboxDict[ipAdd].append(netboxAsset)

        elif netboxAsset not in netboxDict:
            netboxDict[netboxAsset] = 1
        else:
            netboxDict[netboxAsset] +=1
    if(netboxDeviceRAW.json()['next']):
        netboxDeviceRAW = requests.get(netboxDeviceRAW.json()['next'], headers=headers)
        netboxDeviceResults = netboxDeviceRAW.json()['results']
    else:
        newResults=False

netboxVMRAW = requests.get(netboxVMURL, headers=headers)
netboxVMResults = netboxVMRAW.json()['results']
newResults = True

while(newResults):
    for i in range(len(netboxVMResults)):
        netboxVMAsset = str(netboxVMResults[i]['name']).upper()
        netboxIp = (netboxVMResults[i]['primary_ip4'])

        if (type(netboxIp) is dict):
            ipAdd = str(netboxIp['address']).split('/', 1)[0]
            if ipAdd not in netboxDict:
                netboxDict[ipAdd] = []
                netboxDict[ipAdd].append(netboxVMAsset)

        elif netboxVMAsset not in netboxDict:
            netboxDict[netboxVMAsset] = 1
        else:
            netboxDict[netboxVMAsset] +=1
    if(netboxVMRAW.json()['next']):
        netboxVMRAW = requests.get(netboxVMRAW.json()['next'], headers=headers)
        netboxVMResults = netboxVMRAW.json()['results']
    else:
        newResults=False

print(netboxDict)
