var keyy = Math.floor(Math.random() * 100);

//window.onload = function() { // js로 .js로딩할때
$(function(){ // jQuery로 .js로딩할때
    console.log(keyy);
    var wsUri = "ws://172.16.16.225:5000/webSocket/chatchat?keyy="+keyy; //keyy 이걸 문자열로 읽는지?!=> yes. 그래서 add_argument('keyy', required=True) 여기서 그렇게 하라고 하는거다!
//    var wsUri = "ws://172.16.16.225:5000/webSocket/chatchat";
    var output;

    init();

    function init() {
         output = document.getElementById("output");
         testWebSocket();
         console.log("function init()");
    }

    function testWebSocket() {
        websocket = new WebSocket(wsUri);

        websocket.onopen = function(event) {
            onOpen(event)

            websocket.send("loginSuccess.js에서 send한 문장입니다");

            $('#sendbutton').on('click', function(){
                websocket.send($('#myMessage').val());
            //                $('#myMessage').val('');
            //                $('#output').append(websocket.send($('#myMessage').val()));
            });
        };
        websocket.onmessage = function (evt){
            $('#output').append('>> '+evt.data+'<br>');
        }
    }


    function onOpen(event) {
    //         document.getElementById("output").val = "CONNECTED";
         console.log("CONNECTED");
    //         alert("CONNECTED");
    }
//    addEvent('load', )
//};
});