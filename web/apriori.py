# -*- coding: utf-8 -*-
# https://docs.python.org/3/library/collections.html#defaultdictw-examples
from collections import defaultdict

from itertools import combinations, chain

from datetime import datetime


def open_dataset(file):
    """
        Open the dataset and yield an iterator
    """
    file_iterator = open(file, 'r')
    for line in file_iterator:
        line = line.strip().rstrip(' ')
        yield frozenset(line.split(' '))


def read_dataset(data_iterator):
    """
        Read the dataset and return transactions
        This is not the way the material do. But we're trying to not
        do a second pass over the whole transaction dataset.

    """
    elements_on_set = set()
    transactions = list()
    for line in data_iterator:
        transactions.append(line)
        for item in line:
            elements_on_set.add(frozenset([item]))  # Generate 1-itemSets
    return elements_on_set, transactions


# def init_pass(transactions):
#     """
#         This is the way is done in the material. But this mean two
#         passes over the whole transaction dataset.
#         First pass over transaction. Return all possibles elements.
#     """
#     elements_on_set = set()
#     for transaction in transactions:
#         for item in transaction:
#             elements_on_set.add(frozenset([item]))  # Generate 1-itemSets
#     return elements_on_set


def frequents_from_candidates(transactions, minsup, set_counts, candidates):
    """
        Calculate the frequents from the list of candidates
    """
    frequents_items = set()
    set_counts_local = defaultdict(int)
    for transaction in transactions:
        for candidate in candidates:
            if candidate.issubset(transaction):
                set_counts[candidate] += 1
                set_counts_local[candidate] += 1
    for candidate, count in set_counts_local.items():
        if (count / len(transactions)) >= minsup:
            frequents_items.add(candidate)
    return frequents_items


def candidate_gen(current_set, length):
    """
        Generate the candidate of len equals (lenght).
        This is the same as:
            output = set()
            for i in current_set:
                for j in current_set:
                if len(i.union(j)) == length:
                    output.add(i.union(j))
            return output
    """
    return set([i.union(j) for i in current_set for j in current_set if len(i.union(j)) == length])


def apriori(minsup=0.3, minconf=0.8, dataset='../datasets/example.dat'):
    start = datetime.now()
    c1, transactions = read_dataset(open_dataset(dataset))
    set_counts = defaultdict(int)
    total_set = dict()

    # c1 = init_pass(transactions)  # line 1
    f1 = frequents_from_candidates(transactions, minsup, set_counts, c1)
    k = 2
    current_set = f1
    while current_set:
        total_set[k - 1] = current_set
        ck = candidate_gen(current_set, k)
        fk = frequents_from_candidates(transactions, minsup, set_counts, ck)
        current_set = fk
        k += 1

    # TODO: Find a better way to do this
    tts_set = dict()
    for key, value in total_set.items():
        if key != 1:
            tts_set[key] = value

    rules = []
    for key, value in tts_set.items():
        for item in value:
            for subset in map(frozenset, [x for x in chain(*[combinations(item, i + 1) for i, a in enumerate(item)])]):
                rest = item.difference(subset)
                if len(rest) > 0:
                    conf = set_counts[item] / set_counts[subset]
                    if conf >= minconf:
                        rules.append(((tuple(subset), tuple(rest)),
                                      conf))
    for r in rules:
        print (str(r[0][0]) + '->' + str(r[0][1]) + '. Conf: ' + str(r[1]))
    elapsed = datetime.now() - start
    print(elapsed)
    return rules, elapsed
