import sys
import re

from operator import itemgetter
from random import choice
from random import randint
from HTMLParser import HTMLParser  # html.parser in Python 3
from UserString import MutableString

# constants
VERSION = 1

# punch line defaults
punch_default_speed = 85
punch_default_shape = 100
punch_default_volume = 130


class Comedy:
    '''A Comedy Class'''

    def __init__(self, comedy):

        # check the version
        _version = comedy['version']
        self._check_version(_version)

        # parse main voice
        _main_voice = comedy['main_voice']
        self.tts_main_voice = _main_voice

        # parse comedy_jokes
        _jokes = comedy['jokes']
        self.comedy_jokes = self._parse_jokes(_jokes)

        # build comedy_joke_sequence
        _comedy_joke_sequence = comedy['comedy_joke_sequence']
        sequence = self._build_joke_sequence(_comedy_joke_sequence)
        self.comedy_joke_sequence = sequence

        # build the responses
        _responses = comedy['responses']
        self.responses = self.build_responses(_responses)

    def __iter__(self):
        '''Iteration support'''
        return self

    def _parse_jokes(self, jokes):

        _jokes = {}

        for item in jokes:

            # find key and item
            _joke = Joke(item['lines'])
            _id = item['id']

            # add them to the dictionary
            _jokes[_id] = _joke

        return _jokes

    def _check_version(self, version):

        if (VERSION != version):
            sys.exit('Input file version mismatch')

    def _get_unused_jokes(self, sequence):

        _unused_jokes = []

        for key in self.comedy_jokes.keys():

            if (key not in sequence):
                _unused_jokes.append(self.comedy_jokes[key])

        return _unused_jokes

    def _build_joke_sequence(self, comedy_joke_sequence):

        _joke_sequence = []

        # check if there are available parts for this sequence
        _comedy_parts_length = len(self.comedy_jokes)
        _comedy_joke_sequence_length = len(comedy_joke_sequence)

        if (_comedy_parts_length < _comedy_joke_sequence_length):
            sys.exit('Not enough comedies in the input file. (' +
                     str(_comedy_joke_sequence_length) +
                     ' required)')

        # get parts that is not directly referenced in the sequence
        _unused_jokes = self._get_unused_jokes(comedy_joke_sequence)

        # build the joke sequence
        for item in comedy_joke_sequence:

            if (item != '*'):

                # check if it exists
                if item in self.comedy_jokes:
                    comedy = self.comedy_jokes[item]
                else:
                    print "WARNING: Joke '" + str(item) + "' doesn't exist"

            else:
                # that's a random joke
                comedy = choice(_unused_jokes)
                _unused_jokes.remove(comedy)

            _joke_sequence.append(comedy)

        return _joke_sequence

    def build_responses(self, responses):

        _responces = Responces()

        # positive
        positive = responses['positive']

        for response in positive:

            # get items
            trigger = response['trigger']
            item = Line(response['response'])

            _responces.addResponse('positive', trigger, item)

        # negative
        negative = responses['negative']

        for response in negative:

            # get items
            trigger = response['trigger']
            item = Line(response['response'])

            _responces.addResponse('negative', trigger, item)

        # return the object
        return _responces

    def say(self):

        # play the intro
        self.comedy_intro.say()

        # play the sequence
        for item in self.comedy_joke_sequence:
            item.say()

        # play the outro
        self.comedy_outro.say()

    def getText(self):

        # use MutableString for efficiency
        comedy_text = MutableString()

        # intro
        comedy_text += self.comedy_intro.getText()

        # sequence
        for item in self.comedy_joke_sequence:
            comedy_text += item.getText()

        # outro
        comedy_text += self.comedy_outro.getText()

        return str(comedy_text)

    def length(self):

        length = self.comedy_intro.length()

        for item in self.comedy_joke_sequence:
            length = length + item.length()

        length = length + self.comedy_outro.length()

        return length

    def nextJoke(self):
        '''Get the next joke with the use of generators'''

        for joke in self.comedy_joke_sequence:
            yield joke


