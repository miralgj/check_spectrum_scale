#!/usr/bin/python
################################################################################
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
################################################################################

################################################################################
# Name:    Check IBM Spectrum Scale / GPFS
# Author:  Philipp Posovszky, DLR - philipp.posovszky@gmail.com
# Version: 0.0.1
# Date: 30/08/2016
# Dependencies:
#   - IBM Spectrum Scale
################################################################################


# The actual code is managed in the following Git rebository - please use the
# Issue Tracker to ask questions, report problems or request enhancements. The
# repository also contains an extensive README.
#   https://github.com/theGidy/check_spectrum_scale.git


################################################################################
# Disclaimer: This sample is provided 'as is', without any warranty or support.
# It is provided solely for demonstrative purposes - the end user must test and
# modify this sample to suit his or her particular environment. This code is
# provided for your convenience, only - though being tested, there's no
# guarantee that it doesn't seriously break things in your environment! If you
# decide to run it, you do so on your own risk!
################################################################################


################################################################################
# # Imports
################################################################################
import argparse
import sys
import os
import subprocess


################################################################################
# # Variable definition
################################################################################
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3


################################################################################
# # Function definition
################################################################################
def getValueFromList(list, header, row):
    """
    Args:
        list     -     list with first line header and following lines data
        header   -     the header name (col) to search
        row      -     the specific row to return
    Return:
        Value from the given list
    """
    col = list[0].index(header)
    
    return list[row][col]

def executeBashCommand(command):
    """
    Args:
        command    -    command to execute in bash
        
    Return:
        Returned string from command
    """
    
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0]

def checkRequirments():
    """
    Check if following tools are installed on the system:
        -IBM Spectrum Scale
    """

    if not (os.path.isdir("/usr/lpp/mmfs/bin/") or os.path.isfile("/usr/lpp/mmfs/bin/mmgetstate")):
        checkResult = {}
        checkResult["returnCode"] = STATE_CRITICAL
        checkResult["returnMessage"] = "CRITICAL - No IBM Spectrum Scale Installation detected."
        checkResult["performanceData"] = ""
        printMonitoringOutput(checkResult)       
    

def checkStatus(args):
    """
    Check depending on the arguments following settings:
        - gpfs status
        - quorum status
        - how many nodes are online
    """
    checkResult = {}
    output = executeBashCommand("mmgetstate -LY")
    
    lines = output.split("\n")
    list = []
    for line in lines:
        list.append(line.split(":"))     
    
    state = getValueFromList(list, "state", 1)
    quorum = getValueFromList(list, "quorum", 1)
    nodeName = getValueFromList(list, "nodeName", 1)
    nodeNumber = getValueFromList(list, "nodeNumber", 1)
    nodesUp = getValueFromList(list, "nodesUp", 1)
    totalNodes = getValueFromList(list, "totalNodes", 1)
    nodesDown=eval(totalNodes) - eval(nodesUp)
       
    quorumNeeded=((eval(totalNodes) / 2) + 1)
    
    if args.quorum: 
        if quorum < quorumNeeded :   
            checkResult["returnCode"] = STATE_CRITICAL
            checkResult["returnMessage"] = "Critical - GPFS is ReadOnly because not enougth quorum (" + str(quorum) + "/" + str(quorumNeeded) + ") nodes are online!"
       
        else:
            checkResult["returnCode"] = STATE_OK
            checkResult["returnMessage"] = "OK - (" + str(quorum) + "/" + str(quorumNeeded) + ") nodes are online!"
        checkResult["performanceData"] = "quorumUp=" + str(quorum) + ";" + str(quorumNeeded)+ ";" + str(quorumNeeded)+ ";;"
    
    if args.nodes:   
        if args.warning > nodesUp:
            checkResult["returnCode"] = STATE_WARNING
            checkResult["returnMessage"] = "Warning - Less than" + str(nodesUp) + " Nodes are up."
        elif args.critical > nodesUp:
            checkResult["returnCode"] = STATE_CRITICAL
            checkResult["returnMessage"] = "Critical - Less than" + str(nodesUp) + " Nodes are up."
        else:
            checkResult["returnCode"] = STATE_OK
            checkResult["returnMessage"] = "OK - " + str(nodesUp) + " Nodes are up."
        checkResult["performanceData"] = "nodesUp=" + str(nodesUp) + ";" + str(args.warning) + ";" + str(args.critical) + ";; totalNodes=" + str(totalNodes) + " nodesDown=" + str(nodesDown)
                
    if args.status:                
        if not(state == "active"):
            checkResult["returnCode"] = STATE_CRITICAL
            checkResult["returnMessage"] = "Critical - Node" + str(nodeName) + " is in state:" + str(state)
        else:
            checkResult["returnCode"] = STATE_OK
            checkResult["returnMessage"] = "OK - Node " + str(nodeName) + " is in state:" + str(state)
        checkResult["performanceData"] = "nodesUp=" + str(nodesUp) + ";" + str(args.warning) + ";" + str(args.critical) + ";; totalNodes=" + str(totalNodes) + " nodesDown=" + str(nodesDown) + " quorumUp=" + str(quorum) + ";" + str(quorumNeeded)+ ";;;"
        
   
    printMonitoringOutput(checkResult)
        

    
