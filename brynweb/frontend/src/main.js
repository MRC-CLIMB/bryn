import { createApp } from "vue";

import { axios } from "@/api";
import store from "@/store";
import router from "@/router";

import Toast, { POSITION } from "vue-toastification";
import VueClickAway from "vue3-click-away";

// Font Awesome
import { library } from "@fortawesome/fontawesome-svg-core";
import {
  faAngleDown,
  faBox,
  faBuilding,
  faBullhorn,
  faCheck,
  faCheckCircle,
  faEye,
  faEyeSlash,
  faExclamationCircle,
  faGlobeEurope,
  faHdd,
  faInfoCircle,
  faKey,
  faLink,
  faMemory,
  faMicrochip,
  faPhone,
  faPlusCircle,
  faSave,
  faServer,
  faSpinner,
  faSyncAlt,
  faTag,
  faTimes,
  faTimesCircle,
  faTrashAlt,
  faUniversity,
  faUnlink,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

library.add(
  faAngleDown,
  faBox,
  faBuilding,
  faBullhorn,
  faCheck,
  faCheckCircle,
  faEye,
  faEyeSlash,
  faExclamationCircle,
  faGlobeEurope,
  faHdd,
  faInfoCircle,
  faKey,
  faLink,
  faMemory,
  faMicrochip,
  faPhone,
  faPlusCircle,
  faSave,
  faServer,
  faSpinner,
  faSyncAlt,
  faTag,
  faTimes,
  faTimesCircle,
  faTrashAlt,
  faUniversity,
  faUnlink
);

// Create App
import App from "@/App";
const app = createApp(App);

// Plugin registration
app.use(store);
app.use(router);
app.config.globalProperties.$http = axios;
app.use(VueClickAway);
const toastOptions = {
  position: POSITION.BOTTOM_LEFT,
};
app.use(Toast, toastOptions);

// Error handling (Sentry, pending official Vue 3 integration)
import { captureException, init, setTag } from "@sentry/browser";
app.config.errorHandler = (error, _, info) => {
  setTag("info", info);
  captureException(error);
};

init({
  dsn:
    "https://ecce5d21027544c8b534f2f9c4e51514@o563550.ingest.sentry.io/5703644",
});

// Global base component registration
app.component("font-awesome-icon", FontAwesomeIcon);

import BaseButton from "@/components/base/BaseButton";
import BaseButtons from "@/components/base/BaseButtons";
import BaseButtonCancel from "@/components/base/BaseButtonCancel";
import BaseButtonConfirm from "@/components/base/BaseButtonConfirm";
import BaseButtonCreate from "@/components/base/BaseButtonCreate";
import BaseButtonDelete from "@/components/base/BaseButtonDelete";
import BaseCard from "@/components/base/BaseCard";
import BaseDropdown from "@/components/base/BaseDropdown";
import BaseDropdownList from "@/components/base/BaseDropdownList";
import BaseFlexCentered from "@/components/base/BaseFlexCentered";
import BaseFormControl from "@/components/base/BaseFormControl";
import BaseFormField from "@/components/base/BaseFormField";
import BaseFormInput from "@/components/base/BaseFormInput";
import BaseFormInputSelect from "@/components/base/BaseFormInputSelect";
import BaseFormValidated from "@/components/base/BaseFormValidated";
import BaseFormValidatedControl from "@/components/base/BaseFormValidatedControl";
import BaseFormValidatedInput from "@/components/base/BaseFormValidatedInput";
import BaseHeroFull from "@/components/base/BaseHeroFull";
import BaseIcon from "@/components/base/BaseIcon";
import BaseLevel from "@/components/base/BaseLevel";
import BaseLevelItem from "@/components/base/BaseLevelItem";
import BaseMessage from "@/components/base/BaseMessage";
import BaseMiniLoader from "@/components/base/BaseMiniLoader";
import BaseModal from "@/components/base/BaseModal";
import BaseModalCardClassic from "@/components/base/BaseModalCardClassic";
import BaseModalDelete from "@/components/base/BaseModalDelete";
import BaseModalSplit from "@/components/base/BaseModalSplit";
import BaseNotification from "@/components/base/BaseNotification";
import BaseProgress from "@/components/base/BaseProgress";
import BaseTable from "@/components/base/BaseTable";
import BaseTag from "@/components/base/BaseTag";
import BaseTagControl from "@/components/base/BaseTagControl";
import BaseTabs from "@/components/base/BaseTabs";

app.component("BaseButton", BaseButton);
app.component("BaseButtons", BaseButtons);
app.component("BaseButtonCancel", BaseButtonCancel);
app.component("BaseButtonConfirm", BaseButtonConfirm);
app.component("BaseButtonCreate", BaseButtonCreate);
app.component("BaseButtonDelete", BaseButtonDelete);
app.component("BaseCard", BaseCard);
app.component("BaseDropdown", BaseDropdown);
app.component("BaseDropdownList", BaseDropdownList);
app.component("BaseFlexCentered", BaseFlexCentered);
app.component("BaseFormControl", BaseFormControl);
app.component("BaseFormField", BaseFormField);
app.component("BaseFormInput", BaseFormInput);
app.component("BaseFormInputSelect", BaseFormInputSelect);
app.component("BaseFormValidated", BaseFormValidated);
app.component("BaseFormValidatedControl", BaseFormValidatedControl);
app.component("BaseFormValidatedInput", BaseFormValidatedInput);
app.component("BaseHeroFull", BaseHeroFull);
app.component("BaseIcon", BaseIcon);
app.component("BaseLevel", BaseLevel);
app.component("BaseLevelItem", BaseLevelItem);
app.component("BaseMessage", BaseMessage);
app.component("BaseMiniLoader", BaseMiniLoader);
app.component("BaseModal", BaseModal);
app.component("BaseModalCardClassic", BaseModalCardClassic);
app.component("BaseModalDelete", BaseModalDelete);
app.component("BaseModalSplit", BaseModalSplit);
app.component("BaseNotification", BaseNotification);
app.component("BaseProgress", BaseProgress);
app.component("BaseTable", BaseTable);
app.component("BaseTag", BaseTag);
app.component("BaseTagControl", BaseTagControl);
app.component("BaseTabs", BaseTabs);

app.mount("#app");