class Joke:
    '''A Joke Class'''

    def __init__(self, lines):

        # parse the lines of that joke
        self.lines = self._parse_lines(lines)

    def _parse_lines(self, lines):

        _lines = []

        # iterate
        for line in lines:

            _line = Line(line)

            # add it to the list
            _lines.append(_line)

        return _lines

    def say(self):

        for line in self.lines:
            line.say()

    def getText(self):

        # use MutableString for efficiency
        comedy_text = MutableString()

        for line in self.lines:
            comedy_text += line.getText() + ' '

        return str(comedy_text)

    def nextLine(self):
        '''Get the next line with the use of generators'''

        for line in self.lines:
            yield line


class Line:
    '''A Line Class'''

    # use the NLTK library and load the english language tokenizer
    import nltk.data
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    def __init__(self, line):

        # break it into sentences
        self.sentences = self._parseLine(line)

    def nextSentence(self):
        '''Get the next sentence with the use of generators'''

        for sentence in self.sentences:
            yield sentence

    def _parseLine(self, line):
        ''' Get a list of sentences from the line'''

        # init a list
        sentences_list = []

        # get a list of the sentences as strings
        sentences = self.tokenizer.tokenize(line)

        # iterate
        for sentence in sentences:

            # create the Sentence object
            sentence_object = Sentence(sentence)

            # add it to the list
            sentences_list.append(sentence_object)

        return sentences_list


class Sentence:
    ''' A Sentence Class '''

    def __init__(self, sentence):

        self.tokens = self._parseSentence(sentence)

    def _parseSentence(self, sentence):
        '''break html style tags
           e.g. <voice>foo</voice>
                <break />
                <voice attribute='true'> </voice> '''

        # Debug:
        #print "Sentence: " + sentence

        # init the TagTokeniser (an HTMLParser)
        tagTokeniser = TagTokeniser()
        tagTokeniser.feed(sentence)

        # get the tokens
        _tokens = tagTokeniser.tokens()

        return _tokens

    def say(self):

        for token in self.tokens:
            token.say()

    def getText(self):

        # use MutableString for efficiency
        comedy_text = MutableString()

        for token in self.tokens:
            comedy_text += token.getText()

        return str(comedy_text)

    def length(self):

        length = 0

        for token in self.tokens:
            length = length + token.length()

        return length

    def nextToken(self):
        '''Get the next token with the use of generators'''

        # iterate
        for token in self.getCombinedTokens():
            yield token

    def getCombinedTokens(self):

        # init list
        combinedTokens = []

        text = CombinedText()

        # iterate
        for token in self.tokens:

            if isinstance(token, Text) or isinstance(token, Pause):

                # add the text of it
                text.add(token.getText())

            else:

                # if the text is not empty
                if len(text.getText()) > 0:

                    # add it to the list
                    combinedTokens.append(text)

                    # reset it
                    text = CombinedText()

                # add the other token to the list
                combinedTokens.append(token)

        # don't forget to add the remaining text to the list
        if len(text.getText()) > 0:

            # add it to the list
            combinedTokens.append(text)

        return combinedTokens


class CombinedText:
    '''A Combined Text Class'''

    def __init__(self):

        # save the linetype
        self.tokentype = "CombinedText"

        # use MutableString for efficiency
        self._text = MutableString()

    def add(self, text):
        self._text += text

    def getText(self):
        return str(self._text)


class Text:
    '''A Text Class'''

    def __init__(self,
                 text,
                 punch=False,
                 speed=None,
                 shape=None,
                 volume=None,
                 voice=None):

        self.text = text
        self.punch = punch
        self.speed = speed
        self.shape = shape
        self.volume = volume
        self.voice = voice

        self.tokentype = "Text"

    def say(self):
        print "> " + self.text

    def getText(self):

        # use MutableString for efficiency
        comedy_text = MutableString()

        # check if the reset tag is needed
        tagAdded = False

        # get the values
        speed = self.speed
        shape = self.shape
        volume = self.volume
        voice = self.voice

        # if it is a punch line
        # set the punch line defauls but not override
        if self.punch:

            if speed is None:
                speed = punch_default_speed

            if shape is None:
                shape = punch_default_shape

            if volume is None:
                volume = punch_default_volume

        # check for voice tags (if not None or default)
        if speed and speed != 100:
            comedy_text += '\\rspd=' + str(speed) + '\\'
            tagAdded = True

        if shape and shape != 100:
            comedy_text += '\\vct=' + str(shape) + '\\'
            tagAdded = True

        if volume and volume != 100:
            comedy_text += '\\vol=' + str(volume) + '\\'
            tagAdded = True

        if voice:
            comedy_text += '\\vce=speaker=' + voice + '\\'
            tagAdded = True

        # add the text
        comedy_text += self.text

        # add the reset at the end
        if tagAdded:
            comedy_text += '\\rst\\'

        return str(comedy_text)

    def length(self):
        return len(re.findall(r'\w+', self.text))


