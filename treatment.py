#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from geopy import distance

class GPSTreatment:

    def __init__(self, log_num, prefix, meters_en):
        self.label = dict(t=0, lat=1, lon=2, alt=3)
        self.n = log_num
        self.meters_en = meters_en
        self.data = self.load_data(self.n, prefix)
        if meters_en == True:
            sigma = 0.0001
            self.origin = [np.nanmin(self.data[0][:, self.label['lat']]) - sigma, np.nanmin(self.data[0][:, self.label['lon']]) - sigma]
            self.angles_to_meters()

    def load_data(self, n, prefix):
        data = list()
        print('Loading files:')
        for i in range(1, n+1):
            file_name = '{0:s}{1}.log'.format(prefix, i)
            print(file_name)
            try:
                f = open(file_name, 'r')
            except Exception as e:
                print(e)
                exit()
            data.append(np.loadtxt(f, skiprows=1))
        return data

    def angles_to_meters(self):
        lat_0 = self.origin[0]
        lon_0 = self.origin[1]
        for i in range(self.n):
            self.data[i][:, self.label['lat']] = [distance.distance((x, lon_0), (lat_0, lon_0)).m for x in self.get_field(i, 'lat')]
            self.data[i][:, self.label['lon']] = [distance.distance((lat_0, x), (lat_0, lon_0)).m for x in self.get_field(i, 'lon')]

    def print_data(self):
        c = 0
        for i in self.data:
            c = c + 1
            print('\nShape of {0}th array: {1}'.format(c, i.shape))
            print(i)

    def get_field(self, log, name):
        return self.data[log][:,self.label[name]]

    def get_coords(self, log):
        return  [self.get_field(log, 'lon'), 
                self.get_field(log, 'lat')]

    def get_coords_alt(self, log):
        return self.get_field(log, 'alt')

    def vec_length(self, vec_1, vec_2):
        min_len = np.nanmin([len(self.data[vec_1]), len(self.data[vec_2])])
        lat_sub = abs(self.data[vec_1][:min_len,self.label['lat']] - self.data[vec_2][:min_len,self.label['lat']])**2
        lon_sub = abs(self.data[vec_1][:min_len,self.label['lon']] - self.data[vec_2][:min_len,self.label['lon']])**2
        return np.sqrt(lon_sub + lat_sub)

    def stddev_abs(self, vec_1, vec_2):
        print('\nStd dev absolute between {0} and {1}:'.format(vec_1, vec_2))
        stddev = np.std(self.vec_length(vec_1, vec_2))
        print(stddev)
        return stddev

class Plotter():

    def __init__(self, gps):
        self.gps = gps

    def _check_args(func):
        def wrapper(self, args):
            if len(args) < 1:
                num = list(range(1, self.gps.n+1))
            else:
                num = args
            func(self, num)
        return wrapper

    def separate_h(self):
        fig, log = plt.subplots(1, self.gps.n)
        fig.suptitle('Separate horizontal measuring, meters - {0}'.format(self.gps.meters_en))
        dict_args = dict(marker='+')
        for i in range(self.gps.n):
            log[i].scatter( self.gps.get_field(i, 'lon'), 
                            self.gps.get_field(i, 'lat'), 
                            **dict_args)
            log[i].set_aspect('equal', 'box')

    @_check_args
    def together_3d(self, num):
        fig, comp = plt.subplots()
        fig.suptitle('All measuring, meters - {0}'.format(self.gps.meters_en))
        comp = fig.gca(projection='3d')
        comp.set_aspect('equal', 'box')
        for i in num:
            comp.plot(  self.gps.get_field(i-1, 'lon'), 
                        self.gps.get_field(i-1, 'lat'),
                        self.gps.get_field(i-1, 'alt'), 
                        label=i)
        plt.legend()

    @_check_args
    def together_h(self, num):
        fig, comp = plt.subplots()
        fig.suptitle('All horizontal measuring, meters - {0}'.format(self.gps.meters_en))
        comp.set_aspect('equal', 'box')
        for i in num:
            comp.plot(  self.gps.get_field(i-1, 'lon'), 
                        self.gps.get_field(i-1, 'lat'),
                        label=i)
        plt.legend()

    @_check_args
    def together_v(self, num):
        fig, comp = plt.subplots()
        fig.suptitle('All altitude measuring')
        for i in num:
            comp.plot(  self.gps.get_field(i-1, 'alt'), 
                        label=i)
        plt.legend()

    def stddev_rel(self):
        print('\nStd dev relative:')
        print(list(self.gps.label.keys())[1:])
        fig, bar = plt.subplots(1, self.gps.n)
        for i in range(self.gps.n):
            print(np.std(self.gps.data[i][:, 1:], 0))
            bar[i].bar(list(self.gps.label.keys())[1:], np.std(self.gps.data[i][:, 1:], 0))

    def stddev_abs(self):
        fig, bar = plt.subplots(1, self.gps.n)
        fig.suptitle('Std dev absolute measuring all-by-one, meters - {0}'.format(self.gps.meters_en))
        for i in range(self.gps.n):
            for m in range(self.gps.n):
                bar[i].bar(m+1, self.gps.stddev_abs(i, m))

    @_check_args
    def length_abs(self, num):
        fig, log = plt.subplots(1, len(num))
        fig.suptitle('Horizontal asolute measuring all-by-one, meters - {0}'.format(self.gps.meters_en))
        log_idx = 0
        for i in num:
            for m in num:
                log[log_idx].plot(  self.gps.vec_length(i-1, m-1),
                                    label=i)
                log_idx = log_idx + 1
            log_idx = 0
        plt.legend()

def treatment(args):
    gps = GPSTreatment(args.files_number, args.prefix, args.meters)
    plotter = Plotter(gps)

    # gps.stddev_abs(0,2)
    # gps.print_data()

    if args.plot_en:
        plots = tuple(args.plot_show)
        plotter.separate_h()
        plotter.together_h(plots)
        plotter.together_3d(plots)
        plotter.together_v(plots)
        plotter.length_abs(plots)
        plotter.stddev_rel()
        plotter.stddev_abs()
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Commad line tool for making plots from GPS logs")
    parser.add_argument("-n", "--files_number", help="Total number of files to treatment", type=int)
    parser.add_argument("-p", "--prefix", help="Filename prefix (incliding folder)", type=str)
    parser.add_argument("-m", "--meters", help="Enable converting to meters", type=bool, default=True)
    parser.add_argument("-pe", "--plot_en", help="Enable plots", type=bool, default=True)
    parser.add_argument("-ps", "--plot_show", help="Which plots to view", type=int, default=(), nargs='+')
    args = parser.parse_args()

    treatment(args)

if __name__ == '__main__':
    main()
