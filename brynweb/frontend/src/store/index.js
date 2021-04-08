import { createStore } from "vuex";

// Root getters, mutations, actions
import getters from "./getters";
import mutations from "./mutations";
import actions from "./actions";

// Modules
import announcements from "./modules/announcements";
import flavors from "./modules/flavors";
import images from "./modules/images";
import instances from "./modules/instances";
import invitations from "./modules/invitations";
import keyPairs from "./modules/keyPairs";
import polling from "./modules/polling";
import teamMembers from "./modules/teamMembers";
import volumes from "./modules/volumes";
import volumeTypes from "./modules/volumeTypes";

const state = {
  adminEmail: "Lisa.Marchioretto@quadram.ac.uk",
  activeTeamId: null,
  hypervisorStats: [],
  faqs: [],
  filterTenantId: null,
  licenceTerms: null,
  regions: [],
  teams: [],
  user: null,
};

const modules = {
  announcements,
  flavors,
  images,
  instances,
  invitations,
  keyPairs,
  polling,
  teamMembers,
  volumes,
  volumeTypes,
};

export default createStore({
  modules,
  state,
  getters,
  actions,
  mutations,
});
