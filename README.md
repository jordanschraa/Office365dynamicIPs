# office365dynamicIPs

## Script designed to import dynamic office 365 IPs into Check Point object for implementation in a rulebase

As office 365 becomes more prevalent in modern IT, a need arises to allow office 365 traffic in the firewall rules. However since office 365 servers use dynamic IPs it becomes a challenge to incorporate a the constantly changing IPs. In Check Point R80.10 there is a hotfix that addresses this issue, but this script provides another quick method to address the problem. 

This script reaches out to Mircosoft's API to get a list of IP addresses for the servers. These IPs are converted into a Check Point dynamic objects that can be used in both the access policy and HTTPS inspections policy to simplify operations.

The installation guide is attached. Also this script only creates a dynamic object that includes IPv4 addresses.
