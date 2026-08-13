"""Tests for POST /activities/{activity_name}/signup endpoint."""
import pytest


class TestSignup:
    """Test suite for the POST signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "david@test.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "david@test.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup adds the student to the participants list."""
        # Sign up a new participant
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "eva@test.edu"}
        )
        
        # Verify they were added
        response = client.get("/activities")
        activities = response.json()
        assert "eva@test.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 3  # 2 original + 1 new

    def test_signup_to_empty_activity(self, client):
        """Test signup to an activity with no current participants."""
        response = client.post(
            "/activities/Empty Activity/signup",
            params={"email": "frank@test.edu"}
        )
        
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert "frank@test.edu" in activities["Empty Activity"]["participants"]

    def test_signup_duplicate_student_fails(self, client):
        """Test that the same student cannot sign up twice for the same activity."""
        # alice@test.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "alice@test.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found(self, client):
        """Test that signup fails for a non-existent activity."""
        response = client.post(
            "/activities/Non-existent Activity/signup",
            params={"email": "george@test.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_response_format(self, client):
        """Test that signup response has correct format."""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "hannah@test.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data) == 1  # Only message field

    def test_signup_same_student_different_activities(self, client):
        """Test that the same student can sign up for different activities."""
        # isaac@test.edu signs up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "isaac@test.edu"}
        )
        assert response1.status_code == 200
        
        # isaac@test.edu signs up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": "isaac@test.edu"}
        )
        assert response2.status_code == 200
        
        # Verify they appear in both activities
        response = client.get("/activities")
        activities = response.json()
        assert "isaac@test.edu" in activities["Chess Club"]["participants"]
        assert "isaac@test.edu" in activities["Programming Class"]["participants"]

    def test_signup_preserves_existing_participants(self, client):
        """Test that signup preserves existing participants."""
        # Get current participants before signup
        response = client.get("/activities")
        original_participants = response.json()["Chess Club"]["participants"].copy()
        
        # Add new participant
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "julia@test.edu"}
        )
        
        # Verify original participants are still there
        response = client.get("/activities")
        new_participants = response.json()["Chess Club"]["participants"]
        
        for participant in original_participants:
            assert participant in new_participants
        assert "julia@test.edu" in new_participants
