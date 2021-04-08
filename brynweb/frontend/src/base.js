// Bulma & styles
require("./assets/sass/main.scss");

// Font Awesome
import { library, dom } from "@fortawesome/fontawesome-svg-core";
import {
  faBuilding,
  faCheck,
  faEnvelope,
  faLock,
  faPhone,
  faUniversity,
  faUser,
  faUsers,
  faUserGraduate,
} from "@fortawesome/free-solid-svg-icons";

library.add(
  faBuilding,
  faCheck,
  faEnvelope,
  faLock,
  faPhone,
  faUniversity,
  faUser,
  faUsers,
  faUserGraduate
);

dom.watch();

// Hamburgers
document.addEventListener("DOMContentLoaded", () => {
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );
  if ($navbarBurgers.length > 0) {
    $navbarBurgers.forEach((el) => {
      el.addEventListener("click", () => {
        const target = el.dataset.target;
        const $target = document.getElementById(target);
        el.classList.toggle("is-active");
        $target.classList.toggle("is-active");
      });
    });
  }
});
