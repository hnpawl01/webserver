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

#helper fxn to create the client handler, threads can wait 
    def dorequest(self):
    
        if(self.msgtype == 'GET'):
            f = open(self.file_path, 'r')
            self.file = f.read()
            f.close()
        self.content_len = len(self.file)
        respmsg = f'HTTP/1.1 200 OK\r\nConnection: {self.conn}\r\nContent-Length: {self.content_len}\r\n\r\n'
        respmsg += self.file        
        
        print(respmsg)
        self.cliSock.send(respmsg.encode())
        return 

    def interpMsg(self): 
        print("hey")
        
        print(self.buffer.buf) 
        while(True):
            print('in first')
            #msg = self.cliSock.recv(1024).decode()
            #print(msg)

            while(True):
                print('self.buffer.buf inside while', self.buffer.buf)
                print('in second')
                msg = self.cliSock.recv(1024).decode()
                print(msg) 
                self.buffer.buf = self.buffer.buf + msg
                
                if(msg == ''):
                    print("empty")
                    return
                if(msg == '\r\n'):
                    print("in hereeeeee")            
                    break
            print('self.buffer.buf', self.buffer.buf) 
            if (self.buffer.buf.__contains__('GET')):
            
                self.msgtype = 'GET'

            elif (self.buffer.buf.__contains__('HEAD')):

                self.msgtype = 'HEAD'
        
            else:#400 Bad Request error 
                print("bad request")
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
            print(self.file_path) 

            file_exist =  os.path.exists(self.file_path)

            print(file_exist) 
            if (file_exist):
            
                self.dorequest()

                if(self.conn.lower() == 'close'):
                    self.cliSock.close()
                    return
            else:#error 404 Not Found 
                print("404")
                respmsg = f'HTTP/1.1 404 Not Found\r\nConnection: {self.conn}\r\nContent-Length: {self.content_len}\r\n\r\n'
                self.cliSock.send(respmsg.encode()) 
                self.cliSock.close()
                return 
 
class theServer():
    def __init__(self, sock, port):
        self.sock = sock
        self.port = port 

def startClient(clientSocket, serverSocket):
        present_client = clientHandler(clientSocket, serverSocket)

def main():

    port =int(sys.argv[1])
    
    serverSocket = socket(AF_INET, SOCK_STREAM)

    server = theServer(serverSocket, port)
    serverSocket.bind(('', port))
    serverSocket.listen(5)
    
    while(True):
        print("came back")   
        clientSocket, addr = serverSocket.accept()
        holder = multiprocessing.Process(target = startClient, args = (clientSocket, serverSocket))
        holder.start()
        time.sleep(30)
         

main()
