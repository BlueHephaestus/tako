import os
from config import IMAGE_MAX_GB

def fpaths(directory):
    """
    Arguments:
        dir: directory to recursively traverse. Should be a string.

    Returns:
        List of filepaths in that directory, sorted by filepath.
    """
    return sorted([os.path.join(path,fname) for (path, dirs, fnames) in os.walk(directory) for fname in fnames])

def clear_dir(directory):
    #Removes all files and subdirectories from directory 
    for fname in os.listdir(d):
        fpath = os.path.join(d, fname)
        try: 
            if os.path.isfile(fpath):
                os.unlink(fpath)
            elif os.path.isdir(fpath): 
                shutil.rmtree(fpath)
        except:
            pass

def has_duplicates(l):
    return len(l) != len(set(l))

def image_subsections(img):
    """
    Dynamically divide the image
        into smaller equally-sized parts if the image
        is too big for us to efficiently manipulate it in memory
        by itself. 
        
    We determine this size via a constant maximum allowed memory size
        for our image subsection(s), defined in the config file under
        IMAGE_MAX_GB. 

    We additionally forcibly convert the given image into the
        np.uint8 datatype, as otherwise we're wasting space to store
        the pixels of the image, and this additionally allows
        us to accurately compute the memory take up by
        each of our image subsections.

    Yields each subsection in the image, and may just yield
        the original image if it is smaller than IMAGE_MAX_GB
    """
    
    """
    Amount we divide each dimension of our image by to get subsections
        division_factor = 1 means the original image,
        division_factor = 2 means we divide both height and width
            by 2, resulting in 2**2 = 4 subsections, or quarters,
            of the image.
        division_factor = 3 repeats this, resulting in 9 subsections,

        And so on.

    We increase this until each subsection is less than our maximum
        allowed memory size.
    """

    division_factor = 1

    #While each subsection's memory size is larger than our allowed size
    while img.size//(division_factor**2) > IMAGE_MAX_GB:

        #Increase the amount of divisions
        division_factor += 1

    #We now know how many divisions are necessary / what division_factor
    #   needs to be, so we iterate through our subsections
    step = img.size//division_factor
    for si in range(0, img.size-step, step)
        for sj in range(0, img.size-step, step)
            yield img[si:si+step, sj:sj+step]








    

