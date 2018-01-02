# coding: utf-8
# Blackjack with Reinforcement learning
# Author: Jong-Chin Lin <jongchin.lin2@aexp.com>

import random

class Hand:
    def __init__(self,role):
        self.role = role
        self.score = 0
        self.cards = []
        self.stick = False
        self.states = []
        self.usableAce = False

    def hit(self,card):
        self.score = self.handScore(self.score,card)
        self.cards.append(card)

    def cardState(self,card):
        temp = card
        if card in ['J','Q','K']:
           temp = '10'
        return temp

    def handScore(self,score,card):
        #temp = self.cardScore(card)
        temp = 0
        if card in ['J','Q','K']:
           temp = 10
        elif card == 'A':
            if score < 11:
                temp = 11
                self.usableAce = True
            else:
                temp = 1
        else:
            temp = int(card)
        score += temp
        if score > 21 and self.usableAce:
            score -= 10
            self.usableAce = False
        return score


class Player(Hand):
    def __init__(self):
        Hand.__init__(self, 'Player')

    def policyA(self,card):
    #while self.score <= 21:
        if self.score < 20:
            self.hit(card)
            self.states.append(self.score)
        else:
            self.stick = True

    def policyES(self,card, dealer):
        '''
        Initialize, for all s ∈ S, a ∈ A(s):
            Q(s, a) ← arbitrary
            π(s) ← arbitrary
            Returns(s, a) ← empty list
        Repeat forever:
        Choose S0 ∈ S and A0 ∈ A(S0) s.t. all pairs have probability > 0
        Generate an episode starting from S0,A0, following π
        For each pair s, a appearing in the episode:
            G ← the return that follows the first occurrence of s, a Append G to Returns(s, a)
            Q(s, a) ← average(Returns(s, a))
        For each s in the episode:
            π(s) ← argmaxa Q(s,a)
        '''
        # Randomly select S0 from 12-21
        #s = random.randint(12,21)
        #a = random.choice(['h','s'])

        #if s not in self.qvalues:
        #    self.qvalues[s] = {'h': 0.0, 's': 0.0}
        #else:
        #    actions = self.qvalues[s]

        #action = max(actions, key=lambda k: (actions[k], random.random()))
        #self.player.score = s

        s = self.score
        state = (s, dealer.cardState(dealer.cards[1]), self.usableAce)

        actions = self.qvalues[state]
        action = max(actions, key=lambda k: (actions[k], random.random()))
        if action == 'h':
            self.hit(card)
            self.states.append(self.score)
        else:
            self.stick = True


        
class Dealer(Hand):
    def __init__(self):
        Hand.__init__(self, 'Dealer')

    def policy(self,card):
        if self.score < 17:
            self.hit(card)
        else:
            self.stick = True


