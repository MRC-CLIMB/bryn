import { ValidationError } from "@/utils/validators";

export default {
  data() {
    return {
      formNonFieldErrors: [],
    };
  },

  computed: {
    formIsValid() {
      /*
       * Check that all fields are:
       * Marked valid (validators have run successfully)
       * OR Have no validators
       * OR Have a value, but no 'valid' property set
       * - (i.e. they had data already and have not been 'dirtied' by user input)
       */
      return Object.values(this.form).every(
        (fieldObj) =>
          fieldObj.valid ||
          !fieldObj.validators?.length ||
          (fieldObj.value && !this.formFieldIsInvalid(fieldObj))
      );
    },
    formIsDirty() {
      /* Has the user input any data? */
      return Object.values(this.form).some((fieldObj) => fieldObj.dirty);
    },
    formValues() {
      /* Reduce the form object to simply {key: value, ...}. Trim string inputs. */
      return Object.entries(this.form).reduce((acc, [key, fieldObj]) => {
        acc[key] =
          typeof fieldObj.value === "string"
            ? fieldObj.value.trim()
            : fieldObj.value;
        return acc;
      }, {});
    },
  },

  methods: {
    formDirtyField(name) {
      /* Mark field as dirty (user has modified) */
      const field = this.form[name];
      field.dirty = true;
    },
    formResetValidation() {
      /* Remove all errors, validation flags and dirty flags */
      this.formNonFieldErrors = [];
      Object.values(this.form).forEach((field) => {
        delete field.errors;
        delete field.valid;
        delete field.dirty;
      });
    },
    formMapToOptions(entities) {
      /* Quick map to convert simple entities to {value, label} option lists */
      return entities.map((entity) => {
        return {
          value: entity.id,
          label: entity.name,
        };
      });
    },
    formValidate() {
      /* Validate all form fields */
      this.formNonFieldErrors = [];
      Object.keys(this.form).forEach((key) => {
        this.formValidateField(key);
      });
    },
    formValidateField(name) {
      /*
       * Run all validators for a particular field.
       * Push errors to array.
       * Set 'valid' property (absence can be assumed to mean no validation has occurred).
       */
      const field = this.form[name];
      field.errors = [];
      field.validators?.forEach((validator) => {
        try {
          validator(field.value);
        } catch (err) {
          field.errors.push(err);
        }
      });
      field.valid = !field.errors.length;
    },
    formFieldIsInvalid(field) {
      /*
       * Is a field definitely invalid? i.e. validators have run and failed
       * Absence of 'valid' property would mean we don't know, so would be false.
       */
      return field.hasOwnProperty("valid") ? !field.valid : false;
    },
    formParseResponseError(error) {
      /* Parse server side errors (in usual Django Rest Framework format) */
      Object.entries(error).forEach(([field, value]) => {
        value.forEach((message) => {
          if (this.form.hasOwnProperty(field)) {
            this.form[field].errors.push(new ValidationError(message));
          } else {
            this.formNonFieldErrors.push(
              new ValidationError(
                field == "non_field_errors" ? message : `${field}: ${message}`
              )
            );
          }
        });
      });
    },
  },
};
