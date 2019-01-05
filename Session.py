from exceptions import *
import os

class Session():

    def __init__(self, argv):
        #Parse commandline args
        if len(argv) < 6:
            raise InvalidArgumentsException()

        #Assign and Parse each
        self.input_dir = argv[1]
        if not os.path.isdir(self.input_dir):
            raise InvalidArgumentsException()

        self.output_fname = argv[2]
        if ".npy" not in self.output_fname:
            raise InvalidArgumentsException()

        self.label_fname = argv[3]
        if ".txt" not in self.label_fname:
            raise InvalidArgumentsException()

        self.win_h = argv[4]
        self.win_w = argv[5]
        try:
            self.win_h = int(self.win_h)
            self.win_w = int(self.win_w)
        except:
            raise InvalidArgumentsException()

        self.reset = False
        if len(argv) >= 7:
            if argv[6] != "reset":
                raise InvalidArgumentsException()
            else:
                #Check if they're sure
                while True:
                    self.reset_confirm = input("Are you sure you'd like to reset? You will lose all unsaved progress. [Y/N]").upper() 
                    if self.reset_confirm == "Y":
                        self.reset = True
                        break

                    elif self.reset_confirm == "N":
                        break

        self.dataset = Dataset(self.input_dir, self.output_fname, self.label_fname, self.reset)
        self.gui = GUI(self.dataset, self.win_h, self.win_w)

    def start(self):
        pass




    

