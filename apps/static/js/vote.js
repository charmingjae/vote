function chkFormNull() {
  var len = document.voteForm.candidate.length;
  var flag;

  for (i = 0; i < len; i++) {
    if (document.voteForm.candidate[i].checked) {
      flag = true;
      break;
    } else {
      flag = false;
    }
  }

  if (flag === false) {
    alert("후보자를 선택하세요.");
    return false;
  } else {
    document.voteForm.submit();
  }
}