class Blackjack:
    def __init__(self):
        self.cards = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
        self.dealer = Dealer()
        self.player = Player()
        self.hidden = True # Whether first card of dealer's hand is hidden
        self.opening = True
        self.records = {} # (frequency, sum of rewards observed) for a state, (player sum, dealer card, usableAce)
        self.finalReward = 0
        self.winLoss = {1:0,0:0,-1:0}
        self.qvalues = {} # Q(s,a)
        self.frequency = {} # N(s,a)

    def dealCard(self,hand):
        card = random.choice(self.cards)
        if hand == 'P':
            self.player.hit(card)
        elif hand == 'D':
            self.dealer.hit(card)

    def status(self):
        print "\nDealer's hand:"
        if self.hidden:
            print 'X,', self.dealer.cards[1]
        else:
            print ','.join(self.dealer.cards)
            print 'score:',self.dealer.score
        print "Player's hand:"
        print ','.join(self.player.cards)
        print 'score:',self.player.score

        if not self.opening:
            if self.player.score > 21 and self.hidden:
                print 'Go bust!!'
                print 'Player lose!'
                self.finalReward = -1.0
            else:
                if self.dealer.score > 21 or self.dealer.score < self.player.score:
                    print 'Player win!'
                    self.finalReward = 1
                elif self.dealer.score == self.player.score:
                    print 'Draw!'
                    self.finalReward = 0
                else:
                    print 'Player lose!'
                    self.finalReward = -1
                #state = (self.player.score, self.dealer.cardState(self.dealer.cards[1]))
                #self.updateRecords(state, self.finalReward)
        print 'States:',self.player.states

    def getRecords(self):
        print 'Records:',self.records

    def getQvalues(self):
        print 'Qvalues:',self.qvalues

    def getFrequency(self):
        print 'Frequency:',self.frequency


    def reset(self):
        self.hidden = True
        self.opening = True
        self.player.cards = []
        self.dealer.cards = []
        self.player.score = 0
        self.dealer.score = 0
        self.finalReward = 0
        self.player.states = []
        self.player.stick = False

    def updateRecords(self,state,reward):
        if state not in self.records:
            self.records[state] = (1,reward)
        else:
            self.records[state] = (self.records[state][0]+1, self.records[state][1]+reward)

    def updateQ(self,state,action, reward):
        if state not in self.qvalues:
            self.qvalues[state] = {'s': 0, 'h': 0}
            self.qvalues[state] = {action: reward}
        else:
            self.qvalues[state][action] += reward

    def updateN(self, state, action):
        if state not in self.frequency:
            self.frequency[state] = {'s': 0, 'h': 0}
            self.frequency[state] = {action: 1}
        else:
            self.frequency[state][action] += 1

    def averageReturn(self):
        print '\nAverage return:'
        print 'State, frequency, AverageReturn'
        for state in self.records:
            avg = self.records[state][1]*1.0 / self.records[state][0]
            print state,',',self.records[state][0],',',avg

    def policyES(self,card):
        '''
        Initialize, for all s ∈ S, a ∈ A(s):
            Q(s, a) ← arbitrary
            π(s) ← arbitrary
            Returns(s, a) ← empty list
        Repeat forever:
        Choose S0 ∈ S and A0 ∈ A(S0) s.t. all pairs have probability > 0
        Generate an episode starting from S0,A0, following π
        For each pair s, a appearing in the episode:
            G ← the return that follows the first occurrence of s, a Append G to Returns(s, a)
            Q(s, a) ← average(Returns(s, a))
        For each s in the episode:
            π(s) ← argmaxa Q(s,a)
        '''
        # Randomly select S0 from 12-21
        #s = random.randint(12,21)
        #a = random.choice(['h','s'])

        #if s not in self.qvalues:
        #    self.qvalues[s] = {'h': 0.0, 's': 0.0}
        #else:
        #    actions = self.qvalues[s]

        #action = max(actions, key=lambda k: (actions[k], random.random()))
        #self.player.score = s

        s = self.player.score
        state = (s, self.dealer.cardState(self.dealer.cards[1]), self.player.usableAce)

        if state not in self.qvalues:
            self.qvalues[s] = {'h': 0, 's': 0}
        else:
            actions = self.qvalues[state]
        action = max(actions, key=lambda k: (actions[k], random.random()))
        if action == 'h':
            self.hit(card)
            self.states.append(self.score)
        else:
            self.player.stick = True

    def playGame(self):
        # Opening
        self.dealCard('P')
        self.dealCard('P')
        self.dealCard('D')
        self.dealCard('D')
        self.player.states = [self.player.score]
        self.status()
        # Player's turn
        self.opening = False

        # Generate an episode according to policyA (stick when player score = 20 or 21, hit otherwise)
        while self.player.score <= 21 and not self.player.stick:
            previousScore = self.player.score
            card = random.choice(self.cards)
            self.player.policyA(card)
            '''
            if (not self.player.stick) and self.player.score <= 21:
                state = (previousScore, self.dealer.cardState(self.dealer.cards[1]))
                self.updateRecords(state, 0)
            elif self.player.score > 21:
                state = (previousScore, self.dealer.cardState(self.dealer.cards[1]))
                self.updateRecords(state, -1)
            '''

        # Generate an episode according to Monte Carlo ES
        s = self.player.score
        a = random.choice(['h','s'])
        if a == 's':
            self.player.stick = True
        else:
            self.player.stick = False

        #state = (s, self.dealer.cardState(self.dealer.cards[1]), self.player.usableAce)


        while self.player.score <= 21 and not self.player.stick:
            previousScore = self.player.score
            card = random.choice(self.cards)
            #self.player.policyES(card, self.dealer)
            self.policyES(card)


        # Dealer's turn
        if self.player.score <= 21:
            self.hidden = False
            while self.dealer.score <= 21 and not self.dealer.stick:
                card = random.choice(self.cards)
                self.dealer.policy(card)
        self.status()
        #if len(self.player.states) == 1:
        #    state = (self.player.states[0], self.dealer.cardState(self.dealer.cards[1]), self.player.usableAce)
        #    #sa = (state, 's')
        #    #if state not in self.qvalues:
        #    self.updateQ(state, 's', self.finalReward)
        #else:

        if len(self.player.states) > 1:
            for s in self.player.states[:-1]:
                state = (s, self.dealer.cardState(self.dealer.cards[1]), self.player.usableAce)
                self.updateRecords(state, self.finalReward)
                self.updateQ(state, 'h', self.finalReward)
                self.updateN(state, 'h')

        s = self.player.states[-1]
        if s <= 21:
            state = (s, self.dealer.cardState(self.dealer.cards[1]), self.player.usableAce)
            self.updateRecords(state, self.finalReward)
            self.updateQ(state, 's', self.finalReward)
            self.updateN(state, 's')


        #for s in self.player.states:
        #    if s <= 21:
        #        state = (s, self.dealer.cardState(self.dealer.cards[1]), self.player.usableAce)
        #        self.updateRecords(state, self.finalReward)
        self.winLoss[self.finalReward] += 1


if __name__ == '__main__':
    # Start an instance of Blackjack
    bj = Blackjack()
    ngames = 2 # Number of games to play
    winLoss = {1:0,0:0,-1:0} # Win-loss records
    for i in range(ngames):
        print '\nGame ',i+1,':'
        bj.playGame()
        bj.getRecords()
        bj.getQvalues()
        bj.getFrequency()
        #winLoss
        bj.reset()
    bj.averageReturn()
    print bj.winLoss

