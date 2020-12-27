function chkFormNull() {
  if (
    document.signupForm.userid.value == "" ||
    document.signupForm.userid.value == null
  ) {
    alert("아이디를 입력해주세요.");
  } else if (
    document.signupForm.userpw.value == "" ||
    document.signupForm.userpw.value == null
  ) {
    alert("패스워드를 입력해주세요.");
  } else {
    document.signupForm.submit();
  }
}

// 페이지가 렌더링이 된 후에 함수 실행
$(document).ready(function () {
  $("#userid_id").focusout(function () {
    // flag
    // $("#usermajor").val("컴퓨터정보과");
    var userid = $("#userid_id").val().substring(4, 6);

    // 학과 자동 파싱
    switch (userid) {
      case "44":
        $("#usermajor_id").val("컴퓨터정보과");
        break;
      default:
        $("#usermajor_id").val("");
        break;
    }
  });
});
