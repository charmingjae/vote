function mngDelete() {
  var len = document.getElementsByName("candNum").length;
  var flag = false;
  var temp;
  console.log(len);
  for (var i = 0; i < len; i++) {
    if (document.getElementsByName("candNum")[i].checked) {
      temp = document.getElementsByName("candNum")[i];
      flag = true;
    }
  }
  if (!flag) {
    alert("관리 할 후보자를 선택하세요.");
  } else {
    conf = confirm("삭제하시겠습니까?");
    if (conf == true) {
      $("#mngForm_id").append("<input type='hidden' name='act' value='1' />");
      document.mngForm.submit();
    } else {
      return false;
    }
  }
}

function mngModify() {
  var len = document.getElementsByName("candNum").length;
  var flag = false;
  var temp;
  console.log(len);
  for (var i = 0; i < len; i++) {
    if (document.getElementsByName("candNum")[i].checked) {
      temp = document.getElementsByName("candNum")[i];
      flag = true;
    }
  }
  if (!flag) {
    alert("관리 할 후보자를 선택하세요.");
  } else {
    $("#mngForm_id").append("<input type='hidden' name='act' value='2' />");
    document.mngForm.submit();
  }
}

function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(location.search);
  return results == null
    ? ""
    : decodeURIComponent(results[1].replace(/\+/g, " "));
}

$(document).ready(function () {
  if (getParameterByName("flag")) {
    if (getParameterByName("flag") == 1) {
      alert("삭제가 완료되었습니다.");
      window.location.href = "/manageCandidate";
    }
  } else {
  }
});
