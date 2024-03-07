import nibabel as nib

if __name__ == "__main__":
    helpStr = "Just run python nii2img.py filename.nii"
    parser = argparse.ArgumentParser(prog='nii2img',
                                     description='converts nifti file to analyze',
                                     epilog=helpStr, formatter_class=RawTextHelpFormatter)
    # image to extract mask from
    