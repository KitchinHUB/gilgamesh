#!/usr/bin/env python
from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import Popen
from subprocess import PIPE
import datetime

def memory_warning(cutoff=4.0, node='-1', users=None):

    bpstat = Popen('bpstat -P {}'.format(str(node)).split(),
                   stdin=PIPE, stdout=PIPE)
    ls = Popen('ps -e -o pid,vsz,user,comm='.split(), stdout=bpstat.stdin)
    output = bpstat.communicate()[0]
    ls.wait()

    MEM = {}
    for line in output.split('\n')[1:-1]:

        if str(node) == '-1' or str(node) == 'master':
            ID = line.split()[0]
            mem = float(line.split()[1]) / 1e6
            user = line.split()[2]
            com = ' '.join(line.split()[3:])
        else:
            ID = line.split()[1]
            mem = float(line.split()[2]) / 1e6
            user = line.split()[3]
            com = ' '.join(line.split()[4:])
    
        if user not in MEM.keys():
            MEM[user] = [mem, [[mem, com, int(ID)]]]
        else:
            MEM[user][0] += mem
            MEM[user][1] += [[mem, com, int(ID)]]

    SUM = sum([v[0] for k, v in MEM.iteritems()])

    # sort by memory
    sort_users = [u for u, m in sorted([[k, v[0]] for k, v in MEM.iteritems()],
                                       key=lambda x: x[1], reverse=True)]

    if users is None:
        users = sort_users
    elif isinstance(users, str):
        users = [users]

    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    stdout = '{}\nTotal allocated memory: {:>24.2f} GB\n'.format(time, SUM)

    for user in users:
        tot, v = MEM[user]
        stdout += 'user: {:<34} {:>7.2f} GB\n'.format(user, tot)
        if tot > float(cutoff):
            stdout += '\n    Top 5 processes:\n'
            stdout += 'PID     MEM (GB)   COMM\n'

            ind = [i for i, l in sorted(enumerate(v),
                                        key=lambda x: x[1],
                                        reverse=True)]

            for i in ind[:5]:
                stdout += '{:<7} {:<10.2f} {:}\n'.format(v[i][2],
                                                         v[i][0],
                                                         v[i][1])
            stdout += '\n'

    return stdout


def cpu_warning(cutoff=2.0, node='-1', users=None):

    bpstat = Popen('bpstat -P {}'.format(str(node)).split(),
                   stdin=PIPE, stdout=PIPE)
    ls = Popen('ps -e -o pid,%cpu,user,comm='.split(), stdout=bpstat.stdin)
    output = bpstat.communicate()[0]
    ls.wait()

    CPU = {}
    for line in output.split('\n')[1:-1]:

        if str(node) == '-1' or str(node) == 'master':
            ID = line.split()[0]
            cpu = float(line.split()[1]) / 100
            user = line.split()[2]
            com = ' '.join(line.split()[3:])
        else:
            ID = line.split()[1]
            cpu = float(line.split()[2]) / 100
            user = line.split()[3]
            com = ' '.join(line.split()[4:])

        if user not in CPU.keys():
            CPU[user] = [cpu, [[cpu, com, int(ID)]]]
        else:
            CPU[user][0] += cpu
            CPU[user][1] += [[cpu, com, int(ID)]]

    SUM = sum([v[0] for k, v in CPU.iteritems()])

    # Sort by CPU usage
    sort_users = [u for u, m in sorted([[k, v[0]] for k, v in CPU.iteritems()],
                  key=lambda x: x[1], reverse=True)]

    if users is None:
        users = sort_users
    elif isinstance(users, str):
        users = [users]

    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    stdout = '{}\nCPU load: {:>38.2f} \n'.format(time, SUM)

    for user in users:
        tot, v = CPU[user]
        stdout += 'user: {:<34} {:>7.2f}\n'.format(user, tot)
        if tot > float(cutoff):
            stdout += '\n    Top 5 processes:\n'
            stdout += 'PID     CPU        COMM\n'

            ind = [i for i, l in sorted(enumerate(v),
                                        key=lambda x: x[1],
                                        reverse=True)]

            for i in ind[:5]:
                stdout += '{:<7} {:<10.2f} {:}\n'.format(v[i][2],
                                                         v[i][0],
                                                         v[i][1])
            stdout += '\n'

    return stdout

def main():
    for n in range(-1, 31):
        try:
            time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')

            node_mem = check_output(['bpsh', str(n), 'free'])
            mem0, mem1 = node_mem.split()[15:17]
            mem = (float(mem0) / (float(mem1) + float(mem0))) * 100.

            node_idle = check_output(['bpsh', str(n), 'mpstat'])
            # For some reason, the mpstat run by Cron returns military time
            # This changes the indexing which is accounted for here.
            try:
                cpu = 100. - float(node_idle.split()[26])
            except(IndexError):
                cpu = 100. - float(node_idle.split()[24])

            node_load = check_output(['bpsh', str(n), 'uptime'])
            load = node_load.split()[-3].rstrip(',')

            sto = '{} {:1.2f} {} {} \n'.format(time, mem, cpu, load)
            with open('/tmp/logs/node{}.log'.format(n), 'a') as f:
                f.write(sto)

            if n == -1:
                if mem > 80:
                    with open('/tmp/logs/memory-warning.log', 'a') as f:
                        f.write(memory_warning())
                if float(load) > 12.:
                    with open('/tmp/logs/cpu-warning.log', 'a') as f:
                        f.write(cpu_warning())
        except(CalledProcessError):
            pass

if __name__ == "__main__":
    main()
