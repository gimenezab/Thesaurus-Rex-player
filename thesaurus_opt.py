"""
Module that plays Thesaurus Rex (http://thesaurus-rex.org).
Should have Linux's dictionary together with it in file named 'brazilian'
Receives sequence of letters that defines the board.
Prints list of words found.
"""


def import_dict (lang, word_length):
    """
    Import dictionary of words, excluding those started with uppercase and the character '
    """

    #libraries
    from unicodedata import normalize

    #create empty dictionary
    words = []

    #import line by line removing special characters
    with open(lang) as inputfile:
        for line in inputfile:
            words.append(''.join(e for e in line if e.isalnum()))

    #remove acentos, single letters and capitalized (names)
    words = [normalize('NFKD', word).encode('ASCII', 'ignore').decode() for word in words if len(word)>word_length and word[0].islower()]

    #remove duplicates
    words = list(set(words))

    #sort
    words.sort()

    return words



def create_board (letters):
    """
    Creates a 5x5 board with the letters given surrounded by empty spaces
    """

    #libraries
    import numpy as np 

    #create board
    board = np.empty((7,7), dtype=str)

    #fill it up with the given letters
    for i, letter in enumerate(letters):
        board[i//5 +1][i%5 +1] = letter.lower()

    return board



def create_valid (positions=None, directions=None):
    """
    Creates a map of valid positions. Default is 5x5 board of True surrounded by False. Given positions OR path, will tag those as False
    """

    #create base
    valid = [[ False,  False,  False,  False,  False,  False,  False],
             [ False,  True,  True,  True,  True,  True,  False],
             [ False,  True,  True,  True,  True,  True,  False],
             [ False,  True,  True,  True,  True,  True,  False],
             [ False,  True,  True,  True,  True,  True,  False],
             [ False,  True,  True,  True,  True,  True,  False],
             [ False,  False,  False,  False,  False,  False,  False]]
    
    #walk the line (False where walked by directions)
    if directions is not None:
        pos = [0,0]
        for direction in directions:
            pos[0] += direction[0]
            pos[1] += direction[1]
            if not valid[pos[0]][pos[1]]:
                return None
            valid[pos[0]][pos[1]] = False
    
    #stand your ground (False on given positions)
    if positions is not None:
        for pos in positions:
            valid[pos[0]][pos[1]] = False

    return valid



def step (start, valid):
    """
    Will take the next allowed step, respecting valid.
    If no step is allowed, returns None.
    Returns the end position
    """

    #start variables
    direction = [0,0]
    end = [0,0]

    while True:
        #create new direction and find new end place
        direction[0] += direction[1]//3
        direction[1] = direction[1]%3
        end[0] = start[0]+direction[0]-1
        end[1] = start[1]+direction[1]-1
        #after full loop over all directions, return None
        if direction[0] > 2:
            yield None
        #if end is a valid place, return this end
        if valid[end[0]][end[1]]:
            yield end
        #if not valid, set search for new direction
        direction[1] += 1



def johnnywalker (start, valid, word, board, words, used):
    """
    Explores all possible valid paths after start given valid.
    Prints words found.
    Returns dictionary of unused words.
    """
    
    #libraries
    from copy import deepcopy

    #create a generator of valid steps
    stepper = step(start, valid)

    #take first valid step
    next_step = next(stepper)

    #as long as there are valid steps to be taken
    while next_step is not None:

        #create valid and word for new step
        new_valid = deepcopy(valid)
        new_valid[next_step[0]][next_step[1]] = False
        new_word = word + board[next_step[0]][next_step[1]]
        
        #check if new word is in words
        new_words, used = find_in_dict(new_word, words, used)

        #if there are words down the line, keep exploring
        if len(new_words) > 0:
            #walk the line down after this step)
            used = johnnywalker(next_step, new_valid, new_word, board, new_words, used)

        #take next valid step
        next_step = next(stepper)

    #return updated words, without used words
    return used



def find_in_dict (word, words, used):
    """
    If word in words prints word and removes it from words
    Returns number of candidates in words that start with word and updated words
    """

    #filter from dictionary only words of interest
    new_words = list(filter(lambda x: x.startswith(word), words))

    #check the word itself and remove from dictionary and add it to used if found
    if word in new_words and word not in used:
        print(word)
        used.append(word)
    
    return new_words, used



def walk_the_lines (board, words):
    '''
    For each possible start position starts the exploration processes (calls johnnywalker)
    '''

    #list of used words
    used = []

    #for each position on the board
    for i in range(1,6):
        for j in range(1,6):
            #set position as starting position
            start = (i,j)
            #create a valid map
            valid = create_valid([start])
            #start word with letter of starting position
            word = board[start[0]][start[1]]
            #explore down the line from this start position
            johnnywalker(start, valid, word, board, words, used)
    
    return used



def start ():
    '''
    Prepares game and starts it
    '''

    #import dictionary of words
    lang = ''
    word_length = 1
    while True:
        lang = input('Select language (en|br): ')
        if len(lang) is 2:
            if 'en' in lang or 'br' in lang:
                break
    while True:
        word_length = input('Choose minimum word length (int > 1): ')
        word_length = int(word_length)
        if word_length > 1:
            word_length -= 1
            break
    words = import_dict(lang, word_length)

    #build board
    letters = ''
    while True:
        letters = input('Enter the letters: ')
        if len(letters) is 25 and type(letters) is str:
            break
    board = create_board(letters)

    #remove words with unwanted letters
    clean_words = []
    for w in range(len(words)):
        contained = True
        for l in range(len(words[w])):
            if words[w][l] not in letters.lower():
                contained = False
                break
        if contained:
            clean_words.append(words[w])

    #start exploring
    used = walk_the_lines(board, words)
    
    #show the results
    results(used)


    
def results (used):

    #libraries
    from collections import Counter

    #print info
    print('Number of words found:')
    print(len(used))

    #convert words to length of words
    used = [len(word) for word in used]

    #create dictionary with the frequency of word lengths
    ctr = Counter(used)

    #print info
    print('Words length frequency:')
    print(ctr)
    for i in range(min(ctr.keys()),1+max(ctr.keys())):
        print(i, ctr[i])

    #create a long enough vector of points per length
    simple_fibo = [0,1]
    for i in range(26):
        simple_fibo.append(simple_fibo[-2]+simple_fibo[-1])
    
    #points per words length frequency
    for key, count in ctr.items():
        ctr[key] = simple_fibo[key-1] * count
    
    #print info
    print('Points per word length:')
    for i in range(min(ctr.keys()),1+max(ctr.keys())):
        print(i, ctr[i])

    #calculate points
    total = 0
    for points in ctr.values():
        total += points

    #print info
    print('Total points found:')
    print(total)

    
    
if __name__ == "__main__":

    start()
