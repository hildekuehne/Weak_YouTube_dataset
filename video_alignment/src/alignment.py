#!/usr/bin/python2.7

import numpy as np
import Queue
import os
from utils.dataset import Dataset
from utils.gmm import GMM
from utils.grammar import PathGrammar
from utils.length_model import PoissonModel
from utils.viterbi import Viterbi
from matplotlib import pyplot as plt
import time
#from inference import root_dir

################################################################################
### EVAL                                                                   ###
################################################################################

### helper function for evaluating decoding ##########################
def eval(file1, file2):
    
    with open(file1) as f:
        lines1 = f.readlines()
    
    with open(file2) as f:
        lines2 = f.readlines()

    
    count_frames = len(lines1);
    count_correct = 0;
    for i in range (len(lines1)):
        if lines1[i].strip() ==  lines2[i].strip():
            count_correct = count_correct+1;
            
    return count_correct, count_frames;            
    


################################################################################
### MAIN                                                                     ###
################################################################################
if __name__ == '__main__':

    
    # Needed:
    # Dictionary file
    file_dict = './data/weakYouTube_dict.txt';
    # length model (use dummy value if nothing else)
    file_length = './data/weakYouTube_length.txt';
    # grammar or transcript file (1 line = transcript, > 1 line = grammar)
    file_grammar = './data/grammar/-1okAudsnAc.grammar';
    # the probability input (replace with your own data)
    file_probs = './data/probs/-1okAudsnAc.probs';
    
    # Output:
    # labels
    file_out= './data/out/-1okAudsnAc.res';
    #  MoF accuracy (if ground truth is provided)
    file_acc= './data/out/-1okAudsnAc.acc';
    
    # if you want evaluation:
    file_gt = './data/gt/-1okAudsnAc.gt';
  
    
    # read label2index mapping and index2label mapping
    label2index = dict()
    index2label = dict()
    with open(file_dict, 'r') as f:
        content = f.read().split('\n')[0:-1]
        idx_count = 0;
        for line in content:
            line = line.strip();
            label2index[line] = idx_count;
            index2label[idx_count] = line;
            idx_count = idx_count + 1;

    
    # load grammar
    print('Running: '+file_grammar)
    grammar = PathGrammar(file_grammar, label2index);
    
    # load lm
    length_model = PoissonModel(file_length, max_length = 5000)
    
    # load your data here (must be in log space!!!): 
    # Note that you might want to remove a prior first.
    log_probs = np.loadtxt(file_probs, dtype=np.float32);
    
    # sanity check
    print(np.max(log_probs))
    print(np.min(log_probs))
    
    # scale down if out of range
    if np.max(log_probs) > 0:
        log_probs = log_probs - (2*np.max(log_probs));
        
    # Viterbi decoder (max_hypotheses = n: at each time step, prune all hypotheses worse than the top n)
    viterbi_decoder = Viterbi(grammar, length_model, frame_sampling = 20, max_hypotheses = 50000 );
    
    # Viterbi decoding
    print('Processing ' + file_probs)
    print('Result file ' + file_out);

    try:
        start = time.time()
        score, labels, segments = viterbi_decoder.decode( log_probs )
        end = time.time()
        print(end - start)
        # save result
        with open(file_out, 'w') as f:
            for l in labels:
                f.write( index2label[l] + '\n' )
    except Queue.Empty:
        pass
    
    count_correct, count_frames = eval(file_out, file_gt);
    
    print('Accuracy: ' + str( float(count_correct) / float(count_frames) ));
    # save result
    with open(file_acc, 'w') as f:
        f.write( 'Accuracy : \n' )
        f.write( str( float(count_correct) / float(count_frames) ) + '\n' )
