function chkFormNull() {
  if (
    document.loginForm.userid.value == "" ||
    document.loginForm.userid.value == null
  ) {
    alert("아이디를 입력해주세요.");
  } else if (
    document.loginForm.userpw.value == "" ||
    document.loginForm.userpw.value == null
  ) {
    alert("패스워드를 입력해주세요.");
  } else {
    document.loginForm.submit();
  }
}
