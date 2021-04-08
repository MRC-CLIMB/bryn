import { createRouter, createWebHistory } from "vue-router";

import Home from "@/views/Home";
import TeamHome from "@/views/TeamHome";

import Dashboard from "@/views/Dashboard";
import NotFound from "@/views/NotFound";
import Servers from "@/views/Servers";
import Volumes from "@/views/Volumes";
import KeyPairs from "@/views/KeyPairs";
import TeamManagement from "@/views/TeamManagement";
import UserProfile from "@/views/UserProfile";

const routes = [
  {
    path: "/",
    name: "home",
    component: Home,
  },
  {
    path: "/teams/:teamId",
    name: "teamHome",
    component: TeamHome,
    redirect: () => {
      return { name: "dashboard" };
    },
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: Dashboard,
        meta: {
          displayName: "Dashboard",
          displayNameShort: "Home",
          menuSection: "general",
        },
      },
      {
        path: "servers",
        name: "servers",
        component: Servers,
        meta: {
          displayName: "Servers",
          displayNameShort: "Servers",
          menuSection: "compute",
        },
      },
      {
        path: "volumes",
        name: "volumes",
        component: Volumes,
        meta: {
          displayName: "Volumes",
          displayNameShort: "Volumes",
          menuSection: "compute",
        },
      },
      {
        path: "keypairs",
        name: "keypairs",
        component: KeyPairs,
        meta: {
          displayName: "SSH Keys",
          displayNameShort: "Keys",
          menuSection: "compute",
        },
      },
      {
        path: "team",
        name: "teamManagement",
        component: TeamManagement,
        meta: {
          displayName: "Team Management",
          displayNameShort: "Team",
          menuSection: "admin",
        },
      },
      {
        path: "user",
        name: "userProfile",
        component: UserProfile,
        meta: {
          displayName: "User Profile",
          displayNameShort: "User",
          menuSection: "admin",
        },
      },
    ],
  },
  { path: "/:pathMatch(.*)*", name: "notfound", component: NotFound },
];
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
