#!/usr/bin/env python

import csv
import re
import copy 

def OrderChoices(ordering, names):
    "Creates a list for each respondent, with choices ordered 1 = most-preferred"
    choices = [] 
    for order, name in zip(ordering, names):
        choices.append((int(order), name))
        choices.sort()
    return choices

def SimulateChoiceData(num_options, num_voters):
    "Used to simulate preference data" 
    preferences = []
    for voter in range(num_voters):
        choices = range(num_options)
        random.shuffle(choices)
        combo = zip(choices, range(num_options))
        combo.sort()
        preferences.append(combo)
    return preferences 

def ActualChoiceData(file_name):
    "Returns a list of all preferences as well as the names of all the choices."
    # reads in the data from a CSV file. Structure is timestamp, then the rank ordering e.g., 
    # ['2018/05/09 10:55:53 AM AST', '7', '2', '1', '9', '4', '3', '5', '6', '8']
    preferences = []; # will store everyone's preferences 
    with open(file_name, 'rb') as csvfile:
        csvreader = csv.reader(csvfile)
        header = csvreader.next()
        original_names = [re.search("\[.*", h).group(0) for h in header[1::]]  # grabs the choice names from the header row (starts at 1 b/c of timestamp)
        for index, row in enumerate(csvreader):
            preferences.append(OrderChoices(tuple(row[1::]), original_names))
    return {'preferences':preferences, 'original_names':original_names}

def GetVotingOutcome(preferences):
    "From the collection of preferences, tallys votes by name"
    votes = {}
    for preference in preferences:
        top_choice = preference[0][1] # [0] grabs first choice; the [1] is b/c that's where name is stored
        if top_choice in votes: 
            votes[top_choice] += 1
        else:
            votes[top_choice] = 1
    return votes 

def FracTopVoteGetter(voting_outcomes):
    "Gets the fraction of the vote going to the top vote-getter"
    votes_cast = 1.0 * sum(voting_outcomes.values())
    fractions = [v / votes_cast for v in voting_outcomes.values()]
    return max(fractions)

def WorstPerformingName(voting_outcomes, names):
    d = {}
    "Gets the worst-performing name. In case of ties, take first one in list."
    for name in names: # add back the 0s
        if name not in voting_outcomes.keys():
            d[name] = 0
        else:
            d[name] = voting_outcomes[name]
    fewest_votes = min(d.values())
    for name in d.keys():
        if d[name] == fewest_votes:
            break
    return name

def BestPerformingName(voting_outcomes):
    "Gets the best performing name"
    most_votes = max(voting_outcomes.values())
    for name in voting_outcomes.keys():
        if voting_outcomes[name] == most_votes:
            break
    return name

def RemoveName(preference, name_to_remove):
    "Takes an individual's ordered list of preferences and removes choices no longer available"
    new_preference = []
    for p in preference:
        if p[1] == name_to_remove:
            pass

        else:
            new_preference.append(p)
    return new_preference 

def PurgePreferences(preferences, name_to_remove):
    "Returns a new list of preferences w/ name_to_remove purged from all preferences"
    return [RemoveName(p, name_to_remove) for p in preferences]    

def PrintPreferences(voting_outcomes, original_names, names):
    "Print in vote-order those options getting non-zero number of votes"
    results = []
    for name in original_names: 
        if name in voting_outcomes.keys():
            results.append((voting_outcomes[name], name))
        else:
            if name in names:
                results.append((0, name))
            else:
                results.append((-1, name))            
    results.sort(reverse = True)
    break_printed = False 
    for r in results:
        if r[0] < 0 and not break_printed:
            break_printed = True
            print "-----------removed---------------"
        print "Votes: %s" % r[0] + " Name: %s" % r[1]


def FindWinner(preferences, original_names, cutoff): 
    new_preferences = copy.deepcopy(preferences)
    names = copy.deepcopy(original_names)
    round = 0
    while True:
        round += 1 
        print ""
        print "" 
        print "################################################"
        print "##                Round %s                    ##" % round
        print "################################################"
        
        voting_outcomes = GetVotingOutcome(new_preferences)
        PrintPreferences(voting_outcomes, original_names, names)
        frac_going_to_top = FracTopVoteGetter(voting_outcomes)
        print ""
        print "Fraction of vote going to top-voting name %s" % frac_going_to_top
        if frac_going_to_top > cutoff:
            print "Habemus Papam! Our new name is: %s" % BestPerformingName(voting_outcomes)
            break 
        else:
            worst_name = WorstPerformingName(voting_outcomes, names)
            print "We need top vote-getter to have %s of the vote." % CUTOFF
            print "We're dropping from consideration: %s" % worst_name
            new_preferences = PurgePreferences(new_preferences, worst_name)
            names.remove(worst_name)

# Actual results 
voting_results = ActualChoiceData("faculty_vote_results.csv")
FindWinner(voting_results['preferences'], voting_results['original_names'], 0.5)

# Simulated results 
num_choices = 5
num_voters = 30
preferences = SimulateChoiceData(num_choices, num_voters)
choice_names = range(num_choices)
FindWinner(preferences, choice_names, 0.5)
