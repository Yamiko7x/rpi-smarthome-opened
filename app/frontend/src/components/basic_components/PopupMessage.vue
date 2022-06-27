<template>
  <div
    v-if="active"
    class="popupMessage"
    :class="{ info: this.type == 'info', 
              danger: this.type == 'danger', 
              warning: this.type == 'warning',
              faild: this.type == 'faild',
              success: this.type == 'success' }"
  >
    <p>{{ msg }}</p>
    <FA-Icon class="exit" icon="xmark" v-on:click="deactiveMsg" />
  </div>
</template>

<script>
export default {
  name: "PopupMessages",
  props: {
    id: { required: true },
    msg: { required: true },
    type: { required: false, default: "info" },
    active: { required: true },
  },
  data() {
    return {};
  },
  methods: {
    deactiveMsg() {
      this.$store.state.popupMessages[this.id]["active"] = false;
    },
  },
  watch: {},
  created() {},
};
</script>

<style lang="scss">
$color-pastel-blue: rgb(94, 190, 253);
$color-pastel-red: rgb(253, 99, 94);
$color-pastel-yellow: rgb(243, 211, 71);
$color-pastel-green: rgb(143, 226, 143);

.popupMessage {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  width: 100%;
  max-width: 500px;
  margin: 10px auto 0 auto;
  z-index: 100;
  box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);

  p {
    width: calc(100% - 80px);
    margin-left: 40px;
  }

  .exit {
    width: 20px;
    padding: 10px;
    font-size: 1.3em;
    color: rgb(71, 71, 71);
    text-align: right;
  }
  .exit:hover {
    cursor: pointer;
  }
}

.info {
  border-left: 5px solid $color-pastel-blue;
}
.danger, .faild {
  border-left: 5px solid $color-pastel-red;
}
.warning{
  border-left: 5px solid $color-pastel-yellow;
}
.success{
  border-left: 5px solid $color-pastel-green;
}
</style>