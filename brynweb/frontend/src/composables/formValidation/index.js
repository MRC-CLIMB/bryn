import { reactive } from "vue";
import { ValidationError, isRequired } from "./validators";

// Helpers

const titleCase = (str) => {
  return str.replace(/\w\S*/g, (t) => {
    return t.charAt(0).toUpperCase() + t.substr(1).toLowerCase();
  });
};

// CLasses

class FormField {
  constructor({
    name,
    label = undefined,
    element = "input",
    type = undefined,
    value = "",
    options = [],
    validators = [],
    iconClasses = undefined,
  }) {
    this.name = name;
    this.label = label ?? titleCase(name);
    this.element = element;
    this.type = type;
    this.value = value;
    this.options = options;
    this.validators = validators;
    this.iconClasses = iconClasses;

    this.errors = [];
    this.invalid = false;
    this.dirty = false;
  }

  get error() {
    /*
     * Field has been touched and is invalid.
     * Can be used in templates to show/hide validation messages.
     */
    return this.dirty && this.invalid;
  }

  get required() {
    return this.validators.includes(isRequired);
  }

  validate() {
    /*
     * Run all validators for field
     */
    this.errors = [];
    this.validators.forEach((validator) => {
      try {
        validator(this.value);
      } catch (err) {
        this.errors.push(err);
      }
    });
    this.invalid = this.errors.length > 0;
  }

  get touch() {
    return () => {
      /*
       * Mark a field as 'dirty' and call validate (arrow func to maintain this for callbacks)
       */
      this.dirty = true;
      this.validate();
    };
  }

  get debouncedTouch() {
    return (wait = 500) => {
      clearTimeout(this.timeout);
      this.timeout = setTimeout(this.touch, wait);
    };
  }

  resetValidation() {
    /*
     * Reset field validation
     */
    this.errors = [];
    this.dirty = false;
    this.invalid = false;
  }
}

class Form {
  constructor(fields) {
    this.fields = fields;
    this.nonFieldErrors = [];
  }

  get valid() {
    /*
     * Check that all form fields are valid.
     */
    return Object.values(this.fields).every((field) => {
      return !field.invalid;
    });
  }

  get enableSubmit() {
    /*
     * Should the form submission button be enabled?
     */
    return Object.values(this.fields).every((field) => {
      return !field.invalid && (field.value?.length > 0 || !field.required);
    });
  }

  get dirty() {
    /*
     * Has at least one field been touched?
     */
    return Object.values(this.fields).some((field) => field.dirty);
  }

  get values() {
    /*
     * Reduce the form object to simply {key: value, ...}.
     * Trim string inputs.
     */
    return Object.entries(this.fields).reduce((acc, [key, field]) => {
      acc[key] = field.value.trim();
      return acc;
    }, {});
  }

  resetValidation() {
    /*
     * Reset form validation state
     */
    this.nonFieldErrors = [];
    Object.values(this.fields).forEach((field) => field.resetValidation());
  }

  validate() {
    /*
     * Validate all form fields
     */
    this.nonFieldErrors = [];
    Object.values(this.fields).forEach((field) => {
      field.validate();
    });
  }

  get onFieldValidate() {
    /*
     * Handle a field validation event (arrow func to make suitable for event callback)
     */
    return ($event) => {
      const field = this.fields[$event.target.name];
      if (field == null) return;
      field.value = $event.target.value;
      switch ($event.type) {
        case "input":
          field.debouncedTouch(500);
          break;
        case "blur":
          field.debouncedTouch(0);
          break;
        case "change":
          field.touch();
          break;
      }
    };
  }

  parseResponseError(error) {
    /*
     * Parse server side errors (in usual Django Rest Framework format)
     */
    this.nonFieldErrors = [];

    if (Array.isArray(error)) {
      /* DRF response can be simply an array of message strings */
      error.forEach((message) => {
        this.nonFieldErrors.push(new ValidationError(message));
      });
    } else {
      /* In other cases, respnse is an Object where keys are field names, each with an array of message strings */
      Object.entries(error).forEach(([fieldName, fieldErrors]) => {
        fieldErrors.forEach((message) => {
          if (Object.prototype.hasOwnProperty.call(this.fields, fieldName)) {
            this.fields[fieldName].errors.push(new ValidationError(message));
            this.fields[fieldName].invalid = true;
          } else {
            this.nonFieldErrors.push(new ValidationError(message));
          }
        });
      });
    }
  }
}

// Default export

export default function useFormValidation(fields) {
  /*
   * Create a form from field options object.
   * Interface is { fieldName1: { type, [label], [options], [validators] }, fieldName2...}
   */
  const form = new Form(
    Object.entries(fields).reduce((acc, [key, options]) => {
      acc[key] = new FormField({ name: key, ...options });
      return acc;
    }, {})
  );
  return reactive(form);
}