def checkFileSystems(args):
    """
    
    """
    
def checkFileSets(args):
    """
    
    """
    
def checkPools(args):
    """
    
    """
    
def checkQuota(args):
    """
    
    """


def argumentParser():
    """
    Parse the arguments from the command line
    """
    parser = argparse.ArgumentParser(description='Check status of the gpfs filesystem')
    group = parser.add_argument_group();
    group.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')
    
    subParser = parser.add_subparsers()
    
    statusParser = subParser.add_parser('status', help='Check the gpfs status on this node');
    statusParser.set_defaults(func=checkStatus) 
    statusParser.add_argument('-w', '--warning', dest='warning', action='store', help='Warning if online nodes below this value (default=5)', default=5)
    statusParser.add_argument('-c', '--critical', dest='critical', action='store', help='Critical if online nodes below this value (default=3)', default=3)
    statusGroup = statusParser.add_mutually_exclusive_group(required=True)
    # TODO: Disk quorum
    statusGroup.add_argument('-q', '--quorum', dest='quorum', action='store_true', help='Check the quorum status, will critical if it is less than totalNodes/2+1')
    statusGroup.add_argument('-n', '--nodes', dest='nodes', action='store_true', help='Check state of the nodes')
    statusGroup.add_argument('-s', '--status', dest='status', action='store_true', help='Check state of this node')
    
    fileSystemParser = subParser.add_parser('filesystems', help='Check filesystems')
    fileSystemParser.set_defaults(func=checkFileSystems) 
     
    filesetParser = subParser.add_parser('filesets', help='Check the filesets')
    filesetParser.set_defaults(func=checkFileSets) 
     
    poolsParser = subParser.add_parser('pools', help='Check the pools');
    poolsParser.set_defaults(func=checkPools) 
     
    quotaParser = subParser.add_parser('quota', help='Check the quota');
    quotaParser.set_defaults(func=checkQuota)
    quotaParser.add_argument('-w', '--warning', dest='warning', action='store', help='Warning if quota is over this value (default=90%)', default=5)
    quotaParser.add_argument('-c', '--critical', dest='critical', action='store', help='Critical if quota is over this value (default=95)', default=3)
    quotaParser.add_argument('-d', '--device', dest='status', action='store', help='Device to check') 
    quotGroup = statusParser.add_mutually_exclusive_group(required=True)
    # TODO: Disk quorum
    quotGroup.add_argument('-f', '--fileset', dest='fileset', action='store', help='Check quota conditions of a fileset')
    quotGroup.add_argument('-C', '--cluster', dest='cluster', action='store', help='Check quota conditions of a cluster')
    quotGroup.add_argument('-u', '--user', dest='user', action='store', help='Check quota conditions of a cluster')

    return parser

def printMonitoringOutput(checkResult):
    """
    Print the result message with the performanceData for the monitoring tool with the given returnCode state.
    
    Args:
        checkResult: HashArray with returnMessage, perfomranceData and returnCode
    
    Error:
        Prints critical state if the parsed checkResult argument is empty.
    """
    if checkResult != None:
        print(checkResult["returnMessage"] + "|" + checkResult["performanceData"])
        sys.exit(checkResult["returnCode"])
    else:
        print("Critical - Error in Script")
        sys.exit(2)
        
################################################################################
# # Main 
################################################################################
if __name__ == '__main__':
    checkRequirments()
    parser = argumentParser()
    args = parser.parse_args()
    # print parser.parse_args()
    args.func(args)
    
    checkResult = {}
    checkResult["returnCode"] = STATE_UNKNOWN
    checkResult["returnMessage"] = "UNKNOWN - No parameters are passed!"
    checkResult["performanceData"] = ""
    printMonitoringOutput(checkResult)

