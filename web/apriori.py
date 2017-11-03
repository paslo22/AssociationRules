# -*- coding: utf-8 -*-
# https://docs.python.org/3/library/collections.html#defaultdictw-examples
from collections import defaultdict, Set

from itertools import combinations, chain

from datetime import datetime

from celery import current_task, states
from celery.exceptions import Ignore

import json


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Set):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def open_dataset(file):
    """
        Open the dataset and yield an iterator
    """
    file.open(mode='r')
    for line in file:
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


def find_now(start):
    return str(datetime.now() - start)


class Apriori(object):

    def __init__(self, file, minsup=0.3, minconf=0.8):
        self.minsup = minsup
        self.minconf = minconf
        self.file = file
        self.set_counts = defaultdict(int)
        self.total_set = dict()
        self.rules = []

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

    def frequents_from_candidates(self, candidates):
        """
            Calculate the frequents from the list of candidates
        """
        frequents_items = set()
        set_counts_local = defaultdict(int)
        for transaction in self.transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    self.set_counts[candidate] += 1
                    set_counts_local[candidate] += 1
            self.update_state(states.PENDING)
        for candidate, count in set_counts_local.items():
            if (count / len(self.transactions)) >= self.minsup:
                frequents_items.add(candidate)
        return frequents_items

    def candidate_gen(self, current_set, length):
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

    def update_state(self, estado):
        current_task.update_state(state=estado, meta={
            'elapsed': find_now(self.start),
            'c1': json.dumps(self.c1, cls=SetEncoder),
            'total_set': json.dumps(self.total_set, cls=SetEncoder),
            'rules': json.dumps(self.rules)
        })

    def apriori(self):
        self.start = datetime.now()
        self.c1, self.transactions = read_dataset(open_dataset(self.file))
        self.update_state(states.PENDING)
        # c1 = init_pass(transactions)  # line 1
        self.f1 = self.frequents_from_candidates(self.c1)
        self.update_state(states.PENDING)
        k = 2
        current_set = self.f1
        while current_set:
            self.total_set[k - 1] = current_set
            self.update_state(states.PENDING)
            ck = self.candidate_gen(current_set, k)
            current_set = self.frequents_from_candidates(ck)
            k += 1

        # TODO: Find a better way to do this
        tts_set = dict()
        for key, value in self.total_set.items():
            if key != 1:
                tts_set[key] = value

        for key, value in tts_set.items():
            for item in value:
                for subset in map(frozenset, [x for x in chain(*[combinations(item, i + 1) for i, a in enumerate(item)])]):
                    rest = item.difference(subset)
                    if len(rest) > 0:
                        conf = self.set_counts[item] / self.set_counts[subset]
                        if conf >= self.minconf:
                            self.rules.append(((tuple(subset), tuple(rest)),
                                              round(conf, 2)))
                self.update_state(states.PENDING)
            self.update_state(states.PENDING)
        self.update_state(states.SUCCESS)
        raise Ignore()
        return self.rules, datetime.now() - self.start
