document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Create variable for email input and add listener to execute fetchActivities when the email value changes
  const emailInput = document.getElementById("email");
  emailInput.addEventListener("change", () => {
    const userEmail = emailInput.value;
    fetchActivities(userEmail);
  });

  // Function to fetch activities from API
  async function fetchActivities(userEmail) {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear previous options in the select dropdown
      activitySelect.innerHTML = '<option value="">Select an activity</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Add disabled class to activities that the user has already signed up for.
        // disabled when the user has already registered for it.
        const userAlreadySignedUp = userEmail && details.participants.includes(userEmail);
        if (userAlreadySignedUp) {
          activityCard.classList.add("disabled");
        }
        const participantsList = details.participants.length > 0
          ? `<ul class="participants-list">${details.participants.map(email => `<li><span class="participant-email">${email}</span><button class="delete-participant" data-activity="${name}" data-email="${email}" type="button" title="Remove participant">×</button></li>`).join('')}</ul>`
          : '<p class="no-participants">No participants yet</p>';
        
        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Participants:</h5>
            ${participantsList}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // If userEmail is provided, check if the user is already signed up for this activity
        if (userEmail && details.participants.includes(userEmail)) {
          return; // Skip adding this activity to the dropdown if the user is already signed up
        }

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-participant").forEach(button => {
        button.addEventListener("click", async (event) => {
          event.preventDefault();
          const activityName = button.dataset.activity;
          const participantEmail = button.dataset.email;

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(participantEmail)}`,
              { method: "DELETE" }
            );

            if (response.ok) {
              fetchActivities(userEmail);
            } else {
              const result = await response.json();
              alert(result.detail || "Failed to remove participant");
            }
          } catch (error) {
            alert("Error removing participant");
            console.error("Error:", error);
          }
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        const userEmail = email; // Capture email before reset
        signupForm.reset();
        fetchActivities(userEmail); // Refresh activities to show new signup
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
