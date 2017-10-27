from scipy.signal import butter, lfilter, lfilter_zi
import numpy as np
from collections import deque

class LowPassFilter(object):
    def __init__(self, N, cutoff):
        # Set up Butterworth low pass filter
        self.b, self.a = butter(N, cutoff, btype='low', analog=False)
        self.x = deque(maxlen=len(self.b) - 1)
        self.z = lfilter_zi(self.b, self.a)

    def get(self):
        return self.x[-1]

    def filt(self, val):
        # Store new value in circular buffer
        self.x.append(val)
        # Filter
        y, z = lfilter(self.b, self.a, np.float32(self.x), zi=self.z)
        # Store results
        self.z = z
        self.last_val = y[-1]
        return y[-1]
