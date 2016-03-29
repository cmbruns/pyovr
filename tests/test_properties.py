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
        eye_height = ovr.getFloat(self.hmd, ovr.KEY_EYE_HEIGHT, ovr.DEFAULT_EYE_HEIGHT)
        print "eye height = ", eye_height
        self.assertNotEqual(eye_height, 0)
        # TODO: Test setFloat(...)
        # It seems ovr.KEY_IPD is read-only, according to https://forums.oculus.com/viewtopic.php?t=20369


if __name__ == '__main__':
    unittest.main()
    ovr.shutdown()        

