<template>
  <div class="homeWrapper">
    <div :class="[showView ? 'showView' : 'hideView']">
      <TileList :tiles="tiles" />
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeView",
  data() {
    return {
      tiles: null,
      showView: false,
    };
  },
  methods: {
    updateMenu() {
      let menu = [];
      let user_menu = this.$store.state.user.menu;
      /* console.log("User menu: " + user_menu) */
      
      if (user_menu.includes("pilot"))
        menu.push({
          id: 1,
          name: "Pilot",
          method: () => {
            this.$router.push("/pilot");
          },
        });
      if (user_menu.includes("actions"))
        menu.push({
          id: 2,
          name: "Akcje",
          method: () => {
            this.$router.push("/actions");
          },
        });
      if (user_menu.includes("administration"))
        menu.push({
          id: 4,
          name: "Administracja",
          method: () => {
            this.$router.push("/administration");
          },
        });
      if (this.$store.state.user.uname === "admin")
        menu.push({
          id: 5,
          name: "Terminal",
          method: () => {
            window.open("http://192.168.1.45:5000/webgui/terminal");
          },
        });
      menu.push({
        id: 6,
        name: "Wyloguj",
        method: () => {
          this.$store.dispatch("handleLogout");
        },
      });
      this.tiles = menu;
    },
  },
  created() {
    this.$store.state.currentView = "RPi Smart House";
    if (!this.$store.state.user) this.$router.push("/login");
    else {
      this.updateMenu();
      this.$store.commit("changeBgImg", {
        imagePath: require("@/assets/home_bg.jpeg"),
        bgBlur: 5,
      });
    }
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
  },
  components: {
    TileList: require("@/components/basic_components/TileList.vue").default,
  },
};
</script>

<style lang="scss" scoped>
.homeWrapper {
  transition: all 0.2s;

  h1,
  p {
    max-width: 100vw;
    word-wrap: break-word;
  }

  h1 {
    margin: 15px 0 30px 0;
  }
  h3 {
    margin-top: 10px;
  }
}
</style>