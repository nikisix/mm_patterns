# Authors: Tom De Smedt, Frederik Vaassen, Vincent Van Asch
# CLiPS Computational Linguistics & Psycholinguistics Research Group
# University of Antwerp, 2010

# You need the Pattern module to run the experiment: http://www.clips.ua.ac.be/pages/pattern
# You need NodeBox for OpenGL to run the visualizer: http://cityinabottle.org/nodebox
# You need SentiWordNet for the opinion mining: http://sentiwordnet.isti.cnr.it/
# Instructions on how to install SWN in Pattern can be found in the docs (pattern.en > WordNet).

import os, sys; #sys.path.append("/users/tom/desktop/nodebox/creatures/nodebox-opengl") # path to NOGL module.

# This script uses NodeBox for OpenGL to visualize the data gathered with tweets.py.
from nodebox.graphics import *

import os, glob

# --------------------------------------------------------------------------------------------------
# Read in the harvested data, group tweets by politician name.
# Filter out tweets not in Dutch or French (these are probably not from a Belgian citizen).
tweets = {}
for f in glob.glob("harvest*.txt"):
    s = open(f).read().strip()
    s = [x.split("\t") for x in s.split("\n")]
    s = [[a.decode("utf-8") for a in x] for x in s]
    s = [x for x in s if len(x) == 10]
    for id, query, name, party, district, language, txt1, txt2, score, date in s:
        if not query in tweets:
            tweets[query] = []
        if query in txt1.lower() and language in ("nl", "fr"):
            tweets[query].append(
                (id, query, name, party, district, language, txt1, txt2, score, date))

# --------------------------------------------------------------------------------------------------
# Sort by number of tweets, highest-first.
# Filter out names that also belong to famous people 
# (we get lots of tweets for those, but unrelated to the actual politician).
# Each item in the top list is a (count, name, party, tweets)-tuple,
# where tweets is a list of (language, tweet)-items.
false_positives = ('mohamed ali', 'toon hermans', 'guy adams', 'bob peeters')
top = []
top = [(len(tweets[q]), q) for q in tweets if len(tweets[q]) > 0]
top = [(count, q) for count, q in top if q not in false_positives]
top = [(count, q, tweets[q][0][3], [(t[5], t[7], float(t[8])) for t in tweets[q]]) for count, q in top]
top.sort(reverse=True)
top = top[:25] # top 25 most mentioned politicians

# --------------------------------------------------------------------------------------------------
# The name of each party linked to a NodeBox Color object.
# Colors are defined in R,G,B,A values between 0.0-1.0.
party_colors = {
    "N-VA": color(1.00, 0.75, 0.00),
    "MR": color(0.02, 0.31, 0.64),
    "FN": color(0.44, 0.65, 0.93),
    "OPEN VLD": color(0.13, 0.33, 0.64),
    "OPEN VLD KANDIDATEN:": color(0.13, 0.33, 0.64),
    "CD&V": color(0.90, 0.37, 0.01),
    "CDH": color(0.71, 0.26, 0.19),
    "CDH ET CSP CDH": color(0.71, 0.26, 0.19),
    "SP.A": color(1.00, 0.00, 0.00),
    "ECOLO": color(0.32, 0.57, 0.07),
    "PARTI SOCIALISTE": color(1.00, 0.00, 0.00),
    "PVDA+": color(0.90, 0.19, 0.17),
    "PTB+": color(0.90, 0.20, 0.18),
    "VLAAMS BELANG": color(1.00, 0.90, 0.00),
    "LIJST DEDECKER": color(0.92, 0.50, 0.20),
    "PS": color(1.00, 0.00, 0.00),
    "FRONT-DES-GAUCHES": color(0.71, 0.07, 0.08),
    "GROEN!": color(0.60, 0.75, 0.05),
    "GROEN !": color(0.60, 0.75, 0.05),
    "PARTI POPULAIRE": color(0.52, 0.16, 0.45),
    "W+": color(0.94, 0.23, 0.20),
    "R.W.F.": color(0.78, 0.08, 0.11),
    "WALLONIE D'ABORD": color(0.94, 0.23, 0.20),
    "MS PLUS": color(0.87, 0.04, 0.09),
    "PROBRUXSEL": color(0.0, 0.50, 0.50),
}

# --------------------------------------------------------------------------------------------------
# NodeBox drawing code.
# fill(r,g,b,a) sets the current fill color,
# strokewidth() sets the current outline width for lines and shapes,
# rect(x, y, width, height) draws a rectangle at position x, y, etc.

WIDTH = 750
HEIGHT = 750
TEXTWIDTH = 250

def draw(canvas):
    if canvas.frame > 1: 
        return

    background(0.15)
    text("Top 25 of Belgian politicians being mentioned on Twitter", 100, HEIGHT-30, fill=(1,1,1,1), fontsize=16)
    text("Darker  =  negative or derogatory tweets".upper(), 100, HEIGHT-50, fill=(0.7,0.7,0.7,1), fontsize=10)

    translate(0,90)
    for i, (count, query, party, tweets) in enumerate(top):
        # The frequency of Dutch tweets vs. French tweets, 0.0-1.0:
        nl_fr = sum([1 for language, txt, score in tweets if language=="nl"]) / float(count)
        # Negative sentiment score total:
        neg = abs(sum([1 for language, txt, score in tweets if score < 0]))
        # w1: the width of the bar of positive tweets
        # w2: the width of the bar of negative tweets
        w1 = 20 + 1.2 * (count-neg)
        w2 = 20 + 1.2 * neg
        # Current horizontal and vertical position:
        x = TEXTWIDTH + 30
        y = HEIGHT - 200 - 25*i
        # Use the politician's party colors to draw the bars.
        # The negative bar is slightly darker to mark the difference.
        clr = party_colors[party.upper()]
        fill(clr)
        stroke(0, 0.8)
        strokewidth(0.1)
        rect(x, y, w1, 20)
        fill(clr.r*0.7, clr.g*0.7, clr.b*0.7)
        rect(x+w1+(w1 > 0 and 2 or 0), y, w2, 20)
        # Draw a separator on the positive bar to represent the amount of Dutch vs. French tweets.
        if nl_fr < 1:
            stroke(0, 1.0)
            strokewidth(0.5)
            line(x+nl_fr*w1, y, x+nl_fr*w1, y+20)
        # Add some extra information near the separator in the topmost bar.
        fill(0, 0.8)
        fontsize(8)
        if i == 0:
            text(u" NL <", x+nl_fr*w1-27, y+5)
            text(u"> FR", x+nl_fr*w1+4, y+5)
        # Draw numbers info: the amount of positive / negative tweets.
        fill(0)
        fontsize(10)
        text(str(int(count-neg))+"+", x+3, y+5)
        text(str(int(neg))+u"-", x+5+w1+2, y+5)
        # Draw politician name + party.
        fill(1)
        text(query.upper()+" (%s)"%party, 20, y+5, width=TEXTWIDTH, align=RIGHT)

canvas.size = WIDTH, HEIGHT
canvas.run(draw)
