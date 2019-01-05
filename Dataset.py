class Dataset():

    def __init__(self, input_dir, output_fname, label_fname, reset):

        self.images = Images(input_dir, reset)
        self.labels = Labels(label_fname)
        self.classifications = Classifications(self.images, output_fname, reset)

