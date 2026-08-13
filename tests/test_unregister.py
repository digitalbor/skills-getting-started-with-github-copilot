"""Tests for DELETE /activities/{activity_name}/unregister endpoint."""
import pytest


class TestUnregister:
    """Test suite for the DELETE unregister endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity."""
        # alice@test.edu is in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "alice@test.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alice@test.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_removes_participant_from_list(self, client):
        """Test that unregister removes the student from participants list."""
        # Verify alice is in Chess Club
        response = client.get("/activities")
        assert "alice@test.edu" in response.json()["Chess Club"]["participants"]
        
        # Unregister alice
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "alice@test.edu"}
        )
        
        # Verify alice was removed
        response = client.get("/activities")
        activities = response.json()
        assert "alice@test.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1  # Only bob remains

    def test_unregister_decrements_count(self, client):
        """Test that unregister correctly decrements participant count."""
        # Chess Club has 2 participants initially
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        assert initial_count == 2
        
        # Remove one participant
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "alice@test.edu"}
        )
        
        # Verify count decreased
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1

    def test_unregister_student_not_registered(self, client):
        """Test that unregister fails when student is not registered."""
        # kevinl@test.edu is not in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "kevin@test.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()

    def test_unregister_activity_not_found(self, client):
        """Test that unregister fails for a non-existent activity."""
        response = client.delete(
            "/activities/Non-existent Activity/unregister",
            params={"email": "alice@test.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_response_format(self, client):
        """Test that unregister response has correct format."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "alice@test.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data) == 1  # Only message field

    def test_unregister_from_empty_activity_fails(self, client):
        """Test that unregister fails when activity has no participants."""
        # Empty Activity has no participants
        response = client.delete(
            "/activities/Empty Activity/unregister",
            params={"email": "liam@test.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_unregister_preserves_other_participants(self, client):
        """Test that unregistering one participant doesn't affect others."""
        # Get participants before unregister
        response = client.get("/activities")
        participants_before = response.json()["Chess Club"]["participants"].copy()
        
        # Unregister alice
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "alice@test.edu"}
        )
        
        # Get participants after unregister
        response = client.get("/activities")
        participants_after = response.json()["Chess Club"]["participants"]
        
        # Verify bob is still there
        assert "bob@test.edu" in participants_after
        # Verify alice is gone
        assert "alice@test.edu" not in participants_after
        # Verify only alice was removed
        assert len(participants_after) == len(participants_before) - 1

    def test_unregister_twice_fails(self, client):
        """Test that unregistering the same student twice fails."""
        # First unregister succeeds
        response1 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "alice@test.edu"}
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "alice@test.edu"}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data
