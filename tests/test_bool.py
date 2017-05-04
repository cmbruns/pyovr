#!/bin/env python

import unittest
import ctypes

import ovr


class TestProperties(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bool(self):
        # Create various values for testing
        # A) Built in python booleans
        bt1 = True
        bf1 = False
        # B) OVR wrapped booleans
        bt2 = ctypes.c_char(bytes([1]))
        bf2 = ctypes.c_char(bytes([0]))
        # C) chr's, which might accidently get used sometimes
        # This is the most dangerous situation, because bool(chr(0)) == False
        bt3 = chr(1)
        bf3 = chr(0) # DANGER!
        # D) ovr macros
        bt4 = ovr.ovrTrue
        bf4 = ovr.ovrFalse
        # Make sure we understand who is true and false in boolean context
        self.assertTrue(bool(bt1))
        self.assertTrue(bool(bt2))
        self.assertTrue(bool(bt3))
        self.assertTrue(bool(bt4))
        self.assertFalse(bool(bf1))
        self.assertFalse(bool(bf2))
        self.assertTrue(bool(bf3)) # Danger!
        self.assertFalse(bool(bf4))

    def test_convert(self):
        # Test my helper conversion function
        self.assertTrue(ovr.toOvrBool(True))
        self.assertTrue(ovr.toOvrBool(chr(1)))
        self.assertTrue(ovr.toOvrBool(ctypes.c_char(bytes([1]))))
        self.assertFalse(ovr.toOvrBool(False))
        self.assertFalse(ovr.toOvrBool(chr(0))) # Tricky one!
        self.assertFalse(ovr.toOvrBool(ctypes.c_char(bytes([0]))))


if __name__ == '__main__':
    unittest.main()

