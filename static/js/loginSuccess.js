var keyy = Math.floor(Math.random() * 100);

$(function(){
    console.log(keyy);
    var wsUri = "ws://172.16.16.225:5000/webSocket/chatchat?keyy="+keyy; //keyy 이걸 문자열로 읽는지?!=> yes. 그래서 add_argument('keyy', required=True) 여기서 그렇게 하라고 하는거다!
    output = document.getElementById("output");

    websocket = new WebSocket(wsUri);

    websocket.onopen = function(e){
        console.log("[open] 커넥션이 만들어졌습니다.");

        $("#sendbutton").click(function(){
            var valueLoginId = $('#login_id').text();
            var valueText = $('#myMessage').val();
            TEXT = {'loginId':valueLoginId, 'text':valueText}

//            console.log("send 버튼을 눌렀습니다");

            $.post("/webapi/text", TEXT, function(ret){
                console.log("$.post()");
            });
        });
    };

    websocket.onmessage = function(event) {
        console.log('[message] 서버로부터 전송받은 데이터: ${event.data}');
        $('#output').append(event.data+'<br>');
    };
});