<template>
  <div
    class="widgetEditorWrapper"
    :class="[showView ? 'showView' : 'hideView']"
  >
    <div class="searchPanel">
      <div class="header">
        <FA-Icon class="exit" icon="xmark" v-on:click="closeEvent('editWidget')" />
      </div>

      <CreateTwoStateSwitch v-if="componentToAdd.type=='two_state_switch'" :compDict="componentToAdd" :closeEvent="closeEvent" />
      <CreateDisplayInfo v-if="componentToAdd.type=='display_info'" :compDict="componentToAdd" :closeEvent="closeEvent" />
    </div>
  </div>
</template>

<script>
export default {
  name: "WidgetEditor",
  props: { closeEvent: { required: true }, 
           componentToAdd: { required: true } },
  data() {
    return {
      showView: false,
    };
  },
  methods: {},
  created() {
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
  },
  components: {
    CreateTwoStateSwitch: require("@/components/pilot_components/CreateTwoStateSwitch.vue").default,
    CreateDisplayInfo: require("@/components/pilot_components/CreateDisplayInfo.vue").default,
  },
};
</script>

<style lang="scss" scoped>
.widgetEditorWrapper {
  position: fixed;
  top: 0;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  z-index: 80;

  .searchPanel {
    width: 90%;
    max-width: 600px;
    height: 90vh;
    margin: 5vh auto;
    background-color: #fff;
    box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);

    .header {
      width: 100%;
      text-align: right;

      .exit {
        width: 50px;
        padding-top: 15px;
        font-size: 1.5em;
        transition: 0.2s;
      }
      .exit:hover {
        color: rgb(224, 93, 93);
        cursor: pointer;
      }
    }
  }
  
  @media only screen and (max-width: 600px) {
    .searchPanel {
      width: 100%;
      height: 100%;
      margin: 0;
    }
  }
}

</style>