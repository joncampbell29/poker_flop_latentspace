from itertools import product, combinations
import numpy as np
import torch
import torch.nn as nn

with open('one_possible_straights.txt','r') as f:
    ONE_POSSIBLE_STRAIGHT = []
    for i in f.readlines():
        h = i.strip()
        ONE_POSSIBLE_STRAIGHT.append(tuple(sorted((h[0], h[2], h[4]))))
        
ONE_POSSIBLE_STRAIGHT = set(ONE_POSSIBLE_STRAIGHT)
        
with open('two_possible_straights.txt','r') as f:
    TWO_POSSIBLE_STRAIGHTS = []
    for i in f.readlines():
        h = i.strip()
        TWO_POSSIBLE_STRAIGHTS.append(tuple(sorted((h[0], h[2], h[4]))))

TWO_POSSIBLE_STRAIGHTS = set(TWO_POSSIBLE_STRAIGHTS)
 
        
with open('three_possible_straights.txt','r') as f:
    THREE_POSSIBLE_STRAIGHTS = []
    for i in f.readlines():
        h = i.strip()
        THREE_POSSIBLE_STRAIGHTS.append(tuple(sorted((h[0], h[2], h[4]))))
        
THREE_POSSIBLE_STRAIGHTS = set(THREE_POSSIBLE_STRAIGHTS)

CONNECTED_FLOPS = ONE_POSSIBLE_STRAIGHT\
    .union(TWO_POSSIBLE_STRAIGHTS)\
        .union(THREE_POSSIBLE_STRAIGHTS)
        

        
RANKS = [str(i) for i in range(2,10)] + ['T','J','Q','K','A']
SUITS = ['s','h','c','d']

