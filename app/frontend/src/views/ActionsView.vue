<template>
  <div class="actionsWrapper" :class="[showView ? 'showView' : 'hideView']">
    <ActionsTable :fnEditAction="fnEditAction"/>
  </div>
</template>

<script>
export default {
  name: "ActionsView",
  data() {
    return {
      showView: false,
    };
  },
  watch: {},
  methods: {
    fnEditAction(action_id){
      this.$router.push('/actioneditor/'+action_id)
    },
  },
  created() {
    this.$store.state.goto = '/'
    this.$store.state.currentView = "Menadżer Akcji";
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
  },
  components: {
    ActionsTable: require("@/components/actions_components/ActionsTable.vue").default,
  },
};
</script>

<style lang="scss" scoped>
.actionsWrapper {
}
@media only screen and (max-width: 600px) {
}
</style>