#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
import importlib
import re
import sys
import time

import tools
import sunfish

import chess as pychess

from tools import WHITE, BLACK
from xboard import Unbuffered, sunfish
sys.stdout = Unbuffered(sys.stdout)

lf = "sunfish-log.txt"	##############################################
log = open(lf, 'w')

def print2(x):
    print(x)
    log.write("< %s\n" % x)
    log.flush()

def main():
    pos = tools.parseFEN(tools.FEN_INITIAL)
    searcher = sunfish.Searcher()
    forced = False
    color = WHITE
    our_time, opp_time = 1000, 1000 # time in centi-seconds
    show_thinking = True

    # print name of chess engine
    #print('Sunfish')

    stack = []
    while True:
        if stack:
            smove = stack.pop()
        else: smove = input()
        log.write("> %s\n" % smove)
        log.flush()

        if smove == 'quit':
            break

        elif smove == 'uci':
            print2("id name Sunfish")
            print2('uciok')

        elif smove == 'isready':
            print2('readyok')

        elif smove == 'ucinewgame':
            stack.append('position fen ' + tools.FEN_INITIAL)

        elif smove.startswith('position'):
            params = smove.split(' ')
            if params[1] == 'fen' and 'moves' not in smove:
                pos = pychess.Board(' '.join(params[2:8]))
                fen = pos.fen()
                pos = tools.parseFEN(fen)
                color = WHITE if fen.split()[1] == 'w' else BLACK
            if params[1] == 'fen' and 'moves' in smove:
                pos = pychess.Board(' '.join(params[2:8]))
                if len(params) > 9:
                    for mo in params[9:]:
                        pos.push_uci(mo)
                fen = pos.fen()
                pos = tools.parseFEN(fen)
                color = WHITE if fen.split()[1] == 'w' else BLACK
            if params[1] == 'startpos':
                pos = pychess.Board()
                if len(params) > 3:
                    for mo in params[3:]:
                        pos.push_uci(mo)
                fen = pos.fen()
                pos = tools.parseFEN(fen)
                color = WHITE if fen.split()[1] == 'w' else BLACK

        elif smove.startswith('go'):
            #  default options
            depth = 1000
            movetime = 3000	# default move time 3 seconds

            # parse parameters
            params = smove.split(' ')
           # if len(params) == 1: continue

            i = 0
            while i < len(params):
                param = params[i]
                if param == 'depth':
                    i += 1
                    depth = int(params[i])
                if param == 'movetime':
                    i += 1
                    movetime = int(params[i])
                i += 1

            forced = False

            moves_remain = 40

            start = time.time()
            ponder = None
            for _ in searcher._search(pos):
                moves = tools.pv(searcher, pos, include_scores=False)

                if show_thinking:
                    entry = searcher.tp_score.get((pos, searcher.depth, True))
                    score = int(round((entry.lower + entry.upper)/2))
                    usedtime = int((time.time() - start) * 1000)
                    moves_str = moves if len(moves) < 15 else ''
                    print2('info depth {} score cp {} time {} nodes {} pv {}'.format(searcher.depth, score, usedtime, searcher.nodes, moves_str))

                if len(moves) > 5:
                    ponder = moves[1]

                if movetime > 0 and (time.time() - start) * 1000 > movetime:
                    break

                if searcher.depth >= depth:
                    break

            entry = searcher.tp_score.get((pos, searcher.depth, True))
            m, s = searcher.tp_move.get(pos), entry.lower
            # never resign, Cute Chess does not recognize it anyway
            if False:	#  s == -sunfish.MATE_UPPER:
                print2('resign')
            else:
                moves = moves.split(' ')
                if len(moves) > 1:
                    print2('bestmove ' + moves[0] + ' ponder ' + moves[1])
                else:
                    print2('bestmove ' + moves[0])

        elif smove.startswith('time'):
            our_time = int(smove.split()[1])

        elif smove.startswith('otim'):
            opp_time = int(smove.split()[1])

        else:
            pass

if __name__ == '__main__':
    main()
