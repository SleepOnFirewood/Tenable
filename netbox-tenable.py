import os
import requests
import json
import logging

TENABLE_USERS = "https://cloud.tenable.com/users"
TENABLE_TAG_CATEGORIES = "https://cloud.tenable.com/tags/categories"
TENABLE_TAG_VALUES = "https://cloud.tenable.com/tags/values"
TENABLE_TAG_ASSIGNMENT = "https://cloud.tenable.com/tags/assets/assignments"

logger = logging.getLogger("tenable")
logging.basicConfig(level=logging.INFO)

def cred_check():
    response = requests.request("GET", TENABLE_USERS, headers=tenableHeaders)
    if response.ok:
        logger.info("Tenable credentials ok.")
    else:
        logger.debug("{}".format(response))
        logger.critical("Tenable connection or ceredentials failed.")
        exit(1)
    return response

#--- NETBOX Query ---#

NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN")
netboxDeviceURL = 'https://netbox.admin.numerator.com/api/dcim/devices/?limit=100'
netboxVMURL = 'https://netbox.admin.numerator.com/api/virtualization/virtual-machines/?limit=100'
headers = {'Authorization': "Token " + NETBOX_TOKEN}
netboxDict = {} 


def netbox_getAssets():
    netboxDeviceRAW = requests.get(netboxDeviceURL, headers=headers)
    netboxDeviceResults = netboxDeviceRAW.json()['results']
    newResults = True


    while(newResults):
        for i in range(len(netboxDeviceResults)):
            netboxAsset = str(netboxDeviceResults[i]['name']).upper()
            netboxIp = (netboxDeviceResults[i]['primary_ip4'])
            netboxTenant = (netboxDeviceResults)[i]['tenant']

            if (type(netboxIp) is dict):
                ipAdd = str(netboxIp['address']).split('/', 1)[0]
                if ipAdd not in netboxDict:
                    if(type(netboxTenant) is dict):
                        netboxDict[ipAdd]=netboxTenant['name']
                    else:
                        netboxDict[ipAdd] = 'None'

            if netboxAsset not in netboxDict:
                if(type(netboxTenant) is dict):
                    netboxDict[netboxAsset] = netboxTenant['name']
                else:
                    netboxDict[netboxAsset] = 'None'
        if(netboxDeviceRAW.json()['next']):
            netboxDeviceRAW = requests.get(netboxDeviceRAW.json()['next'], headers=headers)
            netboxDeviceResults = netboxDeviceRAW.json()['results']
        else:
            newResults=False


    #--- Virtual Machine Netbox pull -----
    netboxVMRAW = requests.get(netboxVMURL, headers=headers)
    netboxVMResults = netboxVMRAW.json()['results']
    newResults = True

    while(newResults):
        for i in range(len(netboxVMResults)):
            netboxVMAsset = str(netboxVMResults[i]['name']).upper()
            netboxIp = (netboxVMResults[i]['primary_ip4'])
            netboxTenant = (netboxVMResults)[i]['tenant']

            if (type(netboxIp) is dict):
                ipAdd = str(netboxIp['address']).split('/', 1)[0]
                if ipAdd not in netboxDict:
                    if(type(netboxTenant) is dict):
                        netboxDict[ipAdd] = netboxTenant['name']
                    else:
                        netboxDict[ipAdd]='None'

            if netboxVMAsset not in netboxDict:
                if(type(netboxTenant) is dict):
                    netboxDict[netboxVMAsset] = (netboxTenant['name'])
                else:
                    netboxDict[netboxVMAsset] = 'None'
        if(netboxVMRAW.json()['next']):
            netboxVMRAW = requests.get(netboxVMRAW.json()['next'], headers=headers)
            netboxVMResults = netboxVMRAW.json()['results']
        else:
            newResults=False

#--- Tenable query ---#

matched = {}
unmatched = []
tenableUUIDList = {}
TENABLE_ACCESS_KEY = os.environ.get("TENABLE_ACCESS_KEY")
TENABLE_SECRET_KEY = os.environ.get("TENABLE_SECRET_KEY")
tenableURL = "https://cloud.tenable.com/workbenches/assets"
tenableHeaders = {
    "accept": "application/json",
    "X-ApiKeys": "accessKey={ac}; secretKey={sc}".format(
    ac=TENABLE_ACCESS_KEY,
    sc=TENABLE_SECRET_KEY
    )
}
tenableResponse = requests.get(tenableURL, headers=tenableHeaders)
tenableResponse = tenableResponse.json()

