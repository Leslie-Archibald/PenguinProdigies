function createLink(){
    document.getElementById("cookie-link").innerHTML = "<ul><li><a href='http://localhost:8080/visit-counter'>Click here to see the /visit-counter page!</a></li></ul>"
}

function sendLike(postID){
    console.log("Got here!!!")
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
    request.open("POST", "/like-message");
    request.send(postID);
}

function chatMessageHTML(messageJSON) {
    const username = messageJSON["username"]
    const title = messageJSON["title"];
    const postID = messageJSON["id"];
    const description = messageJSON["description"];
    const numLikes = messageJSON["numLikes"];
    let messageHTML = "<br><button onclick='deleteMessage(" + title + ")'>X</button> ";
    messageHTML +=  "<span id='" + postID + "'title='" + title + "'><b>" + username + "</b>: " + 
                        description +
                        "<button className='likeButton' onClick=\"sendLike(\'"+postID+"\')\"> numLikes = "+numLikes+"</button>" +
                    "</span>";
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
    descriptionTextBox.value = "";
    const username = "Guest";
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

function sendAuction(){
    const itemBox = document.getElementById("itemName");
    const item = itemBox.value;
    itemBox.value = "";

    const descripBox = document.getElementById("itemDescription")
    const description = descripBox.value;
    descripBox.value = "";

    const bidBox = document.getElementById("startingBid")
    const bid = bidBox.value;
    bidBox.value = "";

    const timeList = document.getElementsByName("time")
    for (i = 0; i < timeList.length; i++){
        if (timeList[i].checked){
            const startTime = timeList[i].value;
            timeList[i].checked = false;
        }
    }

    // TODO: get and attach file information to post request 


    // username = auction creator, id = post id
    const username = document.getElementById('userid').innerText;
    const id = this.crypto.randomUUID();
    const messageJSON = {"title": item, "auction creator": username, "description": description, "id": id, "bid": bid, "time": time};
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("POST", "/auction-message");
    request.send(JSON.stringify(messageJSON));
    titleTextBox.focus();
    descriptionTextBox.focus();
}   

function auctionMessageHTML(messageJSON){
    const username = messageJSON["username"]
    const title = messageJSON["title"];
    const postID = messageJSON["id"];
    const description = messageJSON["description"];
    const numLikes = messageJSON["numLikes"];
    let messageHTML = "<br><button onclick='deleteMessage(" + title + ")'>X</button> ";
    messageHTML +=  "<span id='" + postID + "'title='" + title + "'><b>" + username + "</b>: " + 
                        "I'm selling " + title + "! "
                        "<button className='joinAuctionButton' onClick=\"joinAuction(\'"+postID+"\')\">Join Auction!</button>" +
                    "</span>";
    return messageHTML;

}

function joinAuction(postID){
    newPath = "/auction/"+postID;
    location.assign(newPath);
}
    //return auctionHTML;
//}   
