export default class CheckboxFormGuard {
  /* Enable/disable a form submit button based upon one or more required checkboxes */
  constructor(checkboxIds, buttonId) {
    if (typeof checkboxIds === "string") checkboxIds = [checkboxIds]; // handle single string id
    this.inputs = checkboxIds.map((checkboxId) => {
      return document.getElementById(checkboxId);
    });
    this.button = document.getElementById(buttonId);
    this.setupEventListeners();
  }

  setupEventListeners() {
    this.inputs.forEach(() => {
      document.addEventListener("click", () => this.setButtonStatus());
    });
    window.addEventListener("load", () => this.setButtonStatus()); // Handle back button
  }

  setButtonStatus() {
    if (this.inputs.every((input) => input.checked)) {
      this.button.removeAttribute("disabled");
    } else {
      this.button.setAttribute("disabled", true);
    }
  }
}
