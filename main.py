from tkinter import *
from tkinter import messagebox
from DatabaseConn.main import get_passwords,add,delete,get_id,update
import sys

password=""
counter=3
num=0
id=0
def submit(textBox):
    global counter
    password=textBox.get()
    if password != "password":
        messagebox.showerror("Error","Wrong Password")
        textBox.delete(0,END)
        textBox.insert(0,"")
        counter-=1
        if counter==0:
            messagebox.showwarning("Warning", "Too many attempts!!")
        elif counter==-1:
            sys.exit()
    else:
        clear_frame()
        show_data()

def clear_frame():
    for widgets in root.winfo_children():
        widgets.destroy()

def password_ver():
    myLabel = Label(root, text="Password :")
    textBox = Entry(root, show="*")
    button_1 = Button(root, text="Submit", command=lambda: submit(textBox))

    myLabel.grid(row=0, column=0, padx=5, pady=5)
    textBox.grid(row=0, column=1, padx=10, pady=5)
    button_1.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

def show_data():
    # root.geometry("350x350")
    frame_label=LabelFrame(root,text="Add Password")
    email_label=Label(frame_label,text="Description :")
    input_email_box = Entry(frame_label)
    password_label = Label(frame_label, text="Password :")
    input_pass_box = Entry(frame_label, show="*")
    add_button = Button(frame_label, text="+ ADD",width =20, command=lambda: add_data(input_email_box,input_pass_box,frame_label))
    sr_no=Label(frame_label,text="Sr.No.",borderwidth = 2,width = 40,relief="sunken")
    website=Label(frame_label,text="Website",borderwidth = 2,width = 40,relief="sunken")
    passwrd=Label(frame_label,text="Password",borderwidth = 2,width = 40,relief="sunken")

    frame_label.pack(padx=10,pady=10)
    email_label.grid(row=1,column=0,padx=(0,10),pady=(0,10))
    input_email_box.grid(row=1, column=1,padx=(0,15),pady=(0,10))
    password_label.grid(row=1, column=2,pady=(0,10))
    input_pass_box.grid(row=1, column=3,padx=(15,15),pady=(0,10))
    add_button.grid(row=1,column=4,padx=(0,0),pady=(0,10))
    sr_no.grid(row=2,column=0,columnspan=2,pady=(0,2))
    website.grid(row=2,column=2,columnspan=2,pady=(0,2))
    passwrd.grid(row=2,column=4,columnspan=2,pady=(0,2))
    display_data(frame_label)

def add_data(mail,pswrd,frame):
    global num
    num+=1
    if mail.get()=="" and pswrd.get()=="":
        messagebox.showerror("Error","Please Enter Data")
        return
    no = Label(frame, text=num,borderwidth = 1,width = 41,relief="ridge")
    email=Label(frame, text=mail.get(),borderwidth = 1,width = 41,relief="ridge")
    passwrd=Label(frame, text=pswrd.get(),borderwidth = 1,width = 41,relief="ridge")
    del_button = Button(frame, text="DELETE",width =7,height=1,font=("Arial", 7),command=lambda x=mail.get(),y=pswrd.get(): delete_data(x,y,frame))
    upd_button = Button(frame, text="UPDATE",width =7,height=1,font=("Arial", 7),command=lambda x=mail.get(),y=pswrd.get(): update_data(x,y,frame))
    add(mail.get(),pswrd.get())

    mail.delete(0,END)
    pswrd.delete(0,END)

    no.grid(row=num+3,column=0,columnspan=2,pady=(0,0))
    email.grid(row=num+3,column=2,columnspan=2,pady=(0,0))
    passwrd.grid(row=num+3,column=4,columnspan=2,pady=(0,0))
    del_button.grid(row=num+3,column=6,pady=(0,0))
    upd_button.grid(row=num+3,column=7,pady=(0,0))

def display_data(frame):
    global num
    num=0
    result=get_passwords()
    for i in range(0,len(result)):
        num += 1
        no = Label(frame, text=num, borderwidth=1, width=41, relief="ridge")
        email = Label(frame, text=result[i][1], borderwidth=1, width=41, relief="ridge")
        passwrd = Label(frame, text=result[i][2], borderwidth=1, width=41, relief="ridge")
        del_button = Button(frame, text="DELETE",width =7,height=1,font=("Arial", 7),command=lambda id=result[i][0]: delete_data_with_id(id,frame))
        upd_button = Button(frame, text="UPDATE",width =7,height=1,font=("Arial", 7),command=lambda x=result[i][1],y=result[i][2]: update_data(x,y,frame))

        no.grid(row=num + 3, column=0, columnspan=2, pady=(0, 0))
        email.grid(row=num + 3, column=2, columnspan=2, pady=(0, 0))
        passwrd.grid(row=num + 3, column=4, columnspan=2, pady=(0, 0))
        del_button.grid(row=num+3,column=6,pady=(0,0))
        upd_button.grid(row=num+3,column=7,pady=(0,0))

def delete_data(mail,password,frame):
    delete(get_id(mail,password))
    frame.destroy()
    show_data()

def delete_data_with_id(id,frame):
    delete(id)
    frame.destroy()
    show_data()

def update_values(ori_mail,ori_pass,email,password,frame,upd):
    frame.destroy()
    update(email,password,get_id(ori_mail,ori_pass))
    upd.destroy()
    show_data()

def update_data(ori_mail,ori_pass,frame):
    upd=Tk()
    upd.title("ALLSAFE")
    upd.iconbitmap(r'C:\Users\Aditya\sample\assets\Allsafe.ico')

    frame_label=LabelFrame(upd,text="Update data")
    email_label=Label(frame_label,text="Description :")
    input_email_box = Entry(frame_label)
    input_email_box.insert(0,ori_mail)
    password_label = Label(frame_label, text="Password :")
    input_pass_box = Entry(frame_label)
    input_pass_box.insert(0,ori_pass)
    add_button = Button(frame_label, text="Done",width =20, command=lambda: update_values(ori_mail,ori_pass,input_email_box.get(),input_pass_box.get(),frame,upd))

    frame_label.pack(padx=10,pady=10)
    email_label.grid(row=0,column=0,padx=(0,10),pady=(0,10))
    input_email_box.grid(row=0, column=1,padx=(0,15),pady=(0,10))
    password_label.grid(row=0, column=2,pady=(0,10))
    input_pass_box.grid(row=0, column=3,padx=(15,15),pady=(0,10))
    add_button.grid(row=1,column=1,padx=(0,0),pady=(0,10),columnspan=3)
root=Tk()
root.title("ALLSAFE")
root.iconbitmap(r'C:\Users\Aditya\sample\assets\Allsafe.ico')
# root.geometry("250x100")

password_ver()

root.mainloop()