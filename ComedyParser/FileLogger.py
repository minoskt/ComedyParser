import sys
import datetime


class FileLogger:
    '''A FileLogger Class'''

    def __init__(self, filename):

        # get date
        today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # calculate the real filename
        filename = ("%s_%s.log" % (filename, today))

        # open the filename
        self._file = open(filename, 'w')

    def _write(self, logtext):
        self._file.write(logtext)

    def log(self, logtext):

        today = datetime.datetime.now()

        self._write("%s - %s\n" % (today, logtext))

    def close(self):

        # close the FileLogger
        self._file.close()


''' main '''
if __name__ == '__main__':

    # check if the the filename exists as a parameter
    if (len(sys.argv) < 2):
        sys.exit('Missing filename')

    # read the filename from the 1st argument
    filename = sys.argv[1]

    # create FileLogger object
    logger = FileLogger(filename)

    # write 10 times a test string
    for i in range(1, 11):
        logger.log("Test %d" % (i))

    # close the logger
    logger.close()
