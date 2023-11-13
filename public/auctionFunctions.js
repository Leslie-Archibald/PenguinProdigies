var sock;
var timerID = null;
function joinAuction(){
    sock = io.connect("http://localhost:8080", { transports: ["websocket"] });
    sock.on('message',(data)=>{
        console.log(data);
    });
    sock.on('connect',(data)=>{
        console.log("Connection Success");
    })
    sock.on('time-left',(data)=>{
        var elem = document.getElementById("time-left");
        elem.innerHTML = "Time Left: "+data;
        console.log(data);
        if(parseInt(data) <= 0){
            clearInterval(timerID);
            timerID = null;
        }
    })
    console.log("Got here");
    return;
}
function sendMessage(msg){
    sock.emit("message",msg);
    return;
}
function updateTime(){
    sock.emit('get-time');
    console.log("Requesting timer update");
    return;
}
function timer(){
    sock.emit("start-timer"," ");
    clearInterval(timerID);
    timerID = setInterval(updateTime,1000);
    console.log("Timer started");
    return;
}