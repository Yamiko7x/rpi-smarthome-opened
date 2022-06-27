<template>
  <div class="backHomeWrapper" v-if="this.$store.state.user">
    <div class="btn-quickAccess" @click="this.$router.push('/'); this.$store.state.quickPanel=false;">
      <FA-Icon icon="house" class="faicon"/>
    </div>
  </div>
</template>

<script>
export default {
  name: "BackHomeButton",
  methods: {
  },
};
</script>

<style lang="scss" scoped>
$backHomeBtn-size: 40px;

.backHomeWrapper {
  position: fixed;
  bottom: calc(85% - 140px);
  right: 0;
  z-index: 100;
}
@media only screen and (max-width: 600px) {
  .backHomeWrapper {
  bottom: calc(50% - 140px);
  }
}
</style>