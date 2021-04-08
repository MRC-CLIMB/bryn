/**
 * Updates a collection of objects for a team, optionally for a specific tenant
 *
 * @param {Object[]} collection - The collection to update
 * @param {Object[]} values - The new values
 * @param {number} - The team id
 * @param {Object} [options] - The options object
 * @param {Object} [options.tenantId] - The tenant id
 */
function updateTeamCollection(
  collection,
  values,
  { id: teamId },
  { id: tenantId } = { id: undefined }
) {
  // Replace existing values matching tenant or team (maintain ref to original array)
  const filtered = collection.filter((value) =>
    tenantId ? value.tenant !== tenantId : value.team !== teamId
  );
  collection.splice(0, collection.length, ...filtered);
  collection.push(...values);
}

function collectionForTeamId(collection, id) {
  return collection.filter((item) => item.team === id);
}

function collectionForTenantId(collection, id) {
  return collection.filter((item) => item.tenant === id);
}

function createFindByIdGetter(collection) {
  return (id) => {
    return collection.find((item) => item.id === id);
  };
}

function createFilterByTenantGetter(collection) {
  return ({ id }) => {
    return collectionForTenantId(collection, id);
  };
}

export {
  createFindByIdGetter,
  createFilterByTenantGetter,
  collectionForTeamId,
  collectionForTenantId,
  updateTeamCollection,
};
