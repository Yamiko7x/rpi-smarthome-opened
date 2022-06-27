<template>
  <div class="quickSwitchPilotActionWrapper" v-if="this.$store.state.user">
    <div v-if="this.$route.name=='pilot'" class="btn-quickAccess" @click='this.$router.push("/actions"); this.$store.state.quickPanel = false;'>
      <FA-Icon icon="align-left" class="faicon"/>
    </div>
    <div v-if="this.check_action_route()" class="btn-quickAccess" @click='this.$router.push("/pilot");  this.$store.state.quickPanel = false;'>
      <FA-Icon icon="grip-vertical" class="faicon"/>
    </div>
  </div>
</template>

<script>
export default {
  name: "QuickSwitchPilotAction",
  methods: {
    check_action_route(){
      if(this.$route.name && this.$route.name.length >= 6){
        if(this.$route.name.substring(0,6)=='action'){
          return true
        }
      }
      return false
    },
    returnToHome() {
      this.$router.push("/");
    },
  },
};
</script>

<style lang="scss" scoped>
.quickSwitchPilotActionWrapper {
  position: fixed;
  bottom: 85%;
  right: 0;
  z-index: 100;
}
@media only screen and (max-width: 600px) {
  .quickSwitchPilotActionWrapper {
    bottom: 50%;
  }
}
</style>