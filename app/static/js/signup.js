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
