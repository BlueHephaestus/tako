from base import *
from scipy.misc import imread
from config import NPY_IMAGE_DIR
from ImageSubsections import ImageSubsections

import numpy as np

class Images():
    """
    Since this class references hard disk files at directories set
        in the class initialization, reading and writing to any instance
        of this class will read and write the exact same images
        as other instances.
    """

    def __init__(self, input_dir, reset):

        #Only convert if resetting
        if reset:
            #Delete all old files in the image directory
            clear_dir(NPY_IMAGE_DIR)

            #Convert the image files in input_dir to .npy files in an intermediate directory.
            i = 0
            for fpath in tqdm(fpaths(input_dir)):

                #Try to load the image file, if we fail it wasn't an image file so we ignore it
                try:
                    img = imread(fpath)
                    
                    """
                    We then iterate through image subsection(s) on the image,
                        via a method which will dynamically divide the image
                        into smaller equally-sized parts if the image
                        is too big for us to efficiently manipulate it in memory
                        by itself. If the image doesn't need to be divided,
                        then we'll only iterate through this generator once.
                    """
                    for img_sub in image_subsections(img):
                        np.save("{:04d}.npy".format(os.path.join(NPY_IMAGE_DIR,i), img_sub))
                        i+=1

                except: pass


        #Our list of image files we provide an interface for with this class
        self.imgs = fpaths(NPY_IMAGE_DIR)

    def __iter__(self):
        for img in self.imgs:
            yield np.load(img)

    def __getitem__(self, i):
        return np.load(self.imgs[i])

    def __setitem__(self, i, img):
        np.save(self.imgs[i], img)

    def __len__(self):
        return len(self.imgs)

