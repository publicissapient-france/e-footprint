from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject

import unittest
from unittest.mock import patch, MagicMock, PropertyMock

MODELING_OBJ_CLASS_PATH = "footprint_model.abstract_modeling_classes.modeling_object"

class TestModelingSubObject(ModelingObject):
    def compute_calculated_attributes(self):
        pass


class TestModelingObject(unittest.TestCase):

    def setUp(self):
        self.modeling_object = TestModelingSubObject("test_object")

    def test_setattr_sets_modeling_obj_container(self):
        value = MagicMock(modeling_obj_container=None)

        with patch(f"{MODELING_OBJ_CLASS_PATH}.type", lambda x: ExplainableObject):
            self.modeling_object.attribute = value

        value.set_modeling_obj_container.assert_called_once_with(self.modeling_object, "attribute")

    def test_setattr_raises_error_if_value_already_linked_to_another_modeling_obj_container(self):
        value = MagicMock(modeling_obj_container=MagicMock(id="mod obj id"))
        self.modeling_object.id = "another obj id"

        with patch(f"{MODELING_OBJ_CLASS_PATH}.type", lambda x: ExplainableObject):
            with self.assertRaises(ValueError):
                self.modeling_object.attribute = value

    def test_handle_model_input_update_triggers(self):
        value = MagicMock(modeling_obj_container=None, left_child=None, right_child=None)
        old_value = MagicMock()
        self.modeling_object.attribute = old_value
        self.modeling_object.handle_model_input_update = MagicMock()

        with patch(f"{MODELING_OBJ_CLASS_PATH}.type", lambda x: ExplainableObject):
            self.modeling_object.attribute = value

            self.modeling_object.handle_model_input_update.assert_called_once_with(old_value)

    def test_handle_model_input_update(self):
        # TODO implement
        pass



if __name__ == "__main__":
    unittest.main()
