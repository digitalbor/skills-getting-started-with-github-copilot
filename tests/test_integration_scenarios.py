"""Integration tests for multi-step scenarios."""
import pytest


class TestIntegrationScenarios:
    """Test suite for complex end-to-end scenarios."""

    def test_signup_then_unregister_workflow(self, client):
        """Test the complete workflow: signup then unregister."""
        # 1. Sign up a new student
        signup_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@test.edu"}
        )
        assert signup_response.status_code == 200
        
        # 2. Verify student is in the list
        response = client.get("/activities")
        assert "michael@test.edu" in response.json()["Chess Club"]["participants"]
        original_count = len(response.json()["Chess Club"]["participants"])
        
        # 3. Unregister the student
        unregister_response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@test.edu"}
        )
        assert unregister_response.status_code == 200
        
        # 4. Verify student is removed
        response = client.get("/activities")
        assert "michael@test.edu" not in response.json()["Chess Club"]["participants"]
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == original_count - 1

    def test_multiple_students_same_activity(self, client):
        """Test that multiple students can sign up for the same activity."""
        students = ["nancy@test.edu", "oliver@test.edu", "patricia@test.edu"]
        
        # Sign up multiple students
        for student_email in students:
            response = client.post(
                "/activities/Programming Class/signup",
                params={"email": student_email}
            )
            assert response.status_code == 200
        
        # Verify all students are in the activity
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        
        for student_email in students:
            assert student_email in participants
        
        # Verify total count includes original participant
        assert len(participants) == len(students) + 1  # +1 for charlie@test.edu

    def test_participant_list_consistency_after_operations(self, client):
        """Test that participant list stays consistent after multiple operations."""
        activity_name = "Chess Club"
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = set(response.json()[activity_name]["participants"])
        
        # Perform series of operations
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "quinn@test.edu"}
        )
        
        response = client.get("/activities")
        after_signup = set(response.json()[activity_name]["participants"])
        
        # Verify the new participant was added
        assert "quinn@test.edu" in after_signup
        assert len(after_signup) == len(initial_participants) + 1
        
        # Unregister original participant
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": "alice@test.edu"}
        )
        
        response = client.get("/activities")
        after_unregister = set(response.json()[activity_name]["participants"])
        
        # Verify alice was removed but quinn is still there
        assert "alice@test.edu" not in after_unregister
        assert "quinn@test.edu" in after_unregister
        assert len(after_unregister) == len(initial_participants)

    def test_signup_across_multiple_activities(self, client):
        """Test that a student can signup for multiple activities independently."""
        student = "rachel@test.edu"
        activities = ["Chess Club", "Programming Class", "Empty Activity"]
        
        # Sign up for all activities
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Verify student appears in all activities
        response = client.get("/activities")
        all_activities = response.json()
        
        for activity in activities:
            assert student in all_activities[activity]["participants"]

    def test_unregister_from_one_activity_doesnt_affect_others(self, client):
        """Test that unregistering from one activity doesn't affect other activities."""
        student = "steven@test.edu"
        
        # Sign up for two activities
        client.post(
            "/activities/Chess Club/signup",
            params={"email": student}
        )
        client.post(
            "/activities/Programming Class/signup",
            params={"email": student}
        )
        
        # Verify student is in both
        response = client.get("/activities")
        assert student in response.json()["Chess Club"]["participants"]
        assert student in response.json()["Programming Class"]["participants"]
        
        # Unregister from Chess Club only
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": student}
        )
        
        # Verify removed from Chess Club but still in Programming Class
        response = client.get("/activities")
        assert student not in response.json()["Chess Club"]["participants"]
        assert student in response.json()["Programming Class"]["participants"]

    def test_activity_full_scenario(self, client):
        """Test behavior when trying to fill an activity to capacity."""
        # Empty Activity has max_participants of 10
        activity_name = "Empty Activity"
        
        # Sign up students one by one
        for i in range(5):
            email = f"user{i}@test.edu"
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all signed up
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert len(participants) == 5
        
        # Unregister one and verify
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": "user0@test.edu"}
        )
        
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert len(participants) == 4
        assert "user0@test.edu" not in participants

    def test_error_recovery_workflow(self, client):
        """Test that app recovers correctly after errors."""
        student = "tina@test.edu"
        
        # Try to sign up for non-existent activity (should fail)
        response = client.post(
            "/activities/Fake Activity/signup",
            params={"email": student}
        )
        assert response.status_code == 404
        
        # Now try to sign up for valid activity (should succeed)
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": student}
        )
        assert response.status_code == 200
        
        # Verify student was added
        response = client.get("/activities")
        assert student in response.json()["Chess Club"]["participants"]
