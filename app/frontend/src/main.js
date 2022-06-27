import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './axios'
import store from './vuex'
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import ActionQueue from '@/components/actions_components/ActionQueue.vue'
import AutoComponent from '@/components/actions_components/AutoComponent.vue'
import PopupBox from '@/components/basic_components/PopupBox.vue'

library.add(fas)

createApp(App)
.use(router)
.use(store)
.component('FA-Icon', FontAwesomeIcon)
.component('ActionQueue', ActionQueue)
.component('AutoComponent', AutoComponent)
.component('PopupBox', PopupBox)
.mount('#app');
