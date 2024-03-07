# This script takes in an input brain scan .img file and an input dot .img file with the same dimensions
# It produces a corresponding .img and .hdr file with everything below the dot image zeroed in the brain scan image
# this was designed to remove the neck from the JADNI files, however it can be used to remove anything
# assumes input images are in axial orientation
import nibabel as nib
import argparse
from argparse import RawTextHelpFormatter
import numpy as np
import os

def deneck(head, dotFile, outputFile, fileType):
    # head = args.image1 # this is T1
    # dotFile = args.image2
    # outputFile = args.output

    print(f"Loading {dotFile}...")
    # load dotFile and extract dot
    data = nib.load(dotFile)
    # get image data
    image = data.get_fdata()
    # header data
    hd = data.header


    print(f'Loading {head}...')
    data2 = nib.load(head)
    if fileType == 16:
        bitType = np.int16
    elif fileType == 8:
        bitType = np.int8
    else:
        raise Exception("Error, invalid filetype bit, options are 8 or 16")

    image2 = data2.get_fdata().astype(bitType)
    # if data.shape != data2.shape:
    #     print("Size mismatch, skipping!")
    #     return
    # extract locations where voxel is 1
    dot = np.argwhere(image == 1)

    # dot is an array of all values where voxel is 1, assume they are all clustered together, extract z values, use average
    cutoff = int(np.round(np.mean(dot[:, 2])))
    print(f'cutoff: {cutoff}')
    # image to stamp mask on to


    image2[:, :, :cutoff] = 0
    t1Root = head.split(".", 1) # split only once on the first .
    # hdr = f'{t1Root[0]}.hdr'
    # newT1 = f'{t1Root[0]}_withNeck.{t1Root[1]}'
    newT1 = f'{t1Root[0]}_withoutNeck.{t1Root[1]}' # preserve original ending
    # newT1 = f'{t1Root[0]}_withoutNeck.hdr'
    # print(f"Renaming T1: {head} to {newT1}")
    # os.rename(head, newT1)
    # os.rename(hdr, newT1hdr)

    data2.set_data_dtype(bitType)
    # reorient
    # nib.orientations.apply_orientation(image2, nib.orientations.axcodes2ornt(('R', 'P', 'I')))
    print(f"Saving denecked as {newT1}...")
    final_img = nib.Nifti1Image(image2, data2.affine)
    nib.save(final_img, newT1) # now saving to T1, not output
    print("Done!")


if __name__ == "__main__":
    # help string, printed out when help flag is used
    helpStr = """    This is the dnk (de-neck) script
    Written by Jacqueline Heaton

    Please run with:
    -t Image 1 (the image with the full brain scan),
    -d Image 2 (the image with the singular dot)
    OR
    -f Folder 1 (a folder with subfolders that have a T1 and T1_dnk file)

    Optional flag:
    -b: specify bit (8 or 16), default is 8
    -o: specify output file, default is output.img, if passing folder as input do not give full path of output file

    Example 1:

    python3 dnk.py -t JADNI0013/JADNI0013_01/JADNI0013_01_T1.img -d JADNI0013/JADNI0013_01/JADNI0013_01_T1_dnk.img  -b 16 -o ADNI0013/JADNI0013_01/denecked.img
    
    Example 2:
    
    python3 dnk.py -f JADNI0013 -o denecked.img
    
    Update Jan 5 2024: output has been changed to rename T1 to ...T1_withNeck.img, and for denecked file to be replacement T1. This renders the -o flag obselete

    """

    # parse in arguments
    parser = argparse.ArgumentParser(prog='De-Neck',
                                     description='Zeros all voxels in image1 below the dot provided in image2',
                                     epilog=helpStr, formatter_class=RawTextHelpFormatter)
    # image to extract mask from
    parser.add_argument('-t', '--image1')
    # image to stamp mask onto
    parser.add_argument('-d', '--image2')

    # folder to walk through
    parser.add_argument('-f', '--folder')

    # if they want to change the save file
    parser.add_argument('-o', '--output', default="denecked.img")
    parser.add_argument('-b', '--bit', default=8, choices=[8, 16])

    args = parser.parse_args()

    if args.image1 is not None and args.image2 is not None:
        deneck(args.image1, args.image2, args.output)
    elif args.folder is not None:
        # walk through folders inside args.folder
        subFolders = os.listdir(args.folder)
        for subFolder in subFolders:
            subFolderPath = os.path.join(args.folder, subFolder)
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
                deneck(T1, Dnk, output, args.bit)
            else:
                print(f"Missing files in {subFolderPath}")
        pass
    else:
        print("Input error: missing input given with proper flags. Please give either the T1 (using -t flag) and T1_dnk (using -d flag) or the folder (using -f flag)")




    ##################
    # TO RUN FROM IDE, CHANGE VALUES HERE AND RUN (COMMENT OUT EVERYTHING ABOVE THIS UP UNTIL __main__(self)
    # class Arg():
    #     def __init__(self):
    #         self.image1 = "JADNI0044/JADNI0044_01/JADNI0044_01_T1.img"
    #         self.image2 = "JADNI0044/JADNI0044_01/JADNI0044_01_T1_dnk.img"
    #         self.output = "JADNI0044/JADNI0044_01/denecked.img"
    # args = Arg()
    ##################
