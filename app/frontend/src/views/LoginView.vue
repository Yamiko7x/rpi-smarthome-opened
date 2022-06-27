<template>
  <div class="login-wrapper">
    <form @submit.prevent="handleSubmit" :class="[showView ? 'showView' : 'hideView']">
      <h1>Zaloguj się</h1>
      <input
        type="text"
        name="uname"
        id="uname"
        v-model="uname"
        placeholder="Login"
      />
      <input
        type="password"
        name="password"
        id="password"
        v-model="password"
        placeholder="Hasło"
      />
      <input type="submit" value="Otwórz panel" />
    </form>
  </div>
</template>


<script>
import axios from "axios";
export default {
  name: "LoginView",
  // -------------------------------------------------
  data() {
    return {
      uname: "",
      password: "",
      showView: false
    };
  },
  // -------------------------------------------------
  methods: {
    async handleSubmit() {
      await axios
        .post("dbm_api/loginuser", {
          uname: this.uname,
          password: this.password,
        })
        .then((result) => {
          /* console.log(result.data); */
          if(result.data.auth) {
            this.$store.commit('updateUser', result.data);
            this.$store.state.refreshWidgetDelay = result.data.refresh_widget_delay;
          }
          else this.$store.dispatch('addMsg', {type: 'danger', msg: result.data.msg})
        })
        .catch((err) =>  console.log(err));
    },
  },
  // -------------------------------------------------
  created(){
    this.$store.state.currentView = ""
    if(this.$store.state.user) this.$router.push('/')
    else this.$store.commit('changeBgImg', {imagePath: require("@/assets/login_bg.jpeg"), bgBlur: 0});
    setTimeout(() => { this.showView = true; }, this.$store.state.animationSpeed);
  },
  unmounted(){
    this.$store.state.popupMessages = []
    console.log("Unmounted")
  }
};
</script>


<style lang="scss" scoped>
.login-wrapper {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;

  h1 {
    color: #fff;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.7);
  }
}
</style>
