from unittest import TestCase

from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject


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

    def test_explain_simple_sum(self):
        self.assertEqual("c = a + b = 1 + 2 = 3", self.c.explain(pretty_print=False))

    def test_explain_nested_sum(self):
        self.assertEqual("d = c + a = 3 + 1 = 4", self.d.explain(pretty_print=False))

    def test_explain_should_skip_calculus_element_without_label(self):
        self.assertEqual("f = c + b + a = 3 + 2 + 1 = 6", self.f.explain(pretty_print=False))

    def test_explain_without_right_child(self):
        self.assertEqual("g = root square of (d) = root square of (4) = 2", self.g.explain(pretty_print=False))
