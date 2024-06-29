import requests
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk 
import threading
import time

def get_file(url):
    response = requests.get(url)
    return response.text

def write_file(txt,type,ast):
    fl = open(r'C:\Users\stavr\OneDrive\Desktop'+'\\'+ast+'.'+type,'w')
    fl.write(txt)
    fl.close()

def threader(ast):
    label ["text"]="Fetching files..."
    Enter["state"]="disabled"
    entry.config(state="disabled")
    if len(ast)==3:
        prefix='0'
    else:
        prefix=ast[:-3]
        
    t = threading.Thread(target=downloader(ast,prefix))
    t.start()
    # Start checking periodically if the thread has finished.
    schedule_check(t)
    return

def downloader(ast,prefix):
    i=0
    url1 = ('https://newton.spacedys.com/~astdys2/epoch/numbered/'+prefix+'/'+ast+'.eq0')
    eq0_txt=get_file(url1)
    url2 = ('https://www.minorplanetcenter.net/tmp2/'+ast+'.txt')
    print(url2)
    obs_txt = get_file(url2)
    print(obs_txt[:15])
    global msg
    while obs_txt[:15] == "<!DOCTYPE html>" and i <=5 :
            
            obs_txt=get_file(url2)
            i=i+1
    if obs_txt[:15] == "<!DOCTYPE html>" and i ==6:
         msg='Obs file has not been dowloaded succesfully. :('
    else :
        msg='Files succesfully dowloaded!'
    fl_type1='obs'
    fl_type2='eq0'
    entry.delete(0,'end')
    entry.config(state="normal")
    return write_file(obs_txt,fl_type1,ast),write_file(eq0_txt,fl_type2,ast)


    
def check_if_done(t):
    # If the thread has finished, re-enable the button and show a message.
    if not t.is_alive():
        label["text"] = "Enter asteroid numerical designation:"
        Enter["state"] = "normal"
        entry.delete(0,'end')

    else:
        # Otherwise check again after one second.
        schedule_check(t)

def schedule_check(t):
    """
    Schedule the execution of the `check_if_done()` function after
    one second.
    """
    window.after(1000, check_if_done, t)



def get_input():
    ast=entry.get()
    threader(ast)
    tkinter.messagebox.showinfo("Web Scrap", msg)
    return ast

window = tk.Tk()
window.title('Web Scrap')
label = tk.Label(text="Enter asteroid numerical designation:")
label.pack()
progressbar = ttk.Progressbar()
entry = tk.Entry()
entry.pack()
progressbar.start()

Enter= tk.Button(window,
          text='Enter', command=lambda : get_input(),padx=5,pady=5)
Enter.pack(side = 'left',expand=True)
Quit= tk.Button(window,
          text='Quit', command=window.quit,padx=5,pady=5)
Quit.pack(side = 'right',expand=True)
window.mainloop()