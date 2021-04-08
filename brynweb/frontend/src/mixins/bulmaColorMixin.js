export default {
  props: {
    color: {
      type: String,
      required: false,
      default: "",
      validator: function(value) {
        return (
          [
            "",
            "white",
            "light",
            "dark",
            "black",
            "text",
            "primary",
            "link",
            "success",
            "warning",
            "danger",
            "info",
            "ghost",
          ].indexOf(value) !== -1
        );
      },
    },
  },
  computed: {
    colorClass() {
      if (this.color) {
        return "is-" + this.color;
      }
    },
    textColorClass() {
      if (this.color) {
        return "has-text-" + this.color;
      }
    },
  },
};
