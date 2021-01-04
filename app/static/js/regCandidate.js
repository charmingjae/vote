$(document).ready(function () {
  $("#btnSubmit").click(function () {
    var topCan = document.getElementById("top_stuPresident").value;
    var secCan1 = document.getElementById("sec_stuPresident1").value;
    var secCan2 = document.getElementById("sec_stuPresident2").value;

    if (
      topCan === (undefined || null || "") ||
      secCan1 === (undefined || null || "") ||
      secCan2 === (undefined || null || "")
    ) {
      alert("후보자 이름을 입력하세요.");
      return false;
    } else {
      alert("다 입력하였음");
      return false;
    }
  });
});