def tenable_getAssets():
    count = 0
    for i in range(len(tenableResponse['assets'])):
        ipAddr = tenableResponse['assets'][i]['ipv4']
        netbios = tenableResponse['assets'][i]['netbios_name']
        host = tenableResponse['assets'][i]['hostname']
        fqdn = tenableResponse['assets'][i]['fqdn']

        if netbios and (netbios[0].upper().split('.')[0] in netboxDict):
            #print(netbios[0].upper().split('.')[0])
            if netboxDict[netbios[0].upper().split('.')[0]] not in matched:
                matched[netboxDict[netbios[0].upper().split('.')[0]]] = []
                matched[netboxDict[netbios[0].upper().split('.')[0]]].append(tenableResponse['assets'][i]['id'])
            else:
                matched[netboxDict[netbios[0].upper().split('.')[0]]].append(tenableResponse['assets'][i]['id'])
            #matched[tenableResponse['assets'][i]['id']] = netboxDict[netbios[0].upper().split('.')[0]]
            count = count+1
        elif host and (host[0].upper().split('.')[0] in netboxDict):
            #print(host[0].upper().split('.')[0])
            if netboxDict[host[0].upper().split('.')[0]] not in matched:
                matched[netboxDict[host[0].upper().split('.')[0]]] = []
                matched[netboxDict[host[0].upper().split('.')[0]]].append(tenableResponse['assets'][i]['id'])
            else:
                matched[netboxDict[host[0].upper().split('.')[0]]].append(tenableResponse['assets'][i]['id'])
            #matched[tenableResponse['assets'][i]['id']] = netboxDict[host[0].upper().split('.')[0]]
            count = count+1
        elif fqdn and (fqdn[0].upper().split('.')[0] in netboxDict):
            #print(fqdn[0].upper().split('.')[0])
            if netboxDict[fqdn[0].upper().split('.')[0]] not in matched:
                matched[netboxDict[fqdn[0].upper().split('.')[0]]] = []
                matched[netboxDict[fqdn[0].upper().split('.')[0]]].append(tenableResponse['assets'][i]['id'])
            else:
                matched[netboxDict[fqdn[0].upper().split('.')[0]]].append(tenableResponse['assets'][i]['id'])
            #matched[tenableResponse['assets'][i]['id']] = netboxDict[fqdn[0].upper().split('.')[0]]
            count = count+1
        else:
            for k in range(len(ipAddr)):
                if ipAddr[k] in netboxDict:
                    if netboxDict[ipAddr[k]] not in matched:
                        matched[netboxDict[ipAddr[k]]] = []
                        matched[netboxDict[ipAddr[k]]].append(tenableResponse['assets'][i]['id'])
                        count = count+1
                    else:
                        matched[netboxDict[ipAddr[k]]].append(tenableResponse['assets'][i]['id'])
                else:
                    unmatched.append(tenableResponse['assets'][i]['ipv4'])

def get_asset_id(matched):
    for i in matched:
        if(matched[i][0] not in tenableUUIDList):
            tenableUUIDList[matched[i][0]]



def get_tag_categories():
    response = requests.request(
        "GET",
        TENABLE_TAG_CATEGORIES,
        headers=tenableHeaders
    )
    print(response.json())

def get_tag_values() -> dict:
    response = requests.request(
        "GET",
        TENABLE_TAG_VALUES,
        headers=tenableHeaders
    )
    values = response.json()["values"]

    # We only care about the value and the UUID
    pairing = {
        value["value"]: value["uuid"]
        for value in values
    }
    return pairing 

def apply_tags():
    tenableTags = get_tag_values()
    for i in matched:
        if i in tenableTags:

            PAYLOAD = {
                "action": "add",
                "assets": matched[i] ,
                "tags": [tenableTags[i]]
            }
            response = requests.post(
                TENABLE_TAG_ASSIGNMENT,
                json= PAYLOAD,
                headers= tenableHeaders
            )
            print(response.text)

def main():
    cred_check()
    netbox_getAssets()
    tenable_getAssets()

    logger.info("Done.")



#main()
#apply_tags()

if __name__ == '__main__':
    main()
