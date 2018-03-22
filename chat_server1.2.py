import socket
import select
import pickle
import os
class ChatServer:
    def __init__( self, port ):
        self.port = port;
        self.srvsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.srvsock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self.srvsock.bind( ("", port) )
        self.srvsock.listen( 5 )
        self.descriptors = [self.srvsock]
        self.directorio=os.getcwd()+os.sep+'users'+os.sep
        print ('Chat server started on port %s\r\n'%port)
        
    def run( self ):
        while 1:
            # Await an event on a readable socket descriptor
            (sread, swrite, sexc) = select.select( self.descriptors, [], [] )
            # Iterate through the socks in descriptors
            for sock in sread:
                # Received a connect to the server (listening) socket
                if sock == self.srvsock:
                    self.accept_new_connection()
                else:
                    # Received something on a client socket
                    host,port = sock.getpeername()
                    try:
                        sms = sock.recv(200).decode()
##                        print(sms)
                        if sms.startswith('User'):
                            archivo=self.save_user(sms,host,sock)
                        elif sms== '':
                            self.exit_cli(host,port,sock)
                        else:
                            host,_=self.load_user(host)   #Cargo el host si esta registrado sino tomo su ip
                            newstr = 'Client [%s] says: %s' % (host, sms.capitalize())
                            self.broadcast_string( newstr, sock )
                    #If can't be decoded, pass          
                    except UnicodeDecodeError:
                        pass
                    #If conection close abruptly, close connection with client
                    except (ConnectionResetError, ConnectionAbortedError) as e:
                        self.exit_cli(host,port,sock)
    def save_user(self,sms,host,sock):
        old_name,existe=self.load_user(host)
        name=str(sms[5:]).strip('\r\n').capitalize()
        archivo=name+'.pickle'
           #Comprobar si el host que se esta intentando registrar existe
        if not existe:
            _,name_existe=self.load_user(name) #Comprobar si el username existe
            if not name_existe:
                user=[name,host]
                 ##Guardar en una lista [name,host]
                file1=open(self.directorio+os.sep+archivo,'wb')
                pickle.dump(user, file1)
                file1.close()
            else:
                sock.send(b'Username error\r\n')
                
                #El username escogido ya está en uso
        else:
            if old_name!=name:
                old_archivo=old_name+'.pickle'
                os.remove(self.directorio+old_archivo)
                self.save_user(sms,host)
        return archivo
    
    def load_user(self,host): #Comprobar si usuario ya se logeó con anterioridad
        existe=False
        for root, dirs, files in os.walk(self.directorio):
            for file in files:
                file2= open(self.directorio+file,'rb')
                user=pickle.load(file2)
                file2.close()
                if user[1]==host:   #Comprobar si el host existe si existe cargar su nombre
                    host=user[0]
                    host_existe=True
                    existe=True
                    break
                elif user[0]==host: #
                    existe=True
                    break         
        return host ,existe       #Regreso host=nombre si esta logeado sino regreso lo mismo que entre
        
    def broadcast_string( self, str, omit_sock ):
        sms=bytes(str,'utf-8')
        for sock in self.descriptors:
            if sock != self.srvsock and sock != omit_sock:
                sock.sendall(sms)
        print (str)
        
    
    def accept_new_connection( self ):
        try:
            newsock, (remhost, remport) = self.srvsock.accept()
            self.descriptors.append( newsock )
            newsock.send(bytes("You're connected to the Python chatserver".center(95,' ')+("\r\n"),'utf-8'))
            newsock.send(bytes('Made by A.M.H'.center(75,'*')+('\r\n'),'utf-8'))
            user,_=self.load_user(remhost)
            active="Client %s active\r\n"%(user)
            str = 'Client joined %s\r\n' % (user)
            for socks in self.descriptors[1:]:
                if socks!=self.srvsock and socks!=newsock:               
                    newsock.send(bytes(active,'utf-8'))
            
            self.broadcast_string( str, newsock )
        except ConnectionAbortedError as a:
            print ('Error aceptando la conexion')
    def exit_cli( self , host , port , sock ):
        user,_=self.load_user(host)
        str = 'Client %s left \r\n' % user
        self.broadcast_string( str, sock )
        sock.close
        self.descriptors.remove(sock)
        
myServer = ChatServer( 2626 )
myServer.run()
