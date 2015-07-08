#encoding=utf-8
#+-------------------------------------------------------+
# wspy.error
# Copyright (c) 2015 OshynSong<dualyangsong@gmail.com>
#
# Define the specific exception and error for the package
# to be encountered.
#+-------------------------------------------------------+
'''
wspy.error
This module contains the collection of wspy error
'''

class WSError(Exception):
    '''Root for wspy package exceptions'''
    pass

class WSTypeError(TypeError):
    '''Different type error for WS'''
    pass

class NetworkError(WSError, IOError):
    '''Socket network error occured'''
    pass
    
class UnmaskError(WSError):
    '''Unmask the frame data occured error'''
    pass

