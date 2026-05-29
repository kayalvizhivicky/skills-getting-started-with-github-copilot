import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    yield
    activities.clear()


class TestRoot:
    """Tests for root endpoint."""
    
    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        # Arrange
        expected_status = 307
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status
        assert response.headers["location"] == expected_location


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self):
        """Test getting all activities with correct structure"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity in expected_activities:
            assert activity in data
        assert data["Chess Club"]["max_participants"] == 12
        assert len(data["Chess Club"]["participants"]) == 2


class TestSignup:
    """Tests for POST /activities/{activity}/signup endpoint."""
    
    def test_signup_success_adds_participant(self):
        """Test successful signup adds participant to activity"""
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={new_email}")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_email in activities[activity]["participants"]
    
    def test_signup_duplicate_rejected(self):
        """Test that duplicate signup is rejected"""
        # Arrange
        activity = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={existing_email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_updates_participant_count(self):
        """Test that signup correctly updates participant count"""
        # Arrange
        activity = "Programming Class"
        initial_count = len(activities[activity]["participants"])
        new_email = "newprogrammer@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={new_email}")
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count + 1


class TestUnregister:
    """Tests for POST /activities/{activity}/unregister endpoint."""
    
    def test_unregister_success_removes_participant(self):
        """Test successful unregister removes participant from activity"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in activities[activity]["participants"]
    
    def test_unregister_not_registered_fails(self):
        """Test unregister for non-registered student returns 404"""
        # Arrange
        activity = "Chess Club"
        unregistered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={unregistered_email}")
        
        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self):
        """Test unregister from non-existent activity returns 404"""
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_updates_participant_count(self):
        """Test that unregister correctly updates participant count"""
        # Arrange
        activity = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(activities[activity]["participants"])
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count - 1


class TestSignupUnregisterFlow:
    """Integration tests for signup and unregister workflows."""
    
    def test_signup_then_unregister_flow(self):
        """Test complete flow: signup then unregister"""
        # Arrange
        activity = "Programming Class"
        email = "testuser@mergington.edu"
        
        # Act - Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert signup
        assert signup_response.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert unregister
        assert unregister_response.status_code == 200
        assert email not in activities[activity]["participants"]
    
    def test_multiple_signups_and_unregisters(self):
        """Test multiple sequential signups and unregisters"""
        # Arrange
        activity = "Gym Class"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        initial_count = len(activities[activity]["participants"])
        
        # Act - Signup all
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Assert all signed up
        assert len(activities[activity]["participants"]) == initial_count + len(emails)
        
        # Act - Unregister middle one
        response = client.post(f"/activities/{activity}/unregister?email={emails[1]}")
        
        # Assert
        assert response.status_code == 200
        assert emails[1] not in activities[activity]["participants"]
        assert emails[0] in activities[activity]["participants"]
        assert emails[2] in activities[activity]["participants"]
