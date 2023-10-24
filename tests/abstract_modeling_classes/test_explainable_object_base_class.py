from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.constants.units import u

from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestExplainableObjectBaseClass(TestCase):
    def setUp(self) -> None:
        self.a = ExplainableObject(1, "a")
        self.b = ExplainableObject(2, "b")

        self.c = ExplainableObject(3, "c")
        self.c.left_child = self.a
        self.c.right_child = self.b
        self.c.child_operator = "+"

        self.d = ExplainableObject(4, "d")
        self.d.left_child = self.c
        self.d.right_child = self.a
        self.d.child_operator = "+"

        self.e = ExplainableObject(5, "e")
        self.e.left_child = self.c
        self.e.right_child = self.b
        self.e.child_operator = "+"
        self.e.label = None

        self.f = ExplainableObject(6, "f")
        self.f.left_child = self.e
        self.f.right_child = self.a
        self.f.child_operator = "+"

        self.g = ExplainableObject(2, "g")
        self.g.left_child = self.d
        self.g.child_operator = "root square"

    def test_deepcopy_should_set_modeling_object_to_none(self):
        a = ExplainableObject(1, "a")
        a.modeling_obj_container = "obj"
        from copy import deepcopy
        b = deepcopy(a)

        self.assertEqual("a", b.label)
        self.assertEqual(1, b.value)
        self.assertIsNone(b.modeling_obj_container)

    def test_creation_with_label(self):
        eo = ExplainableObject(value=5, label="Label A")
        self.assertEqual(eo.value, 5)
        self.assertEqual(eo.label, "Label A")
        self.assertIsNone(eo.left_child)
        self.assertIsNone(eo.right_child)

    def test_creation_without_label_and_child(self):
        with self.assertRaises(ValueError):
            ExplainableObject(value=5)

    def test_set_modeling_obj_container(self):
        # TODO implement
        pass

    def test_return_direct_children_with_id_to_parent(self):
        # TODO implement
        pass

    def test_update_direct_parents_with_id(self):
        # TODO implement
        pass

    def test_get_all_ancestors_with_id(self):
        # TODO implement
        pass

    def test_direct_children(self):
        left_child = ExplainableObject(value=3, label="Label L")
        right_child = ExplainableObject(value=4, label="Label R")
        left_child.modeling_obj_container = MagicMock(name="lc_mod_obj_name", id="lc_mod_obj_id")
        right_child.modeling_obj_container = MagicMock(name="rc_mod_obj_name", id="rc_mod_obj_id")

        eo = ExplainableObject(value=7, left_child=left_child, right_child=right_child, label="Parent")
        self.assertEqual([left_child, right_child], eo.direct_children_with_id)

    def test_define_as_intermediate_calculation(self):
        eo = ExplainableObject(value=5, label="Label A")
        eo.define_as_intermediate_calculation("Intermediate A")
        self.assertEqual(eo.label, "Intermediate A")

    def test_has_child_property(self):
        left_child = ExplainableObject(value=3, label="Label L")
        eo_with_child = ExplainableObject(value=7, left_child=left_child, label="Parent")
        eo_without_child = ExplainableObject(value=7, label="Parent")
        self.assertTrue(eo_with_child.has_child)
        self.assertFalse(eo_without_child.has_child)

    def test_explain_simple_sum(self):
        self.assertEqual("c = a + b = 1 + 2 = 3", self.c.explain(pretty_print=False))

    def test_explain_nested_sum(self):
        self.assertEqual("d = c + a = 3 + 1 = 4", self.d.explain(pretty_print=False))

    def test_explain_should_skip_calculus_element_without_label(self):
        self.assertEqual("f = c + b + a = 3 + 2 + 1 = 6", self.f.explain(pretty_print=False))

    def test_explain_without_right_child(self):
        self.assertEqual("g = root square of (d) = root square of (4) = 2", self.g.explain(pretty_print=False))

    def test_explain_should_put_right_parenthesis_in_complex_calculations(self):
        self.d.label = None
        self.c.label = None
        h = ExplainableObject(1, None, self.c, self.c, "/")
        i = ExplainableObject(2, None, h, self.g, "*")
        j = ExplainableObject(-1, "k", i, self.c, "-")
        self.assertEqual('k = ((a + b) / (a + b)) * g - (a + b) = ((1 + 2) / (1 + 2)) * 2 - (1 + 2) = -1', j.explain(
            pretty_print=False))

    def test_explain_without_children(self):
        eo = ExplainableObject(value=5, label="Label A")
        result = eo.explain()
        self.assertEqual(result, "Label A = 5")

    def test_compute_explain_nested_tuples(self):
        left_child = ExplainableObject(value=3, label="Label L")
        right_child = ExplainableObject(value=4, label="Label R")
        eo = ExplainableObject(value=7, left_child=left_child, right_child=right_child, label="Parent",
                               child_operator="+")
        result = eo.compute_explain_nested_tuples()
        self.assertEqual(result, (left_child, '+', right_child))

    def test_print_tuple_element_value(self):
        self.assertEqual("5.3 W", ExplainableObject.print_tuple_element_value(5.3456 * u.W))
        self.assertEqual(
            "[1.1 yr, 2.2 yr, 3.3 yr]", ExplainableObject.print_tuple_element_value(
                [ExplainableObject(1.123 * u.year, "duration"), ExplainableObject(2.234 * u.year, "duration"),
                 ExplainableObject(3.345 * u.year, "duration")]))
        self.assertEqual("[[1, 2], [3, 5]]", ExplainableObject.print_tuple_element_value([[1, 2], [3, 5]]))

    def test_print_tuple_element(self):
        left_child = ExplainableObject(value=3, label="Label L")
        right_child = ExplainableObject(value=4, label="Label R")
        eo = ExplainableObject(value=7, left_child=left_child, right_child=right_child, label="Parent",
                               child_operator="+")

        self.assertEqual(eo.print_tuple_element((left_child, '+', right_child), False), "Label L + Label R")
        self.assertEqual(eo.print_tuple_element((left_child, '+', right_child), True), "3 + 4")

    def test_pretty_print_calculation(self):
        calc_str = "Label A = Label L + Label R = 3 + 4 = 7"
        result = ExplainableObject.pretty_print_calculation(calc_str)
        expected_result = """Label A
=
Label L + Label R
=
3 + 4
=
7"""
        self.assertEqual(expected_result, result)

    def test_set_mod_obj_cont_raises_error_if_value_already_linked_to_another_modeling_obj_container_and_children(self):
        self.a.modeling_obj_container = MagicMock(id="mod obj id")
        new_parent_mod_obj = MagicMock(id="another obj id")
        self.a.left_child = "non null left child"

        with self.assertRaises(ValueError):
            self.a.set_modeling_obj_container(new_parent_mod_obj, "test_attr_name")
