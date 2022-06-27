<template>
  <div class="popupBox">
    <PopupMessage
      v-for="msgDict in this.$store.state.popupMessages"
      :key="msgDict.id"
      :msg="msgDict.msg"
      :type="msgDict.type"
      :id="msgDict.id"
      :active="msgDict.active"
    />
  </div>
</template>

<script>
export default {
  name: "PopupMessages",
  data() {
    return {
      popupMessage: "Some message",
    };
  },
  methods: {},
  watch: {},
  created() {},
  components: {
    PopupMessage: require("@/components/basic_components/PopupMessage.vue").default,
  },
};
</script>

<style lang="scss">
.popupBox {
  position: fixed;
  top: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  z-index: 150;
}
</style>