// function chkFormNull() {
//   var len = document.voteForm.candidate.length;
//   var flag;
//   var chked;

//   for (i = 0; i < len; i++) {
//     if (document.voteForm.candidate[i].checked) {
//       flag = true;
//       chked = document.voteForm.candidate[i].value;
//       break;
//     } else {
//       flag = false;
//     }
//   }

//   if (flag === false) {
//     alert("후보자를 선택하세요.");
//     return false;
//   } else {
//     var conf = confirm(chked + " 번 후베에게 투표하시겠습니까?");
//     if (conf) {
//       document.voteForm.submit();
//     }
//   }
// }

function vote(elem) {
  var conf = confirm(elem.id + " 번 후보에게 투표하시겠습니까?");
  console.log(elem.id.toString());
  if (conf) {
    var frmName = document.getElementById(elem.id);
    console.log(frmName);
    document.getElementById(elem.id).submit();
  }
}

function vote1(elem) {
  var conf = confirm(elem.id + " 번 후보에게 투표하시겠습니까?");
  if (conf) {
    document.voteForm1.submit();
  }
}

function vote2(elem) {
  var conf = confirm(elem.id + " 번 후보에게 투표하시겠습니까?");
  if (conf) {
    document.voteForm2.submit();
  }
}
