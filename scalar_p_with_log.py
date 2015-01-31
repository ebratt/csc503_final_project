from psim import *
import sys
import random
import timeit as ti
import platform
from matplotlib import pyplot as plt
import numpy as np
import os.path

bases = []
logfile = 'scalar_p.log'
n = 5500
log_flag = True
topology = SWITCH


def log(message):
    """
    logs the message into the logfile
    """
    with open(logfile, 'a') as f:
        f.write(message)
        f.close()


def log_sysinfo():
    sysinfo =  '\n\n****SYSTEM INFORMATION****\n'
    sysinfo += 'Python version  : %s\n' % platform.python_version()
    sysinfo += 'compiler        : %s\n' % platform.python_compiler()
    sysinfo += 'system          : %s\n' % platform.system()
    sysinfo += 'release         : %s\n' % platform.release()
    sysinfo += 'machine         : %s\n' % platform.machine()
    sysinfo += 'interpreter     : %s\n' % platform.architecture()[0]
    sysinfo += 'node            : %s\n' % platform.node()
    sysinfo += 'platforrm       : %s\n' % platform.platform()
    sysinfo += '\n\n'
    log(sysinfo)


def plot_results():
    bar_labels = ['serial', '2', '3', '4', '6']
    fig = plt.figure(figsize=(10,8))
    # plot bars
    y_pos = np.arange(len(bases))
    plt.yticks(y_pos, bar_labels, fontsize=16)
    bars = plt.barh(y_pos, bases,
         align='center', alpha=0.4, color='g')
    # annotation and labels
    for ba,be in zip(bars, bases):
        plt.text(ba.get_width() + 1.4, ba.get_y() + ba.get_height()/2,
            '{0:.2%}'.format(bases[0]/be),
            ha='center', va='bottom', fontsize=11)
    plt.xlabel('time in seconds for n=%s\ntopology: %s' % 
               (n,repr(topology)), fontsize=14)
    plt.ylabel('number of processes\n', fontsize=14)
    t = plt.title('Serial vs. Parallel Scalar Product', fontsize=18)
    plt.ylim([-1,len(bases)+0.5])
    plt.xlim([0,max(bases)*1.1])
    plt.vlines(bases[0], -1, len(bases)+0.5, linestyles='dashed')
    plt.grid()
    plt.show()
    

def run_parallel(p):
    to_log =  '\n\n****PARALLEL****\n'
    comm = PSim(p, topology)
    source = 0
    if comm.rank == source:
        a = [random.random() for k in range(n)]
        b = [random.random() for k in range(n)]
        head = min(n, 5)
        to_log += 'head of a        : %s\n' % a[:head]
        to_log += 'head of b        : %s\n' % b[:head]
        log(to_log)
        s = 0.0
        for k in range(n):
            s += a[k]*b[k]
    else:
        a = b = None
    a = comm.one2all_scatter(source, a)
    b = comm.one2all_scatter(source, b)
    s = 0.0
    for k in range(len(a)):
        s += a[k]*b[k]
    s = comm.all2one_reduce(source, s)
    if comm.rank==source:
        to_log =  'topology         : %s\n' % repr(topology)
        to_log += 'num procs        : %i\n' % p
        to_log += 'parallel result  : %d\n' % s
        to_log += 'num elems        : %i\n' % n
        if log_flag:
            log(to_log)
        else:
            print to_log
    else:
        sys.exit(0)
    

def run_serial():
    a = [random.random() for k in range(n)]
    b = [random.random() for k in range(n)]
    s = 0.0
    for k in range(n):
        s += a[k]*b[k]
    if log_flag: 
        head = min(n, 5)
        to_log =  '\n\n****SERIAL****\n'
        to_log +=  'head of a       : %s\n' % a[:head]
        to_log += 'head of b       : %s\n' % b[:head]
        to_log += 'serial result:  : %d\n' % s
        to_log += 'number of elems : %d\n' % n
        log(to_log)        
    else:
        print 'serial result       : %d\n' % s
        print 'number of elems     : %d\n' % n


if __name__ == '__main__':
    random.seed(123)
    if os.path.exists(logfile): os.remove(logfile)
    bases.append(ti.timeit(stmt='run_serial()',
                           setup='from __main__ import run_serial',
                           number=1))
    for i in 2,3,4,6:
        bases.append(ti.timeit(stmt='run_parallel(%i)' % i,
                           setup='from __main__ import run_parallel',
                           number=1))
    plot_results()
    log_sysinfo()
