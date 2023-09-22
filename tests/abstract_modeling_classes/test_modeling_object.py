from footprint_model.abstract_modeling_classes.modeling_object import ModelingObject
from footprint_model.abstract_modeling_classes.explainable_object_base_class import ExplainableObject

import unittest
from unittest.mock import patch, Mock, call
from pubsub import pub


class TestModelingSubObject(ModelingObject):
    def compute_calculated_attributes(self):
        pass


class TestModelingObject(unittest.TestCase):

    def setUp(self):
        self.modeling_object = TestModelingSubObject("test_object")

    def test_setattr_attribute_used_in_calculation(self):
        value = ExplainableObject(1, "test_value")
        self.modeling_object.attribute = value
        self.assertEqual(f"attribute_in_{self.modeling_object.name}_{self.modeling_object.id}", value.pubsub_topic)

    @patch.object(pub, "sendMessage")
    def test_setattr_publishes_message(self, mock_send_message):
        value = ExplainableObject(1, "test_value")
        self.modeling_object.attribute = value
        mock_send_message.assert_called_once_with(f"attribute_in_{self.modeling_object.name}_{self.modeling_object.id}")

    @patch.object(pub, "subscribe")
    def test_setattr_update_function_output(self, mock_subscribe):
        value = ExplainableObject(1, "test_value")
        self.modeling_object.update_attribute = Mock()  # Mocking the update method
        self.modeling_object.attribute = value
        mock_subscribe.assert_called()

    @patch.object(pub, "subscribe")
    def test_setattr_update_function_output_with_child(self, mock_subscribe):
        value = ExplainableObject(1, "test_value")
        child = ExplainableObject(1, "test_value")
        value.left_child = child
        self.modeling_object.update_attribute = Mock()  # Mocking the update method
        self.modeling_object.attribute = value

        expected_calls = [
            call(self.modeling_object.update_attribute, 'topic_1'),
            call(self.modeling_object.update_attribute, 'topic_2')
        ]
        mock_subscribe.assert_has_calls(expected_calls, any_order=True)

    @patch.object(pub, "subscribe")
    def test_setattr_remove_attribute(self, mock_subscribe):
        value = ExplainableObject(1, "test_value")
        self.modeling_object.update_attribute = Mock()  # Mocking the update method
        self.modeling_object.attribute = value
        del self.modeling_object.attribute
        expected_calls = [
            call(self.modeling_object.update_attribute, 'topic_1'),
            call(self.modeling_object.update_attribute, 'topic_2')
        ]
        mock_subscribe.assert_has_calls(expected_calls, any_order=True)

    def test_setattr_with_modeling_object_without_old_value(self):
        value = TestModelingSubObject("value")  # Replace with your ModelingObject subclass

        with patch.object(self.modeling_object, 'compute_calculated_attributes') as mock_compute:
            self.modeling_object.attribute = value
            mock_compute.assert_called_once()

    @patch.object(pub, "subscribe")
    def test_setattr_same_attribute_multiple_times(self, mock_subscribe):
        value = ExplainableObject(1, "test_value")
        self.modeling_object.update_attribute = Mock()  # Mocking the update method
        self.modeling_object.attribute = value
        self.modeling_object.attribute = value  # Set the same attribute again

        expected_calls = [
            call(self.modeling_object.update_attribute, 'topic_1'),
            call(self.modeling_object.update_attribute, 'topic_2')
        ]
        mock_subscribe.assert_has_calls(expected_calls, any_order=True)

    def test_setattr_invalid_update_method(self):
        value = ExplainableObject(1, "test_value")
        with self.assertRaises(ValueError):
            self.modeling_object.attribute = value  # Value doesn't have the required update method


if __name__ == "__main__":
    unittest.main()
