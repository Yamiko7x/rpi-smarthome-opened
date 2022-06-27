<template>
  <div class="administration-wrapper">
    <div :class="[showView ? 'showView' : 'hideView']">
      <div class="administrationMenu">
        <button v-on:click="this.renderPanel = 'users'">
          Lista użytkowników
        </button>
        <button v-on:click="this.renderPanel = 'register'">
          Dodaj użytkownika
        </button>
        <button v-on:click="this.renderPanel = 'devices'">
          Urządzenia
        </button>
      </div>
      <div class="selfScrollBox">
        <UserRegisterForm v-if="renderPanel === 'register'" :closeEvent="closeEvent" />
        <UsersTable v-if="renderPanel === 'users'" :scrollTo="scrollTo" />
        <DeviceManager v-if="renderPanel === 'devices'"/>
      </div>
      <!-- TODO: Devices Management -->
    </div>
  </div>
</template>

<script>
export default {
  name: "AdministrationView",
  data() {
    return {
      renderPanel: "users",
      showView: false,
      scrollTo: null,
    };
  },
  methods: {
    closeEvent(scrollTo=null){
      this.renderPanel = "users";
      if(scrollTo != null) this.scrollTo = scrollTo;
    }
  },
  created() {
    this.$store.state.goto = '/'
    this.$store.state.currentView = "Administracja"
    setTimeout(() => { this.showView = true; }, this.$store.state.animationSpeed);
  },
  components: {
    UserRegisterForm: require("@/components/basic_components/UserRegisterForm.vue").default,
    UsersTable:       require("@/components/basic_components/UsersTable.vue").default,
    DeviceManager:    require("@/components/basic_components/DeviceManager.vue").default,
  },
};
</script>

<style lang="scss" scoped>
.administration-wrapper {
  .administrationMenu {
    button {
      margin: 2px;
    }
  }

  .selfScrollBox{
    max-width: 500px;
    margin: auto;
    height: 75vh;
    overflow-y: auto;
  }
}
</style>