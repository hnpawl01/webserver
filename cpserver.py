#!/usr/bin/python3

import sys
from socket import  *
import os.path
import time 
import multiprocessing
import re
import select 

class buffer():

    def __init__(self):
        self.buf = ''

class clientHandler():

    def __init__(self, cliSock , theServer):
        self.cliSock = cliSock
        self.server = theServer
        self.buffer = buffer()

        self.conn = ''
        self.content_len = 0
        self.msgtype = ''
        self.file = ''
        self.file_path = ''
        
        self.interpMsg()
 
    def dorequest(self):
    
        if(self.msgtype == 'GET'):
            f = open(self.file_path, 'r')
            self.file = f.read()
            f.close()
        self.content_len = len(self.file)
        respmsg = f'HTTP/1.1 200 OK\r\nConnection: {self.conn}\r\nContent-Length: {self.content_len}\r\n\r\n'
        respmsg += self.file        
        
        self.cliSock.send(respmsg.encode())
        return 

    def interpMsg(self):         
         
        while(True):
            while(True):
                msg = self.cliSock.recv(1024).decode()
                self.buffer.buf = self.buffer.buf + msg
                
                if(msg == ''):
                    return
                if(msg == '\r\n'):         
                    break
    
            if (self.buffer.buf.__contains__('GET')):
            
                self.msgtype = 'GET'

            elif (self.buffer.buf.__contains__('HEAD')):

                self.msgtype = 'HEAD'
        
            else:#400 Bad Request error 
                respmsg = f'HTTP/1.1 400 Bad Request\r\nConnection: {self.conn}\r\nContent-Length: {self.content_len}\r\n\r\n'
                self.cliSock.send(respmsg.encode())
                self.cliSock.close()
                return

            finder = self.buffer.buf.split('Connection:')
            finder = finder[1].split('\r\n')
            self.conn = finder[0].strip() 
            
            self.file_path = os.getcwd()
            finder = self.buffer.buf.split(' ')
            self.file_path += finder[1]
        

            file_exist =  os.path.exists(self.file_path)

        
            if (file_exist):
            
                self.dorequest()

                if(self.conn.lower() == 'close'):
                    self.cliSock.close()
                    return
            else:#error 404 Not Found 
                respmsg = f'HTTP/1.1 404 Not Found\r\nConnection: {self.conn}\r\nContent-Length: {self.content_len}\r\n\r\n'
                self.cliSock.send(respmsg.encode()) 
                self.cliSock.close()
                return 

def startClient(clientSocket, serverSocket):
        present_client = clientHandler(clientSocket, serverSocket)

def servers(ports):
    serverSockets = []
    for i in range(len(ports)):    
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', port))
        serverSocket.listen(5)
        serverSockets.append(serverSocket)
    
    while(True):

        readSocks, holder1_emp, holder2_emp = select.select(serverSockets, [], [])
    
        for i in readSocks:
            for j in sys.stdin:
                if 'stop' == line.strip().lower():
                    for sock in serverSockets:
                        serverSockets.close()
                        sys.exit()

                else:        
                    clientSocket, addr = serverSocket.accept()
                    holder = multiprocessing.Process(target = startClient, args = (clientSocket, serverSocket))
                    holder.start()
                    time.sleep(30)

def main():

    args = sys.argv
    for i in range(len(args)):
        ports[i] = args[i+1]
    
    servers(ports)

main()
