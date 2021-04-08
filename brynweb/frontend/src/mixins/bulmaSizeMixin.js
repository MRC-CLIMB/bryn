export default {
  props: {
    size: {
      type: String,
      default: "normal",
      validator: function (value) {
        return ["small", "normal", "medium", "large"].indexOf(value) !== -1;
      },
    },
  },
  computed: {
    sizeClass() {
      if (this.size) {
        return "is-" + this.size;
      }
    },
  },
};
