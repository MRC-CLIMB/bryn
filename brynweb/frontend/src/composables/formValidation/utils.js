const mapToFormOptions = (entities) => {
  /*
   * Quick map to convert simple id/name entities to {value, label} option lists
   */
  return entities.map((entity) => {
    return {
      value: entity.id,
      label: entity.name,
    };
  });
};

export { mapToFormOptions };