RANKS_DICT_TRUE = {str(i): i for i in range(2, 10)}
RANKS_DICT_TRUE.update({'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14})

RANKS_DICT_IDX = {rank: i for i, rank in enumerate(RANKS)}
RANKS_DICT_IDX_REV = {i: rank for i, rank in enumerate(RANKS)}
VECTOR_IDX_DICT = RANKS_DICT_IDX_REV.copy()
VECTOR_IDX_DICT.update({13:'s',14:'h',15:'c',16:'d',
                        17:'2',18:'3',19:'4',20:'5',21:'6',22:'7',23:'8',24:'9',25:'T',26:'J',27:'Q',28:'K',29:'A',
                        30:'s',31:'h',32:'c',33:'d',
                        34:'2',35:'3',36:'4',37:'5',38:'6',39:'7',40:'8',41:'9',42:'T',43:'J',44:'Q',45:'K',46:'A',
                        47:'s',48:'h',49:'c',50:'d'})

SUITS_DICT = {suit: i for i, suit in enumerate(SUITS)}
SUITS_DICT_REV = {j: i for i, j in SUITS_DICT.items()}

DECK = [rank+suit for rank, suit in product(RANKS, SUITS)]
FLOPS = list(combinations(DECK, 3))

def convert_to_numeric(flop, remove_dups=True):
    res = [RANKS_DICT_TRUE[card[:-1]] for card in flop]
    if remove_dups:
        return sorted(set(res))
    else:
        return sorted(res)

SUITEDNESS_DICT = {
    0: 'rainbow', # No card of same suit
    1: 'two_tone', # 2 of 3 of same suit
    2: 'monotone' # All same suit
}

def eval_suitedness(flop):
    suits = [card[-1] for card in flop]
    unique_suits, counts = np.unique(suits, return_counts=True)

    if len(unique_suits) == 3:
        return 0 # 'rainbow'
    elif len(unique_suits) == 2:
        return 1 # 'two_tone'
    else:
        return 2 # 'monotone'


PAIRNESS_DICT = {
    3: 'high_pair', # AAx-JJx
    2: 'middle_pair', # TTx-77x
    1: 'low_pair', # 66x-22x
    0: 'unpaired' # No pair
}

def eval_pairness(flop):
    flop_numeric = convert_to_numeric(flop, remove_dups=True)
    if len(flop_numeric) == 3:
        return 0 # 'unpaired'
    flop_numeric = convert_to_numeric(flop, remove_dups=False)

    vals, counts = np.unique(flop_numeric, return_counts=True)
    if counts[0] == 3:
        pair_rank = vals[counts == 3] 
    else:
        pair_rank = vals[counts == 2][0]

    
    if pair_rank >= 11:
        return 3 # 'high_pair'
    elif 7 <= pair_rank <= 10:
        return 2 # 'middle_pair'
    else:  
        return 1  # 'low_pair'
    

CONNECTEDNESS_DICT = {
    2: 'three_connected',
    1: 'two_connected',
    0: 'disconnected'
}

def eval_connectedness(flop):
    flop_numeric = convert_to_numeric(flop, remove_dups=False)
    if 14 in flop_numeric and 2 in flop_numeric:
        flop_numeric[flop_numeric.index(14)] = 1  # Convert A to 1 if A-2 scenario exists
        flop_numeric.sort()

    if flop_numeric[2] - flop_numeric[0] == 2 and flop_numeric[1] - flop_numeric[0] == 1:
        return 2  # 'three_connected'

    if flop_numeric[1] - flop_numeric[0] == 1 or flop_numeric[2] - flop_numeric[1] == 1:
        return 1  # 'two_connected'

    return 0  # 'disconnected'


HIGH_LOW_TEXTURE_DICT = {
    0: 'low', # 2 or 3 cards <= 8
    1: 'middle', # neither high or low
    2: 'high' # 2 or 3 broadway cards (T, J, Q, K, A)
}

def eval_high_low_texture(flop):
    broadway_ranks = {'T', 'J', 'Q', 'K', 'A'}

    ranks = [card[:-1] for card in flop]

    broadway_count = sum(1 for rank in ranks if rank in broadway_ranks)
    low_count = sum(1 for rank in ranks if rank.isdigit() and int(rank) <= 8)

    if broadway_count >= 2:
        return 2 # 'high'
    elif low_count >= 2:
        return 0 # 'low'
    else:
        return 1 # 'middle'

HIGH_CARD_DICT = {
    0: '2high', # 2 high
    1: '3high', # 3 high
    2: '4high', # 4 high
    3: '5high', # 5 high
    4: '6high', # 6 high
    5: '7high', # 7 high
    6: '8high', # 8 high
    7: '9high', # 9 high
    8: 'Thigh', # 10 high
    9: 'Jhigh', # J high
    10: 'Qhigh', # Q high
    11: 'Khigh', # K high
    12: 'Ahigh' # A high
    }

def eval_high_card(flop):
    flop_numeric = convert_to_numeric(flop)
    return flop_numeric[-1] - 2

STRAIGHTNESS_DICT = {
    0: 'no_possible', # no possible straights
    1: 'one_possible', # 1 possible straight
    2: 'two_possible', # 2 possible straights
    3: 'three_possible' # 3 possible straights
}

def eval_straightness(flop):
    ranks = tuple(sorted(i[0] for i in flop))
    if ranks in ONE_POSSIBLE_STRAIGHT:
        return 1
    elif ranks in TWO_POSSIBLE_STRAIGHTS:
        return 2
    elif ranks in THREE_POSSIBLE_STRAIGHTS:
        return 3
    else:
        return 0
        
def flop_to_vector(flop: list):
    flop.sort()
    fin_arr = []
    for rank, suit in flop:
        r = RANKS_DICT_IDX[rank]
        s = SUITS_DICT[suit]
        r_one_hot = nn.functional.one_hot(torch.tensor(r), 13)
        s_one_hot = nn.functional.one_hot(torch.tensor(s), 4)
        fin_arr.append(torch.cat([r_one_hot, s_one_hot]))
    return torch.cat(fin_arr)

def flop_look_up(flop: list, df):
    row = df[df.flop.apply(lambda x: sorted(x) == sorted(flop))]
    return row.iloc[0] if not row.empty else None

def vec_to_flop(flop_vector):
    def vec_transfrom(v):
        return RANKS_DICT_IDX_REV[v[0].argmax().item()] + SUITS_DICT_REV[v[1].argmax().item()] 
    
    vec_decomposed = [(v[:13],v[13:]) for v in flop_vector.hsplit(3)]
    return sorted([vec_transfrom(i) for i in vec_decomposed])