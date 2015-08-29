import sys
import random

from UserString import MutableString


class Command(object):
    '''Command Superclass'''

    def __init__(self, filename):

        # read the xml file and save it in message
        xmlfile = open(filename, 'r')
        self.message = xmlfile.read()
        xmlfile.close()

        # set requestor_id
        self.requestor_id = str(self.getRequestorId())
        self.setParameter('requestor_id', self.requestor_id)

    def setParameter(self, key, value):

        # set parameters to the xml command
        key = '$' + key
        self.message = self.message.replace(key, value)

    def getRequestorId(self):
        return str(random.randint(100, 10000))


class CommandAuth(Command):
    '''CommandAuth Class'''

    def __init__(self, access_level, user, password):

        filename = 'xml-commands/com_auth.xml'

        # init super constructor
        super(CommandAuth, self).__init__(filename)

        # set parameters
        self.setParameter('access_level', access_level)
        self.setParameter('user', user)
        self.setParameter('password', password)


class CommandKeepAlive(Command):
    '''CommandKeepAlive Class'''

    def __init__(self):

        filename = 'xml-commands/com_keep_alive.xml'

        # init super constructor
        super(CommandKeepAlive, self).__init__(filename)


class CommandSequenceManagement(Command):
    '''CommandPlaySequence Class'''

    def __init__(self, sequence_number, function_name):

        filename = 'xml-commands/com_seq_mng.xml'

        # init super constructor
        super(CommandSequenceManagement, self).__init__(filename)

        # set parameters
        self.setParameter('function_name', function_name)
        self.setParameter('sequence_number', sequence_number)


class CommandSubscribe(Command):
    '''CommandSubscribe Class'''

    def __init__(self, object_name, notification_type, notification_id):

        filename = 'xml-commands/com_subscribe.xml'

        # init super constructor
        super(CommandSubscribe, self).__init__(filename)

        # set parameters
        self.setParameter('object_name', object_name)
        self.setParameter('type', notification_type)
        self.setParameter('id', notification_id)


class CommandSay(Command):
    '''CommandSay Class'''

    def __init__(self, text, voice=None):

        filename = 'xml-commands/com_say.xml'

        # init super constructor
        super(CommandSay, self).__init__(filename)

        # get the say value in correct format
        say = self.getValue(text, voice)

        # set parameters
        self.setParameter('say', say)

        print "Say: '" + text + "'"

    def getValue(self, text, voice):

        if not voice:
            say = '<![CDATA[speech=' + text + ']]>'
        else:
            say = '<![CDATA[voice=' + voice + '\nspeech=' + text + ']]>'

        return say


class CommandPlay(Command):
    '''CommandPlay Class'''

    def __init__(self, audiofilename):

        filename = 'xml-commands/com_play.xml'

        # init super constructor
        super(CommandPlay, self).__init__(filename)

        # set parameters
        self.setParameter('play', audiofilename)


class CommandOutput(Command):
    '''CommandOutput Class'''

    def __init__(self, output_id, value):

        filename = 'xml-commands/com_output.xml'

        # init super constructor
        super(CommandOutput, self).__init__(filename)

        # set parameters
        self.setParameter('id', output_id)
        self.setParameter('value', str(value))


class CommandOutputRead(Command):
    '''CommandInput Class'''

    def __init__(self, output_id):

        filename = 'xml-commands/com_read_output.xml'

        # init super constructor
        super(CommandOutputRead, self).__init__(filename)

        # set parameters
        self.setParameter('id', output_id)


class CommandFunctionEnable(Command):
    '''CommandFunctionEnable Class'''

    def __init__(self, function, active):

        filename = 'xml-commands/com_function_enable.xml'

        # init super constructor
        super(CommandFunctionEnable, self).__init__(filename)

        # set the active param that ios_serve understands
        if active is True:
            active = 'true'
        else:
            active = 'false'

        # set parameters
        self.setParameter('name', function)
        self.setParameter('active', active)


class CommandFunctionSet(Command):
    '''CommandFunctionSet Class'''

    def __init__(self, function, vardict):

        filename = 'xml-commands/com_function_set.xml'

        # init super constructor
        super(CommandFunctionSet, self).__init__(filename)

        # get the dict into html tags: <key>value</key>
        parameters = self.parseParameters(vardict)

        # set parameters
        self.setParameter('name', function)
        self.setParameter('parameters', parameters)

    def parseParameters(self, vardict):

        # use MutableString for efficiency
        parameters = MutableString()

        # build a string with html tags: <key>value</key>
        for key, value in vardict.items():
            parameters += "\n            <%s>%s</%s>" % (key, value, key)

        return str(parameters)
