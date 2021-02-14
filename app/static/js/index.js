$(document).ready(function () {
  var date1 = new Date("2021-02-20 18:02:00");
  var date2 = new Date();
  if (date2 > date1) {
    console.log("Big");
    $("#btnVote").attr("disabled", true);
  } else {
    console.log("smaller");
    $("#btnVote").attr("disabled", false);
  }
});

function chkTimes() {
  var now = new Date();
  var chkPoint = new Date("2021-02-13 18:02:00");
  if (now > chkPoint) {
    location.href = "/voteOver";
  } else {
    location.href = "/vote";
  }
}
