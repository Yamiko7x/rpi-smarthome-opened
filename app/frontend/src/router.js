import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/LoginView.vue';
import PilotView from '@/views/PilotView.vue';
import AdministrationView from '@/views/AdministrationView.vue';
import ActionsView from '@/views/ActionsView.vue';
import ActionEditor from '@/views/ActionEditor.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/pilot',
    name: 'pilot',
    component: PilotView,
  },
  {
    path: '/administration',
    name: 'administration',
    component: AdministrationView,
  },
  {
    path: '/actions',
    name: 'actions',
    component: ActionsView,
  },
  {
    path: '/actioneditor/:action_id',
    name: 'actioneditor',
    component: ActionEditor,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
