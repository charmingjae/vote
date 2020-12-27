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
  $("#userid").focusout(function () {
    // $("#usermajor").val("컴퓨터학과");
  });
});
