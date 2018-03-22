from tkinter import *
import select, socket,  winsound, os
import tkinter.ttk as ttk
from threading import Thread
'''
__author__ = 'A.M.H.'
__title__= 'PyChaT'
__date__ = '9/03/2018'
__version__ = '1.1'
'''
class ChatClient:
    def __init__(self):
        self.raiz=Tk()
        
    ##Icons
        self.directorio=os.getcwd()+os.sep+'iconos'+os.sep
        self.icono1=PhotoImage(file=self.directorio+"sent.png")
        self.icono2=PhotoImage(file=self.directorio+"logout.png")
        self.icono3=PhotoImage(file=self.directorio+'admin.png')
        self.icono4 = PhotoImage(file=self.directorio+'logout.png')
        self.icono5=PhotoImage(file=self.directorio+'messenger.png')
        self.icono6=PhotoImage(file=self.directorio+'group1.png')
        self.icono7=PhotoImage(file=self.directorio+'speech-bubbles.png')
    ##Tkinter APP 
        self.raiz.title('ChaT')
        self.raiz.attributes('-fullscreen', False)
        self.raiz.minsize(200,200)
        fuente = font.Font(weight='normal')
        self.raiz.configure(bg='light blue')
        titulo = Label(self.raiz,text="PyChaT",fg='black',font=('Broadway',24,),bg='light blue',)
        titulo.pack(side=TOP,pady=10)
        estado = IntVar()
        estado.set(1)
        self.raiz.iconphoto( self.raiz,self.icono5)
        logoimg = PhotoImage(file=self.directorio+os.sep+"esferico.png")
        etiquetalogo = Label(self.raiz,image=logoimg, bg='light blue')
        etiquetalogo.pack(side=TOP,padx=10,pady=10)
        
        
        
        ##Menu and submenus:
        barramenu = Menu(self.raiz)
        self.raiz['menu'] = barramenu
        menu1 = Menu(barramenu)
        barramenu.add_cascade(menu=menu1, label='Opciones')        
        
        menu1.add_command(label='Username', command=self.Login,
                          underline=1,
                          accelerator="Ctrl+a",
                          image=self.icono3,
                          compound=LEFT)
        menu1.add_command(label='Reconnect', command=self.start_connection,
                          underline=1,
                          accelerator="Ctrl+r",
                          image=self.icono7,
                          compound=LEFT)
        menu1.add_command(label='Salir', command=lambda : self.raiz.destroy(), 
                          underline=1, accelerator="Ctrl+q",
                          image=self.icono4,
                          compound=LEFT)
        ##Listbox and Entry objects
        self.lista=Listbox(self.raiz)
        self.lista.pack(side=TOP,padx=10,pady=10,ipadx=140 )

        self.campo= ttk.Entry(self.raiz,textvariable=1)
        self.campo.pack(side=TOP, padx=10, pady=10,ipadx=140)
        self.campo.focus()
        
        ##Buttons
        self.boton1 = ttk.Button(self.raiz,image=self.icono1,command=self.enviar)
        self.boton1.pack(side=LEFT , padx=5, pady=5,fill=BOTH,expand=True)
        self.boton2 = ttk.Button(self.raiz,image=self.icono2,command=lambda:self.salir())
        self.boton2.pack(side= RIGHT ,fill=BOTH,expand=True   , padx=5, pady=5)

        self.raiz.bind("<Key-Insert>", 
                       lambda event: self.enviar())
        self.raiz.bind("<Control-a>", 
                       lambda event: self.Login())
        self.raiz.bind("<Control-q>", 
                        lambda event: self.salir())
        ##Start Connection
        self.running=True
        self.connection=False
        
        self.start_connection()
        self.raiz.mainloop()
        
    def start_connection(self,port=2626,addr='127.0.0.1'):
        try:
            if self.connection==False: ##If there's not connection create the socket connection and start the thread to start reciving
                self.lista.delete(0,END)
                self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((addr,port))
                t=Thread(target=self.recivir,daemon=True)
                t.start()
                self.connection=True
                
        except ConnectionRefusedError:
            self.post("Connection with server can't be stablish".center(68,'*'))
            self.connection=False
            

    def Login(self):
        self.login=Toplevel()
        self.login.configure(bg='light blue')
        self.login.geometry('+'+str(self.raiz.winfo_rootx())+'+'+str(self.raiz.winfo_rooty()))
        self.login.minsize(200,100)
        self.login.title('Username')
        imagen=Label(self.login, image=self.icono6,bg='light blue')
        imagen.pack(side=RIGHT,padx=10,pady=10)
        self.label=Label(self.login, text='Inserte un nombre de usuario',bg='light blue',font='Broadway')
        self.label.pack(padx=10,pady=10)
        self.entry=ttk.Entry(self.login, textvariable='')
        self.entry.pack( padx=10, pady=10)
        self.entry.focus()
        self.boton=Button(self.login, text='Submit',font='Broadway',command=lambda: self.enviar(True))
        self.boton.pack( padx=10, pady=10,expand=True)
        self.login.transient(master=self.raiz)
        self.login.grab_set()
        self.raiz.wait_window(self.login)

    def post(self,text,n=0):
        if n==0:
            self.lista.insert(END,text)
            self.campo.delete(0,END)  
        else:
            for i in text:
                if i=='Username error':
                    messagebox.showerror('Username error', 'The username is already taken')
                elif i=='':pass
                else:self.lista.insert(END,i)
            winsound.Beep(400,150)
        self.lista.see(END)
        self.campo.focus()
        
    def recivir (self):
        try:
            while self.running:
                r,w,e=select.select([self.sock],[],[])
                for sockets in r:
                    text=sockets.recv(1024).decode()
                    text=text.split('\r\n')
                    self.post(text,1)
        except OSError:
            try:
                text='Server connection closed, please try reconnect later...'
                self.post(text)
            except Exception:   ## This exception will raise if the tkinter app was destroyed
                pass
            finally:
                ##Close the socket connection Prepare the app to start over
                self.connection=False
                self.sock.close()
                
                
    def enviar(self,login=False):
        if login and Entry.get(self.entry)== '' :
            messagebox.showerror('Error!!!',"The username can't be empty")
        elif login and not Entry.get(self.entry)== '' :
            self.sock.sendall(bytes('User:'+Entry.get(self.entry).capitalize()+'\r\n','utf-8'))
            self.entry.delete(0,END)
            self.login.destroy()
        else:
            if not Entry.get(self.campo)== '' and self.running:
                self.sock.sendall(bytes(Entry.get(self.campo)+'\r\n','utf-8'))
                self.post('You: ' + Entry.get(self.campo).capitalize())
            elif not self.running:
                self.post('Connection has been closed or reseted, please restart the chat')

    def salir(self):
        salida=messagebox.askyesno('Exit','Are you sure?')
        if salida:
            self.sock.close()
            self.raiz.destroy()         

if __name__=='__main__':       
    ChatClient()
