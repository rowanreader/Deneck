import dnk
import argparse
from argparse import RawTextHelpFormatter
import os

class Arg():
        def __init__(self, image1, image2, output, bit):
            self.image1 = image1
            self.image2 = image2
            self.output = output
            self.bit = bit

if __name__ == "__main__":
    helpStr = """    This is the dnk (de-neck) script
        Written by Jacqueline Heaton

        Please run with directory path:
        Ex: \home\noriko\JADNI
        This will go through each folder and extract:
        Image 1 (the image with the full brain scan), and ending in _T1.img
        Image 2 (the image with the singular dot), and ending in _T1_dnk.img

        Optional flag:
        -o: specify output file, default is output.img

        Example 1:

        python3 multiDnk.py JADNI -b 16 -o denecked.img

        """

    # parse in arguments
    parser = argparse.ArgumentParser(prog='Multi De-Neck',
                                     description='Zeros all voxels in image1 below the dot provided in image2 for all compatible folders',
                                     epilog=helpStr, formatter_class=RawTextHelpFormatter)
    parser.add_argument("path")
    parser.add_argument('-o', '--output', default="denecked.img")
    parser.add_argument("-b", "--bit", choices=[8,16], default=8)
    args = parser.parse_args()

    dirs = os.listdir(args.path)

    for folder in dirs:
        # check if folder has appropriate files
        folderPath = os.path.join(args.path, folder)
        if os.path.isdir(folderPath):
            subFolders = os.listdir(folderPath)
            for subFolder in subFolders:
                subFolderPath = os.path.join(folderPath, subFolder)
                if os.path.isdir(subFolderPath):
                    files = os.listdir(subFolderPath)
                else:
                    # print(f'Skipped: {subFolderPath}')
                    continue
                hasT1 = False
                hasDnk = False
                for i in files:
                    if i.endswith("_T1.img"):
                        if hasT1 == True:
                            print("Oops, double T1 images - either rename or remove so that only 1 file ends with _T1.img")
                            exit(0)
                        hasT1 = True
                        T1 = os.path.join(subFolderPath, i)
                    elif i.endswith("_T1_dnk.img"):
                        if hasDnk == True:
                            print("Oops, double T1_dnk images - either rename or remove so that only 1 file ends with _T1_dnk.img")
                            exit(0)
                        hasDnk = True
                        Dnk = os.path.join(subFolderPath, i)
                if hasT1 and hasDnk: # okay, both the T1 and the dnk files were found, can send into dnk
                    print(f"Applying to: {subFolderPath}")
                    output = os.path.join(subFolderPath, args.output)
                    # dnkArgs = Arg(T1, Dnk, output)
                    dnk.deneck(T1, Dnk, output, args.bit)
                else:
                    print(f"Missing files in {subFolderPath}")
                # print(files)
