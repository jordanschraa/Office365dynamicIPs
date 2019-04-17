#!/usr/bin/env python
import json
import subprocess
import logging
from datetime import datetime

#only works for ipv4 addresses
#updates the dynamicObject called office365 if the object does not exsist it is created
#two reserved dynamic object names office365, tempobject

def main():
 
    #setup logging
    LOG_FILENAME = 'dynamicObject.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

    currentTime = str(datetime.now())
    logging.info(currentTime)

    dynamicObjects = []
    currentRanges = []
    newRanges = []

    #get all the names of the dynamic objects
    output = runBashCommand("dynamic_objects -l")
    for line in (output.split("\n")):
        line = line.split(":")
        if line[0] == "object name ":
            dynamicObjects.append(line[1])

    #if there is no object called "office365" create it
    if " office365" not in dynamicObjects:
        runBashCommand("dynamic_objects -n office365")
        logging.info("office365 dynamic object created")

    currentRanges = objectRanges("office365")

    # ----- #
    
    #REST call to get office 365 IPs
    output = runBashCommand("curl --silent --show-error https://endpoints.office.com/endpoints/Worldwide?ClientRequestId=b10c5ed1-bad1-445f-b386-b919946339a7 -k")
    response = json.loads(output)

    ipv4 = []
    ipv6 = []

    #parse REST call for ipv4 addresses of office365
    for section in response:
        try:
            for ip in section["ips"]:
                if(int(ip.split("/")[1])) > 33:
                    ipv6.append(ip)
                else:
                    ipv4.append(ip)
        except:
            continue
    
    #create tempobject temporally to add new office 365 ips to
    output = runBashCommand("dynamic_objects -n tempobject")

    for ip in ipv4:
        start, end = cidr_to_range(ip)
        output = runBashCommand("dynamic_objects -o tempobject -r "+start+" "+end+" -a")
    
    # ----- #

    newRanges = objectRanges("tempobject")

    if newRanges == []:
        logging.error("Empty list of ips from mircosoft. exiting...")
        logging.info("  ")
        exit()

    addRanges = []	
    deleteRanges = []

    #compare currentRanges and newRanges
    for item in newRanges:
        if item not in currentRanges:
            addRanges.append(item)

    for item in currentRanges:
        if item not in newRanges:
            deleteRanges.append(item)

    #update office365 object
    for range in addRanges:
        output = runBashCommand("dynamic_objects -o office365 -r "+range[0]+" "+range[1]+" -a")

    for range in deleteRanges:
        output = runBashCommand("dynamic_objects -o office365 -r "+range[0]+" "+range[1]+" -d") 

    output = runBashCommand("dynamic_objects -do tempobject") 

    logging.info("The following ranges were added: "+str(addRanges))
    logging.info("The following ranges were deleted: "+str(deleteRanges))
    logging.info(" ")

#gets current ranges for dynamic object
#returns list of ranges for that object
def objectRanges(oName):

    output = runBashCommand("dynamic_objects -l")
    currentRanges = []
    addRange = False

    for line in (output.split("\n")):
        if addRange == True:
            try:
                startRange = (line.split(":")[1][1:].split(" ")[0])
                endRange = (line.split(":")[1][1:].split(" ")[-1])
                #print(startRange, endRange)
                currentRanges.append([startRange, endRange])
            except:
                addRange = False
        if line == "object name : "+oName:
            addRange = True

    return currentRanges

#runs bash command
#returns the output of the bash command
def runBashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error != None:
	logging.error(command+" command failed. exiting...")
        logging.error(error)
        logging.info(" ")
	exit()

    return output
      
#function to convert a cidr address block to an IP range
#returns two strings, the start IP address and the end IP address
def cidr_to_range(ip_address):
    #function from https://boubakr92.wordpress.com/2012/12/20/convert-cidr-into-ip-range-with-python/
    (addrString, cidrString) = ip_address.split('/')

    # Split address into octets and turn CIDR into int
    addr = addrString.split('.')
    cidr = int(cidrString)
 
    # Initialize the netmask and calculate based on CIDR mask
    mask = [0, 0, 0, 0]
    for i in range(cidr):
        mask[int(i/8)] = mask[int(i/8)] + (1 << (7 - i % 8))

    # Initialize net and binary and netmask with addr to get network
    net = []
    for i in range(4):
        net.append(int(addr[i]) & mask[i])

    # Duplicate net into broad array, gather host bits, and generate broadcast
    broad = list(net)
    brange = 32 - cidr
    for i in range(brange):
        broad[3 - int(i/8)] = broad[3 - int(i/8)] + (1 << (i % 8))

    # Print information, mapping integer lists to strings for easy printing
    return ".".join(map(str, net)), ".".join(map(str, broad))
    
if __name__ == "__main__":
    main()