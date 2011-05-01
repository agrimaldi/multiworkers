#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import time
import itertools
import multiprocessing
import Queue
import argparse
import traceback
import numpy


class Worker(multiprocessing.Process):
    def __init__(self, work_queue, result_queue, verbose):
        super(Worker, self).__init__()
        self.__work_queue = work_queue
        self.__result_queue = result_queue
        self.__kill_received = False
        self.__verbose = verbose

    def __print_verbose(self, msg):
        if self.__verbose:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def run(self):
        while not self.__kill_received:
            try:
                job = self.__work_queue.get(True, 0.1)
            except Queue.Empty:
                break
            self.do(job)

    def do(self, job_params):
        self.__result_queue.put(
            job_params
        )


class Controller:
    def __init__(self, input, num_cpu, verbose):
        self.__input = input
        self.__num_cpu = num_cpu
        self.__verbose = verbose
        self.__work_queue = multiprocessing.Queue()
        self.__num_jobs = 0
        for param_set in self.__input:
            param_set['id'] = self.__num_jobs
            self.__work_queue.put(param_set)
            self.__num_jobs += 1
        self.__result_queue = multiprocessing.Queue()
        self.__results = []
        self.__workers = []
        self.__init_workers()

    def __init_workers(self):
        for i in range(self.__num_cpu):
            worker = Worker(
                    self.__work_queue,
                    self.__result_queue,
                    self.__verbose
            )
            self.__workers.append(worker)

    def __finish(self):
        self.__print_verbose('Finishing ...')
        self.__results.sort(cmp=lambda x,y: x['id'] - y['id'])
        for result in self.__results:
            print result
        self.__print_verbose(' done !')

    def __print_verbose(self, msg):
        if self.__verbose:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def start(self):
        try:
            for worker in self.__workers:
                worker.start()
            while len(self.__results) < self.__num_jobs:
                result = self.__result_queue.get()
                self.__results.append(result)
        except Exception as err:
            traceback.print_exc()
        finally:
            self.__finish()


if __name__ == '__main__':
    c = Controller([{'name':'lskdfjs'}, {'name':'ksljdfs'}, {'name':'ksjdnfs'}, {'name':'ggtuna'}], 1, True)
    c.start()
