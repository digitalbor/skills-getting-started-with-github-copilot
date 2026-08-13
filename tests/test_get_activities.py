"""Tests for GET /activities endpoint."""
import pytest


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_all_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_structure(self, client):
        """Test that each activity has the required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check that we have activities
        assert len(activities) > 0
        
        # Check the structure of each activity
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_count(self, client):
        """Test that participant counts are accurate."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "alice@test.edu" in activities["Chess Club"]["participants"]
        assert "bob@test.edu" in activities["Chess Club"]["participants"]
        
        # Programming Class should have 1 participant
        assert len(activities["Programming Class"]["participants"]) == 1
        assert "charlie@test.edu" in activities["Programming Class"]["participants"]

    def test_get_activities_empty_participants(self, client):
        """Test that activities with no participants show empty list."""
        response = client.get("/activities")
        activities = response.json()
        
        # Empty Activity should have no participants
        assert len(activities["Empty Activity"]["participants"]) == 0
        assert activities["Empty Activity"]["participants"] == []

    def test_get_activities_max_participants_type(self, client):
        """Test that max_participants is an integer."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
