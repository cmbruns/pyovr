#!/bin/env python

import unittest
import ovr

class TestProperties(unittest.TestCase):

    def setUp(self):
        ovr.initialize(None)
        self.hmd, luid = ovr.create()

    def tearDown(self):
        ovr.destroy(self.hmd)

    def test_getFloat(self):
        refresh = ovr.getFloat(self.hmd, "VsyncToNextVsync", 0.0)
        self.assertNotEqual(refresh, 0)
        ipd = ovr.getFloat(self.hmd, ovr.KEY_IPD, ovr.DEFAULT_IPD)
        self.assertNotEqual(refresh, 0)
        # TODO: Test setFloat(...)


if __name__ == '__main__':
    unittest.main()
    ovr.shutdown()        
