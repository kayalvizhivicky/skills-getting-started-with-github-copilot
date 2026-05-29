document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
          activityCard.className = "activity-card";

          const spotsLeft = details.max_participants - details.participants.length;

          const participantsHtml = (details.participants && details.participants.length)
          ? `<div class="participants">
               <h5>Participants</h5>
               <ul class="participants-list">
                 ${details.participants.map(email => `<li><span class="participant-email">${email}</span><button class="delete-participant" data-activity="${name}" data-email="${email}" title="Unregister">✕</button></li>`).join('')}
               </ul>
             </div>`
          : `<div class="participants empty">
               <h5>Participants</h5>
               <p class="no-participants">No participants yet</p>
             </div>`;
          activityCard.innerHTML = `\n          <h4>${name}</h4>\n          <p>${details.description}</p>\n          <p><strong>Schedule:</strong> ${details.schedule}</p>\n          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>\n          ${participantsHtml}\n        `;

          activitiesList.appendChild(activityCard);

          // Add option to select dropdown
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          activitySelect.appendChild(option);
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
        signupForm.reset();
        // Refresh activities list to show new participant
        fetchActivities();
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

  // Handle delete participant button clicks
  document.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-participant")) {
      const activityName = event.target.getAttribute("data-activity");
      const email = event.target.getAttribute("data-email");

      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
          { method: "POST" }
        );

        const result = await response.json();

        if (response.ok) {
          messageDiv.textContent = result.message;
          messageDiv.className = "success";
          messageDiv.classList.remove("hidden");
          setTimeout(() => messageDiv.classList.add("hidden"), 5000);
          // Refresh activities list
          fetchActivities();
        } else {
          messageDiv.textContent = result.detail || "Failed to unregister";
          messageDiv.className = "error";
          messageDiv.classList.remove("hidden");
          setTimeout(() => messageDiv.classList.add("hidden"), 5000);
        }
      } catch (error) {
        messageDiv.textContent = "Error unregistering participant";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        console.error("Error:", error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
