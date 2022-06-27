import { createStore } from 'vuex'
import router from './router'
import axios from "axios"

export default createStore({
  state: {
    user: null,
    background: require("@/assets/login_bg.jpeg"),
    backgroundBlur: 0,
    popupMessages: [],
    animationSpeed: 100,
    currentview: '',
    goto: '',
    refreshWidgetDelay: 500,
    quickPanel: false,
    fnsDictRouls: null,
    messageDisplayTime: 3000,
    passwdRules: new RegExp("^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})"),
  },
  getters: {
    authDict: (state) => ( extDict ) => {
      if (extDict != null) return Object.assign({}, {user: state.user.uname, sessionlink: state.user.token}, extDict);
      else return {user: state.user.uname, sessionlink: state.user.token}
    }
  },
  mutations: {
    updateUser(state, userDict) {
      localStorage.setItem('user', JSON.stringify(userDict))
      state.user = userDict
      if(userDict) router.push("/");
    },
    logoutAxios(state) {
      axios
        .post("dbm_api/logout", {
          user: state.user.uname,
          sessionlink: state.user.token,
        })
        .then((result) => {
          console.log(result.data)
        })
        .catch((err) => {
          console.log(err);
        });
    },
    changeBgImg(state, { imagePath, bgBlur }) {
      localStorage.setItem('backgroundPath', imagePath)
      localStorage.setItem('backgroundBlur', bgBlur)
      state.background = imagePath
      state.backgroundBlur = bgBlur
    },
    restoreBackground(state) {
      if (localStorage.getItem('backgroundPath')) state.background = localStorage.getItem('backgroundPath')
      if (localStorage.getItem('backgroundBlur')) state.backgroundBlur = localStorage.getItem('backgroundBlur')
    },
  },
  actions: {
    handleLogout({ commit }) {
      commit('logoutAxios')
      commit('updateUser', null);
      localStorage.removeItem("user");
      router.push("/login");
    },
    isLoggedIn({state, dispatch}) {
      axios
        .post("dbm_api/isloggedin", {
          user: state.user.uname,
          sessionlink: state.user.token,
        })
        .then((result) => {
          if (result.data.auth) console.log(result.data)
          else dispatch('handleLogout')
        })
        .catch((err) => {
          console.log(err);
        });
    },
    changeBgImg({ commit }, { imagePath, bgBlur }) {
      commit('changeBgImg', imagePath, bgBlur)
    },
    addMsg({ state }, { type, msg, time }) {
      let newMsg = {
        id: state.popupMessages.length,
        type: type,
        msg: msg,
        active: true
      }
      state.popupMessages.push(newMsg)
      time = time ? time : state.messageDisplayTime;
      setTimeout(() => {  state.popupMessages[newMsg.id]["active"] = false; }, time);
    }
  },
  modules: {
  },
});