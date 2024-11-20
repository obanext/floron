let thread_id = null;

async function startThread() {
    const response = await fetch('/start_thread', { method: 'POST' });
    const data = await response.json();
    thread_id = data.thread_id;
}

function checkInput() {
    const userInput = document.getElementById('user-input').value.trim();
    const sendButton = document.getElementById('send-button');
    sendButton.disabled = userInput === "";
}

async function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();
    if (!userInput) return;

    displayUserMessage(userInput);
    showLoader();

    document.getElementById('user-input').value = '';
    document.getElementById('send-button').disabled = true;

    try {
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ thread_id, user_input: userInput })
        });

        const data = await response.json();
        hideLoader();

        if (data.response) {
            displayAssistantMessage(data.response);
        }
    } catch (error) {
        console.error('Error:', error);
        hideLoader();
        displayAssistantMessage('Something went wrong, please try again.');
    }
}

function displayUserMessage(message) {
    const messageContainer = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('user-message');
    messageElement.textContent = message;
    messageContainer.appendChild(messageElement);
    scrollToBottom();
}

function displayAssistantMessage(message) {
    const messageContainer = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('assistant-message');
    messageElement.textContent = message;
    messageContainer.appendChild(messageElement);
    scrollToBottom();
}

function showLoader() {
    const messageContainer = document.getElementById('messages');
    const loaderElement = document.createElement('div');
    loaderElement.classList.add('loader');
    loaderElement.textContent = 'Typing...';
    messageContainer.appendChild(loaderElement);
    scrollToBottom();
}

function hideLoader() {
    const loaderElement = document.querySelector('.loader');
    if (loaderElement) {
        loaderElement.remove();
    }
}

function scrollToBottom() {
    const messageContainer = document.getElementById('messages');
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

window.onload = async () => {
    await startThread();
    document.getElementById('user-input').addEventListener('input', checkInput);
};
