import os
import numpy as np
import pywhiten



def manual_PyWhitener():
    os.chdir(os.getcwd()+"/Sample_Prewhitening_Directory")
    time, data, err = np.loadtxt("HD47129_thresh9_lc.txt", unpack = True)

    pywhitener = pywhiten.PyWhitener(time=time, data=data, err=err)
    for i in range(10):
        pywhitener.it_pw(peak_selection_method="highest")


    os.chdir("..")

if __name__ == "__main__":
    manual_PyWhitener()
