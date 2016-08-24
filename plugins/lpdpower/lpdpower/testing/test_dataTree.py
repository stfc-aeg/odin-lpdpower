""" Test DataTree class from lpdpower.

Tim Nicholls, STFC Application Engingeering
"""

from nose.tools import *
from lpdpower.DataTree import DataTree


class TestDataTree():

    """Test the DataTree class.
    """

    @classmethod
    def setup_class(cls):

        cls.int_value = 1234
        cls.float_value = 3.1415
        cls.bool_value = True
        cls.str_value = 'theString'

        cls.simple_dict = {
            'intParam': cls.int_value,
            'floatParam': cls.float_value,
            'boolParam': cls.bool_value,
            'strParam':  cls.str_value,
        }

        cls.simple_tree = DataTree(cls.simple_dict)

        # Set up nested dict of parameters for a more complex tree
        cls.nested_dict = cls.simple_dict.copy()
        cls.nested_dict['branch'] = {
            'branchIntParam': 4567,
            'branchStrParam': 'theBranch',
        }
        cls.nested_tree = DataTree(cls.nested_dict)

    def test_simple_tree_returns_dict(self):

        dt_vals = self.simple_tree.getData('')
        assert_equal(dt_vals, self.simple_dict)

    def test_simple_tree_single_values(self):

        dt_int_val = self.simple_tree.getData('intParam')
        assert_equal(dt_int_val['intParam'], self.int_value)

        dt_float_val = self.simple_tree.getData('floatParam')
        assert_equal(dt_float_val['floatParam'], self.float_value)

        dt_bool_val = self.simple_tree.getData('boolParam')
        assert_equal(dt_bool_val['boolParam'], self.bool_value)

        dt_str_val = self.simple_tree.getData('strParam')
        assert_equal(dt_str_val['strParam'], self.str_value)

    def test_nested_tree_returns_nested_dict(self):

        nested_dt_vals = self.nested_tree.getData('')
        assert_equal(nested_dt_vals, self.nested_dict)

    def test_nested_tree_branch_returns_dict(self):

        branch_vals = self.nested_tree.getData('branch')
        assert_equals(branch_vals['branch'], self.nested_dict['branch'])
