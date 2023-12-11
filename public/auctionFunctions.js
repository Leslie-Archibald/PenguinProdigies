var sock;
var timerID = null;
var aucID = null;
function joinAuction(){
    sock = io.connect("wss://localhost:8080", { transports: ["websocket"] });
    sock.on("message",(data)=>{
        console.log(data);
    });
    sock.on("connect",(data)=>{
        console.log("Connection Success");
        aucID = document.getElementById("auctionData").getAttribute("aucID");
        timerID = setInterval(getInfo,1000);
        console.log("Timer started");
    });
    sock.on("info-response",(data)=>{
        info = JSON.parse(data);
        console.log(info);
        let timerElement = document.getElementById("timer");
        let currLeaderElement = document.getElementById("currLeader");
        let highestBidElement = document.getElementById("currBid");
        if(parseInt(info["timeSeconds"]) <= 0){
            //Times up!
            currLeaderElement.innerHTML="Winner: "+info["winner"];
            timerElement.innerHTML="Time Remaining: This auction has ended";
        }
        else{
            currLeaderElement.innerHTML="Current Leader: "+info["winner"];
            timerElement.innerHTML="Time Remaining: "+info["timeSeconds"];
        }
        highestBidElement.innerHTML="Highest Bid: "+info["bid"];
    });
    sock.on("bidResponse",(data)=>{
        console.log(data);
        if(data == 0){
            //bid unsuccessful
            console.log("Bid Unsuccessful");
        }
        else{
            //bid successful
            console.log("Bid Successful");
            getInfo();
        }
    });
    console.log("Got here");
    return;
}
function sendMessage(msg){
    sock.emit("message",msg);
    return;
}
function getInfo(){
    sock.emit("getInfo",aucID);
}
function submitBid(){
    auth=document.cookie;
    console.log("Cookies = "+auth);
    auth = auth.split(";");
    for(let i = 0;i<auth.length;i++){
        let temp = auth[i].split("=");
        if(temp[0].trim() == "auth"){
            auth = temp[1];
            break;
        }
    }
    bidAmount = document.getElementById("inputBid").value
    let bidInt = parseInt(bidAmount);
    document.getElementById("inputBid").value = ""
    if(bidInt != NaN){
        sock.emit("submitBid","{\"auth\":\""+auth+"\",\"bidAmount\":\""+bidAmount+"\",\"aucID\":\""+aucID+"\"}");
        console.log("auth="+auth);
    }
}
