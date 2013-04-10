#!/usr/bin/env python2

import unittest
import os
import imp

yturl = imp.load_source("yturl", os.path.join(os.path.dirname(__file__), "../yturl"))
y = yturl.YTURL("medium", "KxaCOHT0pmI")

class DatabaseUnitTests(unittest.TestCase):
    def testCorrectItagOrder(self):
        itagOrder = y.getDefaultItagQualityOrder()
        self.assertTrue(itagOrder.index("5") > itagOrder.index("46"))
        self.assertTrue(itagOrder.index("13") > itagOrder.index("17"))

    def testURLStripping(self):
        self.assertTrue(y.stripToVideoID("http://www.youtube.com/watch?feature=player_embedded&v=gEl6TXrkZnk") == "gEl6TXrkZnk")
        self.assertTrue(y.stripToVideoID("youtu.be/gEl6TXrkZnk#foo") == "gEl6TXrkZnk")
        self.assertTrue(y.stripToVideoID("youtu.be/gEl6TXrkZnkfoo") == "gEl6TXrkZnk")

    def testDesiredItagOrder(self):
        self.assertTrue(y.getDesiredItagOrder("18") == ('18', '43', '34', '35', '6', '44', '5', '45', '36', '22', '17', '46', '13', '37', '38'))


if __name__ == "__main__":
    unittest.main()
