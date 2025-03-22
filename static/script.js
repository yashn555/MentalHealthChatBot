// Global variable to store the Chart instance
let moodChart = null;

// Send message on Enter key press
document.getElementById("user-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Function to send a message to the chatbot
async function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (!userInput) return;

    let chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="chat-message user-message"><strong>You:</strong> ${userInput}</div>`;

    try {
        let response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput })
        });

        let data = await response.json();
        if (data.error) {
            chatBox.innerHTML += `<div class="chat-message bot-message"><strong>Error:</strong> ${data.error}</div>`;
        } else {
            chatBox.innerHTML += `<div class="chat-message bot-message"><strong>Bot:</strong> ${data.response}</div>`;
        }
    } catch (error) {
        console.error("Error sending message:", error);
        chatBox.innerHTML += `<div class="chat-message bot-message"><strong>Error:</strong> Failed to send message.</div>`;
    }

    document.getElementById("user-input").value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
    loadChatHistory(); // Reload chat history
    loadMoodChart(); // Update mood chart
}

// Function to load chat history
async function loadChatHistory() {
    try {
        let response = await fetch("/chat_history");
        let data = await response.json();
        let historyList = document.getElementById("chat-history");
        historyList.innerHTML = data.map(h => `
            <li>
                <span>${h.message}: ${h.response}</span>
                <button class="delete-btn" onclick="deleteChat(${Number(h.id)})">Delete</button>
            </li>
        `).join('');
    } catch (error) {
        console.error("Error loading chat history:", error);
    }
}

// Function to load and display the mood chart
async function loadMoodChart() {
    try {
        let response = await fetch("/mood_tracking");
        let data = await response.json();
        let ctx = document.getElementById('moodChart').getContext('2d');

        // Destroy the existing chart instance if it exists
        if (moodChart) {
            moodChart.destroy();
        }

        // Create a new chart instance
        moodChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.mood),
                datasets: [{
                    label: 'Mood Count',
                    data: data.map(d => d.count),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error loading mood chart:", error);
    }
}

// Function to delete a chat entry
async function deleteChat(chatId) {
    try {
        if (!chatId) {
            console.error("Chat ID is undefined");
            return;
        }
        let response = await fetch(`/delete_chat/${chatId}`, { method: "DELETE" });
        if (response.ok) {
            loadChatHistory(); // Reload chat history after deletion
        } else {
            console.error("Failed to delete chat:", await response.text());
        }
    } catch (error) {
        console.error("Error deleting chat:", error);
    }
}

// Function to open the change password modal
function openChangePasswordModal() {
    document.getElementById("changePasswordModal").style.display = "block";
}

// Function to close the change password modal
function closeChangePasswordModal() {
    document.getElementById("changePasswordModal").style.display = "none";
}

// Function to handle change password form submission
document.getElementById("changePasswordForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    let currentPassword = document.getElementById("currentPassword").value;
    let newPassword = document.getElementById("newPassword").value;
    let confirmPassword = document.getElementById("confirmPassword").value;

    if (newPassword !== confirmPassword) {
        alert("New passwords do not match!");
        return;
    }

    try {
        let response = await fetch("/change_password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ currentPassword, newPassword })
        });

        if (response.ok) {
            alert("Password changed successfully!");
            closeChangePasswordModal();
        } else {
            alert("Failed to change password. Please check your current password.");
        }
    } catch (error) {
        console.error("Error changing password:", error);
        alert("An error occurred while changing the password.");
    }
});

// Load chat history and mood chart when the page loads
window.onload = function() {
    loadChatHistory();
    loadMoodChart();
};