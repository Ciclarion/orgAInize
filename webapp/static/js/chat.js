document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const messages = document.getElementById('messages');
    const newConversationBtn = document.getElementById('new-conversation-btn');
    
    const conversationList = document.getElementById('conversation-list');

    let selectedConversationId = null;

    // Load the latest conversation on page load
    const latestConversation = conversationList.querySelector('li');
    if (latestConversation) {
        selectedConversationId = latestConversation.dataset.conversationId;
        loadConversation(selectedConversationId);
        
        latestConversation.classList.add('active');
    }
    
    let currentConversationId = selectedConversationId;

    // Handle conversation click
    conversationList.addEventListener('click', function (e) {
        if (e.target.tagName === 'LI') {
            const conversationId = e.target.dataset.conversationId;
            selectConversation(conversationId);
        }
    });

    newConversationBtn.addEventListener('click', function () {
        fetch('conversations/new/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
                loadConversation(currentConversationId);
                const newItem = document.createElement('li');
                newItem.dataset.conversationId = currentConversationId;
                newItem.textContent = `Conversation ${currentConversationId}`;
                newItem.addEventListener('click', function () {
                    currentConversationId = this.dataset.conversationId;
                    loadConversation(currentConversationId);
                    document.querySelectorAll('.conversation-list li').forEach(li => li.classList.remove('active'));
                    this.classList.add('active');
                });
                document.querySelector('.conversation-list ul').appendChild(newItem);
                document.querySelectorAll('.conversation-list li').forEach(li => li.classList.remove('active'));
                newItem.classList.add('active');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            appendMessage('User', message);
            messageInput.value = '';
            if (!currentConversationId) {
                createNewConversationAndSendMessage(message);
            } else {
                sendMessageToServer(message, currentConversationId);
            }
        }
    });

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `${sender}: ${message}`;
        messages.appendChild(messageElement);
        messages.scrollTop = messages.scrollHeight;  // Scroll to the bottom
    }

    function processBotResponse(botResponse) {
        const fileRegex = /[Ff]ichier_name:\s*(documents\/[^\s]+\.pdf)/g;  // Regex pour détecter les chemins de fichiers
        const fileRegexVF = /[Ff]ichier nom:\s*(documents\/[^\s]+\.pdf)/g;
        return botResponse.replace(fileRegexVF, '<a href="/$1" target="_blank">voir document</a>').replace(fileRegex, '<a href="/$1" target="_blank">voir document</a>');
    }
    
    function ajouterLiensVoirDocument(texte) {
        // Regex pour trouver les liens vers les fichiers PDF commençant par "documents/documents"
        const regex = /(documents\/documents\/[^/]+\/[^/]+\/[^/]+\/[^/]+\..+\.pdf)/g;

        // Obtenir l'URL absolue de base de votre site
        const baseUrl = window.location.origin;

        // Remplacer les liens correspondants par un lien "Voir document" avec une URL absolue
        const texteAvecLiens = texte.replace(regex, function(match, lienPDF) {
            const lienAbsolu = baseUrl + '/' + lienPDF; // Concaténer l'URL absolue de base avec le chemin relatif du lien PDF
            return `${lienPDF} <a href="${lienAbsolu}" target="_blank">Voir document</a>`;
        });

        return texteAvecLiens;
    }
    function sendMessageToServer(message, conversationId) {
        fetch(`/users/chat-api/${conversationId}/`, {  // Assurez-vous que le chemin est correct
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage('orgAInize', ajouterLiensVoirDocument(processBotResponse(data.response)));
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function loadConversation(conversationId) {
        fetch(`conversations/${conversationId}/`, {
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            messages.innerHTML = '';
            data.messages.forEach(msg => {
                appendMessage(msg.sender, ajouterLiensVoirDocument(processBotResponse(msg.text)));
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return csrfToken;
    }
    
    function selectConversation(conversationId) {
        if (selectedConversationId) {
            const prevSelected = conversationList.querySelector(`li[data-conversation-id="${selectedConversationId}"]`);
            if (prevSelected) {
                prevSelected.classList.remove('active');
            }
            
            currentConversationId = selectedConversationId;
        }
        const selectedElement = conversationList.querySelector(`li[data-conversation-id="${conversationId}"]`);
        if (selectedElement) {
            selectedElement.classList.add('active');
            selectedConversationId = conversationId;
            loadConversation(conversationId);
        }
    }
    
    function createNewConversationAndSendMessage(message) {
        fetch('conversations/new/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
                loadConversation(currentConversationId);
                const newItem = document.createElement('li');
                newItem.dataset.conversationId = currentConversationId;
                newItem.textContent = `Conversation ${currentConversationId}`;
                newItem.addEventListener('click', function () {
                    currentConversationId = this.dataset.conversationId;
                    loadConversation(currentConversationId);
                    document.querySelectorAll('.conversation-list li').forEach(li => li.classList.remove('active'));
                    this.classList.add('active');
                });
                conversationList.appendChild(newItem);
                newItem.classList.add('active');
                loadConversation(currentConversationId);
                sendMessageToServer(message, currentConversationId);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

