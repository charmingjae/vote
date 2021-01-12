$(document).ready(function () {
  $(".navbar-burger").click(function () {
    if ($(".navbar-burger").hasClass("is-active") === true) {
      $(".navbar-burger").removeClass("is-active");
      $("#navbarBasicExample").removeClass("is-active");
    } else {
      $(".navbar-burger").addClass("is-active");
      $("#navbarBasicExample").addClass("is-active");
    }
  });
});
