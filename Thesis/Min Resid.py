import os
import fnmatch
from astropy.io import fits
import numpy as np
import shutil

mainpath=r'C:\Users\stavr\OneDrive\Desktop\Physics\Thesis\obs\AUTH_1_MPC_solved'
Paths=[]
Targets=[]
N=[]
resid_list = []
Names=[]
n=0
mins_list=[]
Files=[]
txt='_new'

#Getting path directory and files names for later use.
for path,dirs,files in os.walk(mainpath):
    n=0
    Name_i=[]
    for file in files:
        if fnmatch.fnmatch(file,'*.fits'):
            fullname = os.path.join(path,file)
            n=n+1
            Name_i.append(fullname)
            Files.append(file)
            if "_new" in file:
                target = file[:len(file)-15]
            else:
                target = file[:len(file)-11]
            if path not in Paths:
                Paths.append(path)
    if n!=0:
        N.append(n)
        Names.append(Name_i)
        Targets.append(target)        
           
mins_index=[]
j=-1
All_data='n'
endfix='.fits'

for name in Names: 
    resid_list = []
    for i in range(len(name)):
        k=0
        total_path = name[i]
        with fits.open(total_path, mode='update') as hdul:
            hdr = hdul[0].header
            data = hdul[0].data
            try :
                PS_residual = float(hdr['HISTORY'][3].split()[3])
                resid_list.append(PS_residual)
            except KeyError:
                resid_list.append(100)
                #If data type is not Mono 16 it can not be used by Visual Pin Point.
                if data.dtype == np.uint8:
                    if All_data=='n':
                        ans=input("Data type is MONO 8 do you want to change the data to MONO 16, in order to be accepted by Visual Pin Point? (y/n)\n DISCLAIMER: Data will be forever changed.\n")
                        All_data=input('Apply the option to ALL the data? (y/n)\n')
                        if All_data=='y':
                            All_data==True
                    if ans=='y' or ans=='yes' or All_data==True:
                        # Load the 8-bit FITS image 
                        input_file = total_path
                        hdul = fits.open(total_path)
                        data_8bit = hdul[0].data.astype(np.uint8)  # Assuming the data is in the primary HDU

                        # Convert 8-bit to 16-bit
                        data_16bit = data_8bit.astype(np.uint16)

                        # Update the data in the FITS header
                        hdul[0].data = data_16bit

                        # Save the new 16-bit FITS image
                        new_path=total_path.replace(".fits","_new.fits")
                        hdul.writeto(new_path, overwrite=True)

                        # Close the FITS file
                        hdul.close()
                        print('NOTE:The images need to be solved again.')
                pass
        
        k=resid_list.index(min(resid_list)) #fits name  number
        best_file=name[k]
    best_new_file=best_file[:-15]
    l_bestfile=best_new_file+'.fits'
    new_path_ofbest=r'C:\Users\stavr\OneDrive\Desktop\bestfiles'+'\\'+Targets[j]+'.fits'
    #new_path=best_file.replace(".fits","_new.fits")
    with fits.open(best_file, mode='update') as hdul1:
        hdul1.writeto(new_path_ofbest, overwrite=True)
    j=j+1
    mins_list.append(min(resid_list))
    print(Targets[j],'       Minimum residual: ',min(resid_list),"\t",'Image Colour MONO',hdr['BITPIX'],"\t",
    'Index of best image: ', resid_list.index(min(resid_list)) + 1,"\n"
    ,end = "\r",)
print('\n End of program')