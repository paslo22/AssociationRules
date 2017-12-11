# -*- coding: utf-8 -*-
# https://docs.python.org/3/library/collections.html#defaultdictw-examples
from collections import defaultdict, Set

from itertools import combinations, chain
import operator

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

    def update_state(self, state):
        if current_task:
            current_task.update_state(state=state, meta={
                'elapsed': find_now(self.start),
                'c1': json.dumps(self.c1, cls=SetEncoder),
                'total_set': json.dumps(self.total_set, cls=SetEncoder),
                'rules': json.dumps(sorted(
                    self.rules,
                    key=operator.itemgetter(1, 2),
                    reverse=True
                ))
            })

    def rules_one_consecuent(self, frecuent):
        consecuents_valids = set()
        for consecuent in map(frozenset, combinations(frecuent, 1)):
            rest = frecuent.difference(consecuent)
            conf = self.set_counts[frecuent] / self.set_counts[rest]
            sup = self.set_counts[frecuent] / len(self.transactions)
            if conf >= self.minconf and sup >= self.minsup:
                consecuents_valids.add(consecuent)
                self.rules.append(((tuple(rest), tuple(consecuent)),
                                   round(conf, 2), round(sup, 2)))
            self.update_state(states.PENDING)
        return consecuents_valids

    def gen_rules(self, frecuent, consecuents, k, m):
        if consecuents and k > m + 1:
            candidates = self.candidate_gen(consecuents, m + 1)
            next_h = set()
            for candidate in candidates:
                rest = frecuent.difference(candidate)
                conf = self.set_counts[frecuent] / self.set_counts[rest]
                sup = self.set_counts[frecuent] / len(self.transactions)
                if conf >= self.minconf and sup >= self.minsup:
                    self.rules.append(((tuple(rest), tuple(candidate)),
                                       round(conf, 2), round(sup, 2)))
                    next_h.add(candidate)
                self.update_state(states.PENDING)
            self.gen_rules(frecuent, next_h, k, m + 1)

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

        for key, value in self.total_set.items():
            if key == 1:
                continue
            for item in value:
                self.gen_rules(item, self.rules_one_consecuent(item), key, 1)
        self.update_state(states.SUCCESS)
        if current_task:
            raise Ignore()
        for r in self.rules:
            print (str(r[0][0]) + '->' + str(r[0][1]) + '. Conf: ' + str(r[1]))
        return len(self.rules), str(datetime.now() - self.start)
