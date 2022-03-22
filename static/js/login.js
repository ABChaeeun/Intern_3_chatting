window.onload = function() {
//$(function(){
    console.log("window onload : start");
//    document.getElementById('loginButton').addEventListener('click', function(){
//    var id = document.getElementById('id').value;
//    var passwd = document.getElementById('passwd').value;

////////////////////////////////////////////////
// login 버튼
    $("#loginButton").click(function(){
        var valueById = $('#id').val();
        var valueByPasswd = $('#passwd').val();
        IDPW = {'id':valueById, 'pw':valueByPasswd}

        console.log("로그인버튼을 눌렀습니다");

        $.post("/webapi/idpw", IDPW, function(ret){
            console.log("$.post()");
              if(ret.status=='ok'){
                window.location.href = '/loginSuccess';
              }else{
//                alert(ret);
                alert(ret.reason)
              }
        });
    });
//});
};