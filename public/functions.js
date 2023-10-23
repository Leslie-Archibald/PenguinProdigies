function createLink(){
    document.getElementById("cookie-link").innerHTML = "<ul><li><a href='http://localhost:8080/visit-counter'>Click here to see the /visit-counter page!</a></li></ul>"
}

function chatMessageHTML(messageJSON) {
    const username = messageJSON["username"]
    const title = messageJSON["title"];
    const description = messageJSON["description"];
    let messageHTML = "<br><button onclick='deleteMessage(" + title + ")'>X</button> ";
    messageHTML += "<span id='message_" + title + "'><b>" + title + "by:" + username + "</b>: " + description + "</span>";
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("chatHistory");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chatHistory");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function sendPost() {
    const titleTextBox = document.getElementById("titleBox");
    const title = titleTextBox.value;
    titleTextBox.value = ""
    const descriptionTextBox = document.getElementById("messageBox");
    const description = descriptionTextBox.value;
    descriptionTextBox.value = ""
    const url = window.location.href;
    // todo: peel off username from the end of the url (from last backslash on)
    // three options: it is empty (unlogged in, / filepath), it is index.html (unlogged in, /index filepath), or it is logged in
    // put this in an if/else statement
    // note: doing it this way is most likely a security risk
     

    const id = this.crypto.randomUUID();
    const messageJSON = {"title": title, "username": username, "description": description, "id": id};
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("POST", "/chat-message");
    request.send(JSON.stringify(messageJSON));
    titleTextBox.focus();
    descriptionTextBox.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-history");
    request.send();
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });

    updateChat();
    setInterval(updateChat, 2000);
}