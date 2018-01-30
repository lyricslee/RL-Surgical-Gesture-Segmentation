import os
import numpy as np 
from subprocess import Popen
from config import *

import pdb

# This is an awkward solution since I dont know how to run multiple tf sessions..

def experiment_tcn():
    
    tcn_cmd = 'python3 tcn_main.py'
    os.system(tcn_cmd)

    # Get Averaged Results: TCN
    template = 'tcn_result_{}_run_{}.npy'
    for feature_type in ['sensor', 'visual']:
        tcn_result = np.zeros((tcn_run_num, split_num, 6))
        for tcn_run_idx in range(1, 1 + tcn_run_num):
            run_result_file = template.format(feature_type, tcn_run_idx)
            run_result_file = os.path.join(result_dir, run_result_file)
            tcn_result[tcn_run_idx-1,:,:] = np.load(run_result_file)
            os.remove(run_result_file)

        tcn_result_file = 'tcn_avg_result_{}.npy'.format(feature_type)
        tcn_result_file = os.path.join(result_dir, tcn_result_file)
        #np.save(tcn_result_file, tcn_result.mean(0).mean(0))
        np.save(tcn_result_file, tcn_result)


def experiment_trpo(naming):

    trpo_train_cmd = 'python3 trpo_train.py '
    trpo_test_cmd = 'python3 trpo_test.py '
    cmd_args = '--feature_type {} --tcn_run_idx {} --split_idx {} --run_idx {}'

    # Run TRPO in paralell    
    for tcn_run_idx in range(1, 1 + tcn_run_num):
        for split_idx in range(1, 1 + split_num):
            for run_idx in range(1, 1 + trpo_train_run_num):

                processes = []
                for feature_type in ['sensor', 'visual']:
                    formatted_args = cmd_args.format(
                        feature_type, tcn_run_idx, split_idx, run_idx)
                    full_cmd = trpo_train_cmd + formatted_args
                    # full_cmd = 'echo ' + full_cmd + ';sleep 1' # test
                    processes.append(Popen(full_cmd, shell=True))

                exitcodes = [p.wait() for p in processes]
                if sum(exitcodes) != 0:
                    raise Exception('Subprocess Error!')


    # Get Averaged Results: TRPO
    template = 'result_{}_tcn_{}_split_{}_run_{}.npy'
    for feature_type in ['sensor', 'visual']:
        trpo_result = np.zeros((tcn_run_num, split_num,
                            trpo_train_run_num, trpo_test_run_num, 9))
        for tcn_run_idx in range(1, 1 + tcn_run_num):
            for split_idx in range(1, 1 + split_num):
                for run_idx in range(1, 1 + trpo_train_run_num):
                    run_result_file = template.format(
                        feature_type, tcn_run_idx, split_idx, run_idx)
                    run_result_file = os.path.join(result_dir, run_result_file)
                    run_result = np.load(run_result_file)
                    run_result = run_result.mean(0)
                    trpo_result[tcn_run_idx-1,split_idx-1,run_idx-1,:,:] = run_result
                    os.remove(run_result_file)

        trpo_result_file = 'trpo_avg_result_{}_{}.npy'.format(feature_type, naming)
        trpo_result_file = os.path.join(result_dir, trpo_result_file)
        #np.save(trpo_result_file, trpo_result.mean(0).mean(0).mean(0).mean(0))
        np.save(trpo_result_file, trpo_result)


def main():
    experiment_tcn()
    experiment_trpo('baseline')


if __name__ == '__main__':
    main()