$(document).ready(function () {
  $("#btnSubmit").click(function () {
    var topCan = document.getElementById("top_stuPresident").value;
    var secCan1 = document.getElementById("sec_stuPresident1").value;
    var secCan2 = document.getElementById("sec_stuPresident2").value;
    var msgCandidate = document.getElementById("msgCandidate").value;
    var length = document.getElementsByName("candidate_name").length;
    var arr = [];

    for (var i = 0; i < length; i++) {
      var nameCandidate = document.getElementsByName("candidate_name")[i].value;
      if (nameCandidate === (undefined || null || "")) {
        alert("후보자 이름을 입력하세요.");
        return false;
      }
    }

    if (msgCandidate === (undefined || null || "")) {
      alert("공약을 입력하세요.");
      return false;
    } else {
      for (var i = 0; i < length; i++) {
        arr.push(document.getElementsByName("candidate_name")[i].value);
      }
      alert(
        "총 학생 회장 후보 : " +
          arr[0] +
          "\n부 학생 회장 후보1: " +
          arr[1] +
          "\n부 학생 회장 후보2 : " +
          arr[2] +
          "\n후보자 공약 : \n" +
          msgCandidate
      );
      return false;
    }
  });
});
