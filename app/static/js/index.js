const { start } = require("repl");

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
  var startDate = new Date("2021-02-12 18:02:00");
  var endDate = new Date("2021-02-13 18:02:00");
  if (endDate <= now) {
    location.href = "/voteOver";
  } else if (now < startDate) {
    location.href = "/voteBef";
  } else {
    location.href = "/vote";
  }
}
