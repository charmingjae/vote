function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(location.search);
  return results == null
    ? ""
    : decodeURIComponent(results[1].replace(/\+/g, " "));
}

$(document).ready(function () {
  $("#btnSubmit").click(function () {
    var msgCandidate = document.getElementById("msgCandidate").value;
    var nameLength = document.getElementsByName("candidate_name").length;
    var selLength = document.getElementsByName("stuPresident_dep").length;
    console.log(selLength);
    var nameArr = [];
    var depArr = [];

    for (var i = 0; i < nameLength; i++) {
      var nameCandidate = document.getElementsByName("candidate_name")[i].value;
      if (nameCandidate === (undefined || null || "")) {
        alert("후보자 이름을 입력하세요.");
        return false;
      }
    }

    for (var i = 0; i < selLength; i++) {
      var candDep = document.getElementsByName("stuPresident_dep")[i].value;
      console.log(candDep);
      if (candDep === (undefined || null || "")) {
        alert("후보자의 학과를 선택하세요.");
        return false;
      }
    }

    if (msgCandidate === (undefined || null || "")) {
      alert("공약을 입력하세요.");
      return false;
    } else {
      for (var i = 0; i < nameLength; i++) {
        nameArr.push(document.getElementsByName("candidate_name")[i].value);
      }
      for (var i = 0; i < selLength; i++) {
        depArr.push(document.getElementsByName("stuPresident_dep")[i].value);
      }
      if (
        confirm(
          "총 학생 회장 후보 : " +
            nameArr[0] +
            "\n총 학생 회장 학과 : " +
            depArr[0] +
            "\n\n부 학생 회장 후보1: " +
            nameArr[1] +
            "\n부 학생 회장 후보1 학과 : " +
            depArr[1] +
            "\n\n부 학생 회장 후보2 : " +
            nameArr[2] +
            "\n부 학생 회장 후보2 학과 : " +
            depArr[2] +
            "\n\n후보자 공약 : \n" +
            msgCandidate
        )
      ) {
        document.regCandidateForm.submit();
      } else {
        return false;
      }
    }
  });
});
