# test_relation_manager_facade.py

import unittest
from unittest.mock import Mock, MagicMock

# Import the FacadeRelationManager class
from app.services.facade_relations_manager import FacadeRelationManager

class TestFacadeRelationManager(unittest.TestCase):
    def setUp(self):
        # Create mock facades
        self.mock_user_facade = MagicMock()
        self.mock_place_facade = MagicMock()
        self.mock_amenity_facade = MagicMock()
        self.mock_review_facade = MagicMock()

        # Initialize the FacadeRelationManager with the mock facades
        self.relation_manager = FacadeRelationManager(
            user_facade=self.mock_user_facade,
            place_facade=self.mock_place_facade,
            amenity_facade=self.mock_amenity_facade,
            review_facade=self.mock_review_facade
        )

        # Sample user data
        self.sample_user = Mock()
        self.sample_user.id = "user-123"
        self.sample_user.first_name = "John"
        self.sample_user.places = []

        # Sample place data
        self.sample_place = Mock()
        self.sample_place.id = "place-456"
        self.sample_place.title = "Cozy Cottage"
        self.sample_place.owner_id = "user-123"
        self.sample_place.owner_first_name = "John"
        self.sample_place.amenities = []
        self.sample_place.reviews = []

        # Sample amenity data
        self.sample_amenity = Mock()
        self.sample_amenity.name = "WiFi"

        # Sample review data
        self.sample_review = Mock()
        self.sample_review.id = "review-789"
        self.sample_review.text = "Great place!"
        self.sample_review.rating = 5
        self.sample_review.place_id = "place-456"
        self.sample_review.user_id = "user-123"

    def test_create_place_for_user_success(self):
        """Test creating a place for a user successfully."""
        user_id = "user-123"
        place_data = {
            "title": "Cozy Cottage",
            "description": "A lovely cottage.",
            "price": 150.0,
            "latitude": 34.0522,
            "longitude": -118.2437,
        }

        # Mock user_facade.user_repo.get to return the sample user
        self.mock_user_facade.user_repo.get.return_value = self.sample_user

        # Mock place_facade.create_place to return the created place data
        created_place_data = {
            **place_data,
            "id": "place-456",
            "owner_first_name": "John",
            "owner_id": "user-123",
            "amenities": [],
            "reviews": []
        }
        self.mock_place_facade.create_place.return_value = created_place_data

        # Mock user's to_dict method
        self.sample_user.to_dict.return_value = {
            "id": "user-123",
            "first_name": "John",
            "places": ["place-456"]
        }

        # Call the method
        result = self.relation_manager.create_place_for_user(user_id, place_data)

        # Assertions
        self.mock_user_facade.user_repo.get.assert_called_once_with(user_id)
        expected_place_data = {
            **place_data,
            "owner_id": user_id,
            "amenities": [],
            "reviews": [],
            "owner_first_name": "John"
        }
        self.mock_place_facade.create_place.assert_called_once_with(expected_place_data)
        self.assertIn("place-456", self.sample_user.places)
        self.mock_user_facade.user_repo.update.assert_called_once_with(user_id, self.sample_user.to_dict())
        self.assertEqual(result, created_place_data)

    def test_create_place_for_user_user_not_found(self):
        """Test creating a place when the user is not found."""
        user_id = "user-999"
        place_data = {
            "title": "Cozy Cottage",
            "description": "A lovely cottage.",
            "price": 150.0,
            "latitude": 34.0522,
            "longitude": -118.2437,
        }

        # Mock user_facade.user_repo.get to return None
        self.mock_user_facade.user_repo.get.return_value = None

        # Call the method and expect ValueError
        with self.assertRaises(ValueError) as context:
            self.relation_manager.create_place_for_user(user_id, place_data)

        self.mock_user_facade.user_repo.get.assert_called_once_with(user_id)
        self.assertIn(f"User with id {user_id} not found.", str(context.exception))

    def test_get_all_places_dict_from_user_place_id_list_success(self):
        """Test getting all places for a user successfully."""
        user_id = "user-123"
        self.sample_user.places = ["place-456", "place-789"]
        self.mock_user_facade.user_repo.get.return_value = self.sample_user

        # Mock places using simple objects
        class MockPlace:
            def __init__(self, id, title):
                self.id = id
                self.title = title

            def to_dict(self):
                return {"id": self.id, "title": self.title}

        place_456 = MockPlace("place-456", "Cozy Cottage")
        place_789 = MockPlace("place-789", "Modern Apartment")

        # Mock place_facade.place_repo.get to return these places
        def mock_get(place_id):
            if place_id == "place-456":
                return place_456
            elif place_id == "place-789":
                return place_789
            else:
                return None

        self.mock_place_facade.place_repo.get.side_effect = mock_get

        # Call the method
        result = self.relation_manager.get_all_places_dict_from_user_place_id_list(user_id)

        # Assertions
        self.mock_user_facade.user_repo.get.assert_called_once_with(user_id)
        self.mock_place_facade.place_repo.get.assert_any_call("place-456")
        self.mock_place_facade.place_repo.get.assert_any_call("place-789")
        expected_result = [place_456.to_dict(), place_789.to_dict()]
        self.assertEqual(result, expected_result)

    def test_get_all_places_dict_from_user_place_id_list_user_not_found(self):
        """Test getting all places when the user is not found."""
        user_id = "user-999"
        self.mock_user_facade.user_repo.get.return_value = None

        with self.assertRaises(ValueError) as context:
            self.relation_manager.get_all_places_dict_from_user_place_id_list(user_id)

        self.mock_user_facade.user_repo.get.assert_called_once_with(user_id)
        self.assertIn(f"User with id: {user_id} not found", str(context.exception))

    def test_get_all_places_dict_from_user_place_id_list_no_places(self):
        """Test getting all places when the user has no places."""
        user_id = "user-123"
        self.sample_user.places = []
        self.mock_user_facade.user_repo.get.return_value = self.sample_user

        with self.assertRaises(ValueError) as context:
            self.relation_manager.get_all_places_dict_from_user_place_id_list(user_id)

        self.assertIn(f"No place found for this user: {user_id}", str(context.exception))

    def test_add_amenity_to_a_place_success(self):
        """Test adding an amenity to a place successfully."""
        place_id = "place-456"
        amenity_data = {"name": "WiFi"}

        # Mock place_facade.place_repo.get to return sample_place
        self.mock_place_facade.place_repo.get.return_value = self.sample_place

        # Mock amenity_facade.create_amenity to return amenity data
        created_amenity_data = {"id": "amenity-001", "name": "WiFi"}
        self.mock_amenity_facade.create_amenity.return_value = created_amenity_data

        # Mock place's to_dict method
        self.sample_place.to_dict.return_value = {
            "id": "place-456",
            "title": "Cozy Cottage",
            "amenities": ["WiFi"]
        }

        # Call the method
        result = self.relation_manager.add_amenity_to_a_place(place_id, amenity_data)

        # Assertions
        self.mock_place_facade.place_repo.get.assert_called_once_with(place_id)
        self.assertIn("WiFi", self.sample_place.amenities)
        self.mock_place_facade.place_repo.update.assert_called_once_with(place_id, self.sample_place.to_dict())
        self.mock_amenity_facade.create_amenity.assert_called_once_with(amenity_data)
        self.assertEqual(result, created_amenity_data)

    def test_add_amenity_to_a_place_place_not_found(self):
        """Test adding an amenity when the place is not found."""
        place_id = "place-999"
        amenity_data = {"name": "WiFi"}

        # Mock place_facade.place_repo.get to return None
        self.mock_place_facade.place_repo.get.return_value = None

        with self.assertRaises(ValueError) as context:
            self.relation_manager.add_amenity_to_a_place(place_id, amenity_data)

        self.mock_place_facade.place_repo.get.assert_called_once_with(place_id)
        self.assertIn(f"Place: {place_id} not found.", str(context.exception))

    # Continue adding tests for other methods...

if __name__ == '__main__':
    unittest.main()