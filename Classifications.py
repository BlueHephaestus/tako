from base import *
from config import NPY_CLASSIFICATION_DIR
import numpy as np
from tqdm import tqdm

class Classifications():
    """
    Since this class references hard disk files at directories set
        in the class initialization, reading and writing to any instance
        of this class will read and write the exact same classifications
        as other instances.

    Each image's classifications are like this:
        (X,Y,I)
        Such that for a window shape wh, ww and with n samples selected, these are formatted as follows:
            X: (n, wh, ww) - List of window inputs
            Y: (n,) - List of the classifications of those inputs
            I: (n, 2) - List of (i, j) indicating the row and column index 
                relative to wh and ww.

        Since .npy files don't work that way, they don't have tuples,
            We need three files like index_X.npy, index_Y.npy, index_I.npy
            For each image.

        We wrap it as if it's stored in one file in that format, but we are actually 
            referencing 3 for reads and writes.
    """

    def __init__(self, imgs, output_fname, reset):
        self.output_fname = output_fname.replace(".npy","")

        if reset:
            #Delete all old files in the classification directory
            clear_dir(NPY_CLASSIFICATION_DIR)

            #Create empty classification files for every image
            for i in range(len(imgs)):
                fpath = "{:04d}".format(os.path.join(NPY_CLASSIFICATION_DIR,i))
                np.save("{}_X.npy".format(fpath), np.array([]))
                np.save("{}_Y.npy".format(fpath), np.array([]))
                np.save("{}_I.npy".format(fpath), np.array([]))


        #Our list of classification files we provide an interface for with this class
        self.classifications = fpaths(NPY_CLASSIFICATION_DIR)

        """
        This list needs to only have the prefixes for each file, i.e. 
           none of the _X, _Y, _I, to make it easier for our wrapper to operate.
        
        Since fpaths returns a sorted list, we take advantage of this
           to get every third filename and then remove the _X.npy from it.
        
        This assumes there are no other files in this directory, just like the other
           wrappers.
        """
        self.classifications = list(map(lambda f: f.replace("_X.npy",""), self.classifications[::3]))

    def __del__(self):
        """
        Combine all our classifications into three files and save it to output_fname
           This means all _X files are combined into output_fname_X.npy,
           and same for _Y and _I files.

        We make use of our __iter__ method to ease this process.

        I did some theoretical calculations. 
            For windows of size 300x300, we'd need 100,000 classifications to get up to 9GB
            For windows of size 500x500, we'd need 10,000 classifications to get up to 2.5GB

        Since we're using uint8 for our image data / for each pixel, this means 1 byte per pixel,
            which is how I got the above numbers.

        Considering the very large amount of classifications necessary to get the memory required
            up to an amount where holding it in RAM wouldn't be possible, i'm electing
            to not yet use memmaps here and just vstack each array to one global array as we load it in
            in our loop.

        This may change in the future if it presents a problem.
        """
        X = self.__getitem__(0)
        Y = self.__getitem__(0)
        I = self.__getitem__(0)
        for (x,y,i) in tqdm(self.__iter__()[1:]):
            X = np.vstack((X,x))
            Y = np.vstack((Y,y))
            I = np.vstack((I,i))

        np.save(self.output_fname + "_X.npy", X)
        np.save(self.output_fname + "_Y.npy", Y)
        np.save(self.output_fname + "_I.npy", I)

    def __iter__(self):
        #Return (X,Y,I) for each index via calling __getitem__ on each index.
        for i in range(len(self.classifications)):
            yield self.__getitem__(i)

    def __getitem__(self, i):
        #Return (X,Y,I) for this index via loading all 3 files and putting them in a tuple.
        fpath = self.classifications[i]
        data = (np.load(fpath + "_X.npy"), np.load(fpath + "_Y.npy"), np.load(fpath + "_I.npy"))
        return data 

    def __setitem__(self, i, classification):
        fpath = self.classifications[i]
        np.save(fpath + "_X.npy", X)
        np.save(fpath + "_Y.npy", Y)
        np.save(fpath + "_I.npy", I)

    def __len__(self):
        return len(self.classifications)

