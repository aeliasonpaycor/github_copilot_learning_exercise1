import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        # Arrange
        # Activities are already set up by the reset_activities fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) >= 2
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activity objects have required fields"""
        # Arrange
        expected_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        # Assert
        for field in expected_fields:
            assert field in chess_club
    
    def test_participants_list_in_activity(self, client, reset_activities):
        """Test that participants list is included in response"""
        # Arrange
        expected_participant = "michael@mergington.edu"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_participants = data["Chess Club"]["participants"]
        
        # Assert
        assert isinstance(chess_participants, list)
        assert expected_participant in chess_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test successfully signing up a new participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds participant to activity list"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up twice for same activity fails"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for non-existent activity fails"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_increments_participant_count(self, client, reset_activities):
        """Test that participant count increases after signup"""
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        
        # Assert
        assert count_after == count_before + 1


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_existing_participant(self, client, reset_activities):
        """Test successfully removing a participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
    
    def test_remove_participant_from_activity_list(self, client, reset_activities):
        """Test that remove actually deletes participant from list"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client, reset_activities):
        """Test that removing non-existent participant fails"""
        # Arrange
        activity_name = "Chess Club"
        email = "notexist@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_from_nonexistent_activity_fails(self, client, reset_activities):
        """Test that removing from non-existent activity fails"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_decrements_participant_count(self, client, reset_activities):
        """Test that participant count decreases after removal"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        
        # Assert
        assert count_after == count_before - 1


class TestIntegration:
    """Integration tests combining multiple endpoints"""
    
    def test_signup_and_remove_workflow(self, client, reset_activities):
        """Test complete signup and removal workflow"""
        # Arrange
        activity_name = "Programming Class"
        email = "integration@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        get_response = client.get("/activities")
        
        # Assert - Verified in list
        assert signup_response.status_code == 200
        assert email in get_response.json()[activity_name]["participants"]
        
        # Act - Remove
        delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")
        final_response = client.get("/activities")
        
        # Assert - Verified removed
        assert delete_response.status_code == 200
        assert email not in final_response.json()[activity_name]["participants"]
    
    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Test multiple different students signing up for same activity"""
        # Arrange
        activity_name = "Chess Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # Assert
        for email in emails:
            assert email in participants
    
    def test_signup_remove_signup_same_person(self, client, reset_activities):
        """Test that a person can sign up after being removed"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Remove
        client.delete(f"/activities/{activity_name}/participants/{email}")
        get_response_1 = client.get("/activities")
        
        # Assert - Removed
        assert email not in get_response_1.json()[activity_name]["participants"]
        
        # Act - Sign up again
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        get_response_2 = client.get("/activities")
        
        # Assert - Back in list
        assert signup_response.status_code == 200
        assert email in get_response_2.json()[activity_name]["participants"]
