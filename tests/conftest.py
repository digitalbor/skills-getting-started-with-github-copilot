import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Return a FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture
def test_activities():
    """
    Fixture that provides a clean set of test activities for each test.
    This ensures test isolation - each test gets a fresh copy of the data.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": ["alice@test.edu", "bob@test.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 5,
            "participants": ["charlie@test.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Mondays, 2:00 PM - 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
    }


@pytest.fixture(autouse=True)
def reset_activities(test_activities):
    """
    Fixture that automatically runs before and after each test to reset
    the global activities dictionary. This ensures test isolation.
    """
    # Store original activities
    original_activities = dict(activities)
    
    # Clear and populate with test data
    activities.clear()
    activities.update(test_activities)
    
    yield
    
    # Restore original activities after test completes
    activities.clear()
    activities.update(original_activities)
