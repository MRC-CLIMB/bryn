class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
  }
}

const isRequired = (value) => {
  if (typeof value === "string") {
    if (value.trim().length > 0) {
      return true;
    }
  } else {
    if (value != null) {
      return true;
    }
  }
  throw new ValidationError("Value required");
};

const isAlphaNumHyphensOnly = (value) => {
  if (!value || /^([a-zA-Z0-9-]+)$/.test(value)) {
    return true;
  }
  throw new ValidationError("Only letters, numbers and hyphens are allowed");
};

const isValidEmailSyntax = (value) => {
  if (!value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    return true;
  }
  throw new ValidationError("Please enter a valid email address");
};

const isPublicKey = (value) => {
  const re = /^(ssh-rsa AAAAB3NzaC1yc2|ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNT|ecdsa-sha2-nistp384 AAAAE2VjZHNhLXNoYTItbmlzdHAzODQAAAAIbmlzdHAzOD|ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1Mj|ssh-ed25519 AAAAC3NzaC1lZDI1NTE5|ssh-dss AAAAB3NzaC1kc3)[0-9A-Za-z+/]+[=]{0,3}( .*)?$/;
  if (!value || re.test(value)) {
    return true;
  }
  throw new ValidationError("A valid SSH key is required");
};

export {
  ValidationError,
  isAlphaNumHyphensOnly,
  isPublicKey,
  isRequired,
  isValidEmailSyntax,
};