class Audio:
    '''An Play Object'''

    def __init__(self, filename, length):

        # save the filename and length
        self.filename = filename
        self.length = length

        self.tokentype = "Audio"

    def say(self):
        return self.getText()

    def getText(self):
        # Just for debug reasons.
        # This should never reach the communication module
        return "<audio file='%s' length='%s'/>" % (self.filename, self.length)


class Command:
    '''A Command Object'''

    def __init__(self, commandType, value, refsave=None):

        # save the command type and value
        self.commandType = commandType
        self.value = value
        self.refsave = refsave

        self.tokentype = "Command"

    def say(self):
        return self.getText()

    def getText(self):
        # Just for debug reasons.
        # This should never reach the communication module
        return "<command %s='%s' />" % (self.commandType, self.value)


class Pause:
    '''A Pause Object'''

    def __init__(self, time=1000):

        # save the time
        self.time = time

        self.tokentype = "Pause"

    def say(self):
        print '<pause:' + str(self.time) + '>'

    def getText(self):
        return '\\pau=' + str(self.time) + '\\'


class Response:
    '''A Response Object'''

    def __init__(self, trigger):

        #save the type
        self.trigger = trigger

        self.tokentype = "Response"


class TagTokeniser(HTMLParser):
    '''A SentenceTokeniser that parses HTML tags'''

    def __init__(self):

        # init HTMLParser
        HTMLParser.__init__(self)

        # init tokens list
        self._tokens = []

        # init params stack (LIFO)
        self._params = []

    ''' HTMLParser handlers '''

    def handle_starttag(self, tag, attrs):

        # handle tags
        if (tag == 'say'):
            # will be handled in handle_data method
            pass

        elif (tag == 'audio'):
            self.handle_audio(attrs)

        elif (tag == 'command'):
            self.handle_command(attrs)

        elif (tag == 'pause'):
            self.handle_pause(attrs)

        elif (tag == 'response'):
            self.handle_response(attrs)

        else:
            print "WARNING: Unknown tag '" + tag + "'"

        # push to the params stack
        self._params.append(attrs)

    def handle_data(self, data):

        if (self._params):  # if not empty
            # handle say with last object as attrs
            attrs = self._params[-1]

        else:
            # when we have text without say tag
            attrs = []

        self.handle_say(data, attrs)

    def handle_endtag(self, tag):

        # pop from the params stack
        if self._params:
            self._params.pop()
        else:
            print "WARNING: Wrong handling of tag: " + tag

    ''' Custom handlers '''

    def handle_say(self, text, params):

        # init the say params to None
        speed = None
        shape = None
        volume = None
        voice = None
        punch = False

        # check if params are available
        for item in params:
            if (item[0] == 'speed'):
                speed = int(item[1])
            elif (item[0] == 'shape'):
                shape = int(item[1])
            elif (item[0] == 'volume'):
                volume = int(item[1])
            elif (item[0] == 'voice'):
                voice = str(item[1])
            elif (item[0] == 'punch'):
                punch = bool(item[1])
            else:
                print "WARNING: Unsupported parameter in <say />:" + item[0]

        textObject = Text(text, punch, speed, shape, volume, voice)
        self._tokens.append(textObject)

    def handle_audio(self, params):

        # init the params to None
        filename = None
        length = None

        # check if params are available
        for item in params:

            # play
            if (item[0] == 'filename'):
                filename = item[1]
            elif (item[0] == 'length'):
                length = float(item[1])
            else:
                param = item[0]
                print "WARNING: Unsupported param in <command />: %s" % (param)

        if filename is None:
            print "WARNINNG: filename parameter should exist in <audio />"

        if length is None:
            print "WARNINNG: length parameter should exist in <audio />"

        audioObject = Audio(filename, length)
        self._tokens.append(audioObject)

    def handle_command(self, params):

        # init the params to None
        commandType = None
        value = None
        refsave = None

        # check if params are available
        for item in params:

            # type: sequence
            if (item[0] in ['sequenceplay', 'sequencestop']):

                commandType = item[0]
                value = item[1]

            # type: look
            elif (item[0] == 'look'):

                commandType = 'look'
                value = item[1]

            # type: point
            elif (item[0] == 'point'):

                commandType = 'point'
                value = item[1]

            # in case there is a refsave
            elif (item[0] == 'refsave'):
                refsave = item[1]

            else:
                print "WARNING: Unsupported param in <command />:" + item[0]

        commandObject = Command(commandType, value, refsave)
        self._tokens.append(commandObject)

    def handle_pause(self, params):

        # default pause time is 1000
        time = 1000

        # check if params are available
        for item in params:
            if (item[0] == 'time'):
                time = int(item[1])
            else:
                print "WARNING: Unsupported parameter in <pause />:" + item[0]

        pauseObject = Pause(time)
        self._tokens.append(pauseObject)

    def handle_response(self, params):

        # default is laughter
        trigger = "laughter"

        # check if params are available
        for item in params:
            if (item[0] == "trigger"):
                if item[1] not in ["laughter", "applauding"]:
                    print "WARNING: Unsupported trigger:" + item[1]
                else:
                    trigger = item[1]
            else:
                print "WARNING: Unsupported param in <response />:" + item[0]

        responseObject = Response(trigger)
        self._tokens.append(responseObject)

    ''' other methods '''

    def tokens(self):

        if (self._params):  # if not empty
            count = len(self._params)
            print "WARNING: %d starttag(s) exists without an endtag" % (count)

        return self._tokens

    def reset(self):

        # call superclass reset
        HTMLParser.reset(self)

        # reset the parser
        self._tokens = []
        self._params = []


