# -*- coding: utf-8 -*-
from collections import defaultdict, Set
from itertools import combinations

import operator

from datetime import datetime

from celery import current_task, states
from celery.exceptions import Ignore

import json


class SetEncoder(json.JSONEncoder):
    """
        This helpers is used to json encode sets.
    """
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
        # In the next lines the white spaces are striped
        line = line.strip().rstrip(' ')
        yield frozenset(line.split(' '))


def read_dataset(data_iterator):
    """
        In transaction are stored all the transaction from the
        dataset.
        In elements_on_set are stored all 1-candidates generated
        using the iterator from open_dataset.
        This is not the way the material do. But we're trying to not
        do a second pass over the whole transaction dataset.
    """
    elements_on_set = set()
    transactions = list()
    for line in data_iterator:
        transactions.append(line)
        for item in line:
            elements_on_set.add(frozenset([item]))
    return elements_on_set, transactions


def find_now(start):
    """
        Calculate the amount of time passed from the start
        of the algorithm
    """
    return str(datetime.now() - start)


class Apriori(object):

    def __init__(self, file, minsup=0.3, minconf=0.8):
        """
            This is the constructor, if minsup or minconf are not
            provided takes 0.3 and 0.8 as defaults.
            set_counts is a counter that keep track of the amount
            of times a itemset appear and calculate the conf.
        """
        self.minsup = minsup
        self.minconf = minconf
        self.file = file
        self.set_counts = defaultdict(int)
        self.total_set = dict()
        self.rules = []

    def frequents_from_candidates(self, candidates):
        """
            Calculate the frequents from the set of candidates.
            The candidate is added to frequents_items if it
            support is greater than minsup.
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
            current_set got the frequents items for this iteration.
            This function use joint union between all the frequents items
            keeping only the ones that are of the length required.
        """
        return set([i.union(j) for i in current_set for j in current_set if len(i.union(j)) == length])

    def update_state(self, state):
        """
            This function update the state of the running thread.
            This update this metadata:
                - elapsed: Time elapsed so far.
                - total_set: Frequents items.
                - rules: Rules ordered by conf and sup.
        """
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
        """
            This function generate the 1-consecuent rules from
            frecuents items if their conf is greater than minconf
            and their sup is greater than minsup.
            This also return the consecuents of the rules generated.
        """
        consecuents_valids = set()
        for consecuent in map(frozenset, combinations(frecuent, 1)):
            rest = frecuent.difference(consecuent)
            conf = self.set_counts[frecuent] / self.set_counts[rest]
            sup = self.set_counts[frecuent] / len(self.transactions)
            if conf >= self.minconf and sup >= self.minsup:
                consecuents_valids.add(consecuent)
                self.rules.append(((tuple(rest), tuple(consecuent)),
                                   round(conf, 2), round(sup, 2)))
        return consecuents_valids

    def gen_rules(self, frecuent, consecuents, k, m):
        """
            This function generate the n-consecuents rules.
            It use the consecuent part of the rules with one
            consecuent to generate the candidates and then use
            these candidates to generate the rules.
            If those rules got conf greater than minconf and
            sup greater than minsup, they are added to rules
            as valid.
        """
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
            self.gen_rules(frecuent, next_h, k, m + 1)

    def apriori(self):
        """
            This is the main function.
        """
        # start keep the moment that the algorithm start.
        self.start = datetime.now()
        # c1 got the 1-candidates. And transaction got all the transcation
        # in the dataset.
        self.c1, self.transactions = read_dataset(open_dataset(self.file))
        self.update_state(states.PENDING)
        # f1 got the 1-frequents items
        self.f1 = self.frequents_from_candidates(self.c1)
        self.update_state(states.PENDING)
        k = 2
        current_set = self.f1
        # current_set keep the frequents generated in the previous
        # iteration. If it is empty, the recursion stops.
        while current_set:
            # save the k-1-frequents items.
            self.total_set[k - 1] = current_set
            self.update_state(states.PENDING)
            # generate the k-candidates
            ck = self.candidate_gen(current_set, k)
            # generate the k-candidates
            current_set = self.frequents_from_candidates(ck)
            k += 1
        # total_set got all the frequents items.
        for key, value in self.total_set.items():
            # skip the 1-frequents items.
            if key == 1:
                continue
            for item in value:
                # call gen_rules with every k-frequents.
                self.gen_rules(item, self.rules_one_consecuent(item), key, 1)
            self.update_state(states.PENDING)
        self.update_state(states.SUCCESS)
        if current_task:
            raise Ignore()
        for r in self.rules:
            print (str(r[0][0]) + '->' + str(r[0][1]) + '. Conf: ' + str(r[1]))
        return len(self.rules), str(datetime.now() - self.start)
