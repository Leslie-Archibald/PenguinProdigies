function createLink(){
    document.getElementById("cookie-link").innerHTML = "<ul><li><a href='http://localhost:8080/visit-counter'>Click here to see the /visit-counter page!</a></li></ul>"
}

function sendPost() {
    const titleTextBox = document.getElementById("title-text-box");
    const title = titleTextBox.value;
    const descriptionTextBox = document.getElementById("description-text-box");
    const description = descriptionTextBox.value;
    titleTextBox.value = "";
    descriptionTextBox.value = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    const username = "Guest"
    const messageJSON = {"title": title, "username": username, "description": description};
    request.open("POST", "/chat-message");
    request.send(JSON.stringify(messageJSON));
    chatTextBox.focus();
}