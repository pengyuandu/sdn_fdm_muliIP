#!/usr/bin/python

"""
This example shows how to create a simulation with two roaming hosts and seven APs
"""
from subprocess import call, check_call, check_output
from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, Host, RemoteController, UserSwitch, Controller
from mininet.link import Link, Intf, TCLink, TCULink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from functools import partial
import sys, time
flush=sys.stdout.flush
import os, string

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def WifiNet(n, m, IP, req, cap, mod,ts):

    """ Uncomment following lines to add controller """
    # info( '*** Adding controller\n' )
    print(IP)
    #link=partial(TCLink,delay='2ms',bw=10)
    #net.addController('c0',controller=Controller,link=link)
    net = Mininet(switch=UserSwitch, link=TCULink)
    #net = Mininet(switch=OVSKernelSwitch)
    net.addController( 'c0', controller=RemoteController, ip=IP, port=6653 )

    """ Initialize WifiSegment
        Reference mininet/ns3.py for more detail of WIFISegment class """

    """ Node names """
    hosts = []
    switches = []
    links = []
    hosts.append('dest')
    sw_name=[]
    for i in range(1,16):
        sw_name.append('0'+hex(i)[-1])
    for i in range(16,60):
        sw_name.append(hex(i)[-2:])
    for i in range(1, n+1):
        hosts.append('ship'+str(i))
    for i in range(1, n+m+2):
        switches.append('s'+str(i))
    #hosts = ['h1', 'h2']
    #switches = ['s1', 's2', 's3', 's4', 's5', 's6', 's7']
    """ Links between APs """
    for i in range(1, n+1):
        for j in range(m):
            links.append([hosts[i], switches[i-1]])
        for j in range(n, n+m):
            links.append([switches[i-1], switches[j]])
        #links.append([switches[i-1],switches[i-1+n]])
    for i in range(n, m+n):
        links.append([switches[-1], switches[i]])
    links.append([hosts[0], switches[-1]])
    print(links)



    nodes = {}

    """ Initialize Ships """
    for host in hosts:
        node = net.addHost(host)
        nodes[host] = node

    """ Initialize SATCOMs """
    for switch in switches:
        node = net.addSwitch(switch)
        nodes[switch] = node

    """ Add links """
    for link in links:
        name1, name2 = link[0], link[1]
        node1, node2 = nodes[name1], nodes[name2]
        print(name1,name2)
        net.addLink(node1, node2)

    """ Create routing config for each host """
    
    #with cd("~/Desktop"):
        #call(["mkdir", "fdm_scripts"])
        
    #with cd("~/Desktop/fdm_scripts"):
    for i in range(1,n+1):
        name=hosts[i]
        file=open(name+".sh","w")
        file.write("#!/bin/bash\n\n")
        for j in range(m):
            intf=name+"-eth"+str(j)
            ipaddr="10.0."+str(i)+"."+str(j)
            file.write("ifconfig "+intf+" "+ipaddr+" netmask 255.255.255.255\n\n")
        for j in range(m):
            ipaddr="10.0."+str(i)+"."+str(j)
            file.write("ip rule add from "+ipaddr+" table "+str(j+1)+"\n\n")
        for j in range(m):
            ipaddr="10.0."+str(i)+"."+str(j)+"/32"
            intf=name+"-eth"+str(j)
            file.write("ip route add "+ipaddr+" dev "+intf+" scope link table "+str(j+1)+"\n\n")
        for j in range(m):
            ipaddr="10.0."+str(i)+"."+str(j)
            intf=name+"-eth"+str(j)
            file.write("ip route add default via "+ipaddr+" dev "+intf+" table "+str(j+1)+"\n\n")
        file.write("ip route add default scope global nexthop via 10.0."+str(i)+".0 dev "+name+"-eth0")
        file.close()
        call(["sudo", "chmod", "777", name+".sh"])
                
    
    
    """ Start the simulation """
    info('*** Starting network\n')
    net.start()
    
    for i in range(1,n+1):
        src=nodes[hosts[i]]
        info("--configing routing table of "+hosts[i])
        src.cmdPrint('./'+hosts[i]+'.sh')
    
    time.sleep(ts)
    '''
    info( 'Testing network connectivity\n' )
    for i in range(1,n+1):
        nodes[hosts[i]].cmdPrint('ping 10.0.0.1 -c 3')
    '''

    ''' Auto GENERATE RUNCONFIG AND DELETE.SH '''
    info('*** generating runconfig')
    #time.sleep(10)
	
    #with cd("~/Desktop/fdm_scripts"):
    file=open('runconfig.sh','w')
    file.write("#!/bin/bash\n")
    for i in range(1,n+1):
        file.write('curl -X POST -d \'{"cmd":"ADD","dst-port":'+\
        '"0","dst-switch":"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-switch":'+\
        '"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-port":"0","requirement":"'+str(req[i-1])+'"}\''+\
        ' http://'+IP+':8080/wm/fdm/config/json\n')

    for i in range(m):
        file.write('curl -X POST -d \'{"cmd":"ADD","dst-port":"'+str(i+1)+'",'+\
        '"dst-switch":"00:00:00:00:00:00:00:'+sw_name[n+m]+'","src-switch":'+\
        '"00:00:00:00:00:00:00:'+sw_name[n+i]+'","src-port":"'+str(n+1)+'","capacity":"'+str(cap[i])+'"}\''+\
        ' http://'+IP+':8080/wm/fdm/config/json\n')
    file.close()
    call(["sudo", "chmod", "777", "runconfig.sh"])
    call("./runconfig.sh")

    file=open('delete.sh','w')
    file.write("#!/bin/bash\n")
    for i in range(1,n+1):
        file.write('curl -X POST -d \'{"cmd":"DELETE","dst-port":'+\
        '"0","dst-switch":"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-switch":'+\
        '"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-port":"0"}\''+\
        ' http://'+IP+':8080/wm/fdm/config/json\n')
    file.close()
    
    call(["sudo", "chmod", "777", "delete.sh"])
    
    file=open('modify1.sh','w')
    file.write("#!/bin/bash\n")
    for i in range(1,n+1):
        file.write('curl -X POST -d \'{"cmd":"MODIFY","dst-port":'+\
        '"0","dst-switch":"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-switch":'+\
        '"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-port":"0","requirement":"'+str(mod[i-1])+'"}\''+\
        ' http://'+IP+':8080/wm/fdm/config/json\n')
    file.close()
    
    call(["sudo", "chmod", "777", "modify1.sh"])
    
    file=open('modify2.sh','w')
    file.write("#!/bin/bash\n")
    for i in range(1,n+1):
        file.write('curl -X POST -d \'{"cmd":"MODIFY","dst-port":'+\
        '"0","dst-switch":"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-switch":'+\
        '"00:00:00:00:00:00:00:'+sw_name[i-1]+'","src-port":"0","requirement":"'+str(req[i-1])+'"}\''+\
        ' http://'+IP+':8080/wm/fdm/config/json\n')
    file.close()
    
    call(["sudo", "chmod", "777", "modify2.sh"])
	
    info('*** run iperf test')

    time.sleep(ts)


    ''' Run Iperf test '''
    
    dst=nodes[hosts[0]]
    dst.cmdPrint('iperf -s -i 2 >testiperf.txt &')
    
    for i in range(1,n+1):
        src=nodes[hosts[i]]
        info("testing",src.name,"<->",dst.name,'\n')
        src.cmdPrint('iperf -c 10.0.0.1 -t 100 -i 2 >src'+str(i)+'.txt &')
        time.sleep(0.2)
    
    time.sleep(20)
    call("./modify1.sh")
    time.sleep(20)
    call("./modify2.sh")
    time.sleep(60)
    '''
    call("./delete.sh")
    time.sleep(10)
    call("./runconfig.sh")
    time.sleep(ts)
    for i in range(1,n+1):
        src=nodes[hosts[i]]
        info("testing",src.name,"<->",dst.name,'\n')
        src.cmdPrint('iperf -c 10.0.0.1 -t 10 -i 2 >src'+str(i)+'.txt &')
        time.sleep(0.2)
    '''
    
    '''
    ports=[]
    for i in range(n):
        ports.append(1010+i)
        dst.cmdPrint('iperf -s -i 2 -p '+str(ports[i])+' -t 100 >testiperf'+str(i)+'.txt &')

    for i in range(1,n+1):
        src, dst=nodes[hosts[i]],nodes[hosts[0]]
        info("testing",src.name,"<->",dst.name,'\n')
        src.cmdPrint('iperf -c 10.0.0.1 -t 10 -i 2 -p '+str(ports[i-1])+' >src'+str(i)+'.txt &')
        #serverbw,_clientbw=net.iperf([src,dst],seconds=10)
        #info(serverbw, '\n')
        #flush()
    '''
    CLI(net)

    net.stop()
    info( '*** net.stop()\n' )

if __name__ == '__main__':
    setLogLevel( 'info' )
    #WifiNet(30,3,"131.179.136.83",[2.0]*30,[15.0,25.0,35.0],90)
    #WifiNet(3,3,"131.179.136.83",[2.0]*3,[5,5,5],30)
    WifiNet(5,3,"131.179.210.194",[2.0]*5,[5.0,7.0,6.0], [1.0]*5,30)
    #WifiNet(30,3,"127.0.0.1",[2.0]*30,[30,20,30],120)