class Responces:

    def __init__(self):

        # init the responce list
        self._positive = []
        self._negative = []

    def addResponse(self, responsetype, trigger, response):

        # create the response
        response = {"trigger": trigger,
                    "response": response}

        if responsetype == "positive":

            self._positive.append(response)

        elif responsetype == "negative":

            self._negative.append(response)

        else:
            print "WARNING: Unknown response type: " + responsetype

    def getResponse(self, responsetype, trigger):

        # should I get a responce?
        p = 100  # Yes, with a probability of p%

        if randint(1, 100) <= p:
            respond = True
        else:
            respond = False

        # init responce with None
        response = None

        # if we will respond
        if respond:

            if responsetype == "positive":
                responcelist = self._positive

            elif responsetype == "negative":
                responcelist = self._negative

            else:
                responcelist = None
                print "WARNING: Unknown response type: " + responsetype

            # if list is not empty
            if responcelist:

                # get a list with all responses with same trigger
                triggerList = filter(lambda x: x["trigger"] == trigger,
                                     responcelist)

                if triggerList:
                    response = choice(triggerList)

                    # remove it so we don't have duplicate responses
                    responcelist.remove(response)

                else:
                    print "WARNING: List '" + trigger + "' is empty."

            else:
                print "WARNING: List '" + responsetype + "' is empty."

        # return the response (even if it is None)
        return response


''' main '''
if __name__ == '__main__':

    # check if the the filename exists as a parameter
    if (len(sys.argv) < 2):
        sys.exit('Missing input file')

    # read the filename from the 1st argument
    filename = sys.argv[1]

    # open the file
    source = open(filename, 'r')

    # print loading message
    print "Loading Comedy Parser..."

    # import json library
    import json

    # parse the json file
    comedy = json.load(source)

    # close the file
    source.close()

    # print some empty lines (separate from previous commands)
    for i in range(0, 50):
        print " "

    # clear screen
    import os
    os.system('clear')

    # parse comedy
    comedy = Comedy(comedy)

    # iterate (just for testing)
    for joke in comedy.nextJoke():
        for line in joke.nextLine():
            for sentence in line.nextSentence():
                for token in sentence.nextToken():
                    print token.getText()
