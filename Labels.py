from exceptions import InvalidLabelsException
from base import has_duplicates

class Labels():
    """
    Wraps around all provided labels in the given label_fname,
        after parsing the label_fname file
    """

    def __init__(self, label_fname):
        with open(label_fname, "r") as f:
            self.labels = [line.strip() for line in f]

            #Ensure we have at least one label
            if len(self.labels) < 1:
                raise InvalidLabelsException()

            #Ensure we have no null / empty labels
            if '' in self.labels:
                raise InvalidLabelsException()

            #Ensure we have no duplicate labels
            if has_duplicates(self.labels):
                raise InvalidLabelsException()

    def __iter__(self):
        for label in self.labels:
            yield label

    def __getitem__(self, i):
        return self.labels[i]

    def __setitem__(self, i, label):
        self.labels[i] = label

    def __len__(self):
        return len(self.labels)


   
"""
Must be at least 1 classification here, otherwise we won't be gathering any data.
Display a warning, not an error, if this is not true.
"""
