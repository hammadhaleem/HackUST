import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import wave
import sys
import math
from scipy.fftpack import dct
import itertools
import os

def dynamicTimeWarp(seqA, seqB, d = lambda x,y: math.pow(abs(x-y),2)):
    # create the cost matrix
    numRows, numCols = len(seqA), len(seqB)
    cost = [[0 for _ in range(numCols)] for _ in range(numRows)]
 
    # initialize the first row and column
    cost[0][0] = d(seqA[0], seqB[0])
    for i in xrange(1, numRows):
        cost[i][0] = cost[i-1][0] + d(seqA[i], seqB[0])
 
    for j in xrange(1, numCols):
        cost[0][j] = cost[0][j-1] + d(seqA[0], seqB[j])
 
    # fill in the rest of the matrix
    for i in xrange(1, numRows):
        for j in xrange(1, numCols):
            choices = cost[i-1][j], cost[i][j-1], cost[i-1][j-1]
            cost[i][j] = min(choices) + d(seqA[i], seqB[j])
 

    test_cost = cost[-1][-1]

    return test_cost

#define threshhold and return match results
def match_test(test_cost):
    if test_cost <= 1000:
        return True
    else:
        return False

#read wav file and get data and rate
def read_file(filename):
    raw = wave.open(filename)
    signal = raw.readframes(-1)
    data = np.fromstring(signal, 'Int16')
    if raw.getnchannels() == 2:
        data = data[::2]
    rate = raw.getframerate()
    return rate, data

#normalize data betwen -1 and 1
def normalize(data):
    data_max = max([abs(val) for val in data])
    new_range_val = 1
    data = [float(val)/data_max * new_range_val for val in data]
    return data

#set a threshhold to start analysis
def get_threshhold(data, thresh=.15):
    for i in range(len(data)):
        if data[i] >= thresh:
            return i

#set an end threshhold for analysis
def get_end(data, end_thresh=.1):
    for i in reversed(range(len(data))):
        if data[i] >= end_thresh:
            return i

#create dataset with new threshholds
def new_data_start(data, threshhold, end, min_len=40000):
    data = data[threshhold:end]
    if len(data) >= min_len:
        return data
    else:
        return [0] * len(data)

#split data into consistent, overlapping bins
def split(data, bin_len=400, bin_overlap=160):
    bins = []
    for i in range(0,len(data), bin_len-bin_overlap):
        bins.append(data[i:i+bin_len])
    if len(bins[-1]) != bin_len: # if last bin is short of len
        bins[-1] += [0] * (bin_len - len(bins[-1])) # zero pad it
    if len(bins[-2]) != bin_len: # if last bin is short of len
        bins[-2] += [0] * (bin_len - len(bins[-2]))
    num_of_bins = len(bins)
    return bins

#transform from time spectrum to frequency spectrum
def get_power_spectrum(bins):
    power_spectrum = []
    for bin in bins:
        spectrum = np.fft.rfft(bin)
        magnitude = np.absolute(spectrum)
        power = np.square(magnitude)
        power_spectrum.append(power)
    return power_spectrum

#hertz to mels conversion
def hertz_mels(hertz):
    mels = 2595 * np.log10(1+hertz/700.0)
    return mels

#mels to hertz conversion
def mels_hertz(mels):
    hertz = 700*(10**(mels/2595.0)-1)
    return hertz

#set up filterbank with 13 bands up to 3000hz
def mel_filterbank(power_spectrum):
    block_size = int(len(power_spectrum[0]))
    num_bands = int(13)
    min_hz = 0
    max_hz = 3000
    max_mel = int(hertz_mels(max_hz))
    min_mel = int(mels_hertz(min_hz))

    filter_matrix = np.zeros((num_bands, block_size))

    mel_range = np.array(xrange(num_bands + 2))

    mel_centers = mel_range * (max_mel - min_mel)/(num_bands + 1) + min_mel

    aux = np.log(1 + 1000.0 / 700.0) / 1000.0
    aux = (np.exp(mel_centers * aux) -1) / 22050
    aux = 0.5 + 700 * block_size * aux
    aux = np.floor(aux)
    center_index = np.array(aux, int)


    for i in xrange(num_bands):
        start, center, end = center_index[i:i + 3]
        k1 = np.float32(center - start)
        k2 = np.float32(end - center)
        up = (np.array(xrange(start, center)) - start) / k1
        down = (end - np.array(xrange(center, end))) / k2

        filter_matrix[i][start:center] = up
        filter_matrix[i][center:end] = down

    return filter_matrix.transpose()

#dot product of power spectrum and mel filterbank
def MFCC(power_spectrum, filter_matrix):
    dct_spectrum = []
    for power in power_spectrum:
        filtered_spectrum = np.dot(power, filter_matrix)
        log_spectrum = np.log(filtered_spectrum)
        dct_item= dct(log_spectrum, type=2)
        dct_spectrum.append(dct_item)
    return dct_spectrum

#take average MFCC for each bin
def get_average(dct_spectrum):
    avg_spectrum = []
    for each in dct_spectrum:
        avg = sum(each)/len(each)
        avg_spectrum.append(avg)
    return avg_spectrum

#creates wavform graph (way to test if rate and data look correct)
# def plot_wave(rate, data):
#     Time=np.linspace(0, len(data)/rate, num=len(data))

#     plt.title('Wave')
#     plt.plot(Time,data)
#     return plt.show()


def master(filename):
    rate, data = read_file(filename)
    data = normalize(data)
    threshhold = get_threshhold(data)
    end = get_end(data)
    data = new_data_start(data, threshhold, end)
    bins = split(data)
    power_spectrum = get_power_spectrum(bins)
    filter_matrix = mel_filterbank(power_spectrum)
    dct_spectrum = MFCC(power_spectrum, filter_matrix)
    avg_spectrum = get_average(dct_spectrum)

    # plt.show() = plot_wave(rate, data)

    return avg_spectrum
    




    
















