"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.core.files import File as DjangoFile
from archiwum.models import Document, Dean, DocumentVersion

#class Document_get_current_fileTestCase(TestCase):
    #def setUp(self):
        
        #self.document = Document.objects.create(
            #title='TestDocument', public=True, 
            #issued_on = datetime.datetime.now(), author=)
        ##self.documentVersion = DocumentVersion.objects.create(
            ##download_counter=0, document=self.document,
            ##file=DjangoFile(
    #def tearDown(self):
        #self.document.delete()
    #def test_no_file(self):
        #self.assertEqual([], self.document.current_file)
        
class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}
