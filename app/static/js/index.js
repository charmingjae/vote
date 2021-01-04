$(document).ready(function () {
  var date1 = new Date("2021-01-05 18:02:00");
  var date2 = new Date();
  if (date2 > date1) {
    console.log("Big");
    $("#btnVote").attr("disabled", true);
  } else {
    console.log("smaller");
    $("#btnVote").attr("disabled", false);
  }
});
