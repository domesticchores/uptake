const inputBox = document.getElementById('input-box');
const chatBox = document.getElementById('chat-box');

inputBox.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && inputBox.value.trim() !== '') {
        if (inputBox.value.trim() == 'clear') {
            chatBox.innerHTML = '';
            inputBox.value = '';
            appendMessage('Notification Bot', "What can I help you with?");
            return;
        }
        const userText = inputBox.value;
        appendMessage('You', userText);
        inputBox.value = '';

        fetch('/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: userText })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage('Notification Bot', data.response);
        });
    }
});

function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    if (sender == 'You') {
        messageDiv.classList.add('you-message');
    } else {
        messageDiv.classList.add('message');
    }
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}